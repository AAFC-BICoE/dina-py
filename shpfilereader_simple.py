"""
Show comprehensive information for first polygon feature
"""

from dinapy.entities.Site import SiteAttributesDTOBuilder, SiteDTOBuilder
import geopandas as gpd
import json
from shapely.geometry import mapping
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os
from dinapy.site_uploader.site_uploader import SiteUploader
from dinapy.schemas.site_schema import SiteSchema
from dinapy.apis.collectionapi.siteapi import SiteApi

def parse_shapefile(shapefile_path):
    """
    Show all information for the first polygon feature without printing all points
    """

    try:
        # Read the shapefile
        gdf_original = gpd.read_file(shapefile_path)

        gdf = gdf_original.copy()
        gdf["geometry"] = gdf_original.geometry.simplify(
            tolerance=0.1
        )

        # Check CRS
        if gdf.crs:
            if gdf.crs.to_string() == "EPSG:4326":
                print("✅ CRS is already EPSG:4326 (WGS84) - ready for DINA")
            else:
                gdf = gdf.to_crs(epsg=4326)
                print(f"⚠️  CRS is {gdf.crs} - converted to EPSG:4326")
        else:
            print("⚠️  No CRS defined - assume EPSG:4326 or define before upload")

        return gdf

    except Exception as e:
        print(f"\n✗ Error parsing shapefile: {e}")
        import traceback

        traceback.print_exc()
        return None


def prepare_site(row):

    coords_list = list(row.geometry.exterior.coords)
    print(f"number of points: {len(coords_list)}")
    site_name = "NAFO-" + str(row.Label)
    site_geom = {
        "type": "Polygon",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "coordinates": [coords_list]
    }



    # Build the Site attributes using the builder pattern
    site_attributes = (
        SiteAttributesDTOBuilder()
        .group("aafc")
        .name(site_name)
        .code(site_name)
        .siteGeom(site_geom)
        .build()
    )

    # Build the Site DTO
    site_dto = SiteDTOBuilder().attributes(site_attributes).build()

    return site_dto


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Show comprehensive information for first polygon in shapefile"
    )
    parser.add_argument("shapefile", help="Path to shapefile (.shp)")
    parser.add_argument(
        "-upload",
        action="store_true",
        help="Upload the polygons to DINA",
    )

    args = parser.parse_args()

    try:
        result = parse_shapefile(args.shapefile)

        

        if result is not None:
            # Upload to DINA
            siteapi = SiteApi()

            site_schema = SiteSchema()

            result = result.iloc[:10]
            for row in result.itertuples(index=False):
                site_dto = prepare_site(row)
                json_data = site_schema.dump(site_dto)
                if args.upload:
                    siteapi.create_entity(json_data)


    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
