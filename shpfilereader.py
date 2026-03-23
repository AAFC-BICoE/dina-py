"""
Show comprehensive information for first polygon feature
"""

from dinapy.entities.Site import SiteAttributesDTOBuilder, SiteDTOBuilder
import geopandas as gpd
import json
from shapely.geometry import mapping
import json
import matplotlib.pyplot as plt
import os
from dinapy.schemas.site_schema import SiteSchema
from dinapy.apis.collectionapi.siteapi import SiteApi

def simplify_shapefile(
    input_path,
    output_path=None,
    tolerance=0.001,
    preserve_topology=True,
    show_comparison=True,
):
    """
    Simplify polygons in a shapefile

    Args:
        input_path: Path to input shapefile
        output_path: Path to save simplified shapefile (optional)
        tolerance: Simplification tolerance (larger = more simplified)
                  For EPSG:4326, this is in degrees
                  Typical values: 0.0001 (minimal) to 0.01 (aggressive)
        preserve_topology: If True, ensures topology is preserved (recommended)
        show_comparison: If True, display before/after comparison

    Returns:
        Simplified GeoDataFrame
    """
    print("\n" + "=" * 70)
    print("POLYGON SIMPLIFICATION")
    print("=" * 70)

    # Read the shapefile
    print(f"\nReading: {input_path}")
    gdf_original = gpd.read_file(input_path)

    print(f"Original features: {len(gdf_original)}")
    print(f"Original CRS: {gdf_original.crs}")

    # Calculate original statistics
    original_points = count_total_points(gdf_original)
    original_size = calculate_geometry_size(gdf_original)

    print(f"\n📊 ORIGINAL STATISTICS")
    print("-" * 70)
    print(f"Total coordinate points: {original_points:,}")
    print(f"Average points per feature: {original_points / len(gdf_original):.1f}")
    print(f"Geometry data size: {original_size / 1024:.2f} KB")

    # Simplify
    print(f"\n🔄 SIMPLIFYING with tolerance={tolerance}...")
    print(f"Preserve topology: {preserve_topology}")

    gdf_simplified = gdf_original.copy()
    gdf_simplified["geometry"] = gdf_original.geometry.simplify(
        tolerance=tolerance, preserve_topology=preserve_topology
    )

    # Calculate simplified statistics
    simplified_points = count_total_points(gdf_simplified)
    simplified_size = calculate_geometry_size(gdf_simplified)

    # Calculate reductions
    point_reduction = original_points - simplified_points
    point_reduction_pct = (point_reduction / original_points) * 100
    size_reduction = original_size - simplified_size
    size_reduction_pct = (size_reduction / original_size) * 100

    print(f"\n✅ SIMPLIFIED STATISTICS")
    print("-" * 70)
    print(f"Total coordinate points: {simplified_points:,}")
    print(f"Average points per feature: {simplified_points / len(gdf_simplified):.1f}")
    print(f"Geometry data size: {simplified_size / 1024:.2f} KB")

    print(f"\n📉 REDUCTION")
    print("-" * 70)
    print(f"Points removed: {point_reduction:,} ({point_reduction_pct:.1f}%)")
    print(f"Size reduced: {size_reduction / 1024:.2f} KB ({size_reduction_pct:.1f}%)")

    # Calculate area differences
    print(f"\n📏 AREA COMPARISON")
    print("-" * 70)

    if any(gdf_original.geometry.geom_type.isin(["Polygon", "MultiPolygon"])):
        original_area = gdf_original.geometry.area.sum()
        simplified_area = gdf_simplified.geometry.area.sum()
        area_diff = abs(original_area - simplified_area)
        area_diff_pct = (area_diff / original_area) * 100

        print(f"Original total area: {original_area:.6f}")
        print(f"Simplified total area: {simplified_area:.6f}")
        print(f"Area difference: {area_diff:.6f} ({area_diff_pct:.3f}%)")

    # Show per-feature comparison
    print(f"\n📋 PER-FEATURE COMPARISON (First 5 features)")
    print("-" * 70)

    for i in range(min(5, len(gdf_original))):
        original_geom = gdf_original.iloc[i].geometry
        simplified_geom = gdf_simplified.iloc[i].geometry

        orig_points = count_geometry_points(original_geom)
        simp_points = count_geometry_points(simplified_geom)
        reduction = orig_points - simp_points
        reduction_pct = (reduction / orig_points) * 100

        # Get feature identifier if available
        feature_id = "Unknown"
        for col in ["ZONE", "NAFO_DIV", "NAME", "ID", "FID"]:
            if col in gdf_original.columns:
                feature_id = gdf_original.iloc[i][col]
                break

        print(f"\nFeature {i} ({feature_id}):")
        print(f"  Original points:   {orig_points:,}")
        print(f"  Simplified points: {simp_points:,}")
        print(f"  Reduction:         {reduction:,} ({reduction_pct:.1f}%)")

        if original_geom.geom_type in ["Polygon", "MultiPolygon"]:
            orig_area = original_geom.area
            simp_area = simplified_geom.area
            area_change = abs(orig_area - simp_area) / orig_area * 100
            print(f"  Area change:       {area_change:.3f}%")

    # Validate simplified geometries
    print(f"\n✓ VALIDATION")
    print("-" * 70)
    invalid_count = (~gdf_simplified.geometry.is_valid).sum()
    if invalid_count > 0:
        print(f"⚠️  Warning: {invalid_count} invalid geometries after simplification")
        print(f"   Consider using preserve_topology=True or lower tolerance")
    else:
        print(f"✅ All geometries are valid after simplification")

    # Save if output path provided
    if output_path:
        print(f"\n💾 SAVING")
        print("-" * 70)
        gdf_simplified.to_file(output_path)
        print(f"✓ Saved to: {output_path}")

        # Calculate file size difference
        if os.path.exists(input_path) and os.path.exists(output_path):
            orig_file_size = os.path.getsize(input_path)
            simp_file_size = os.path.getsize(output_path)
            file_reduction = orig_file_size - simp_file_size
            file_reduction_pct = (file_reduction / orig_file_size) * 100

            print(f"\nFile size comparison:")
            print(f"  Original: {orig_file_size / 1024:.2f} KB")
            print(f"  Simplified: {simp_file_size / 1024:.2f} KB")
            print(
                f"  Reduction: {file_reduction / 1024:.2f} KB ({file_reduction_pct:.1f}%)"
            )

    # Show visual comparison
    if show_comparison:
        print(f"\n🎨 Generating visual comparison...")
        create_simplification_comparison(gdf_original, gdf_simplified, tolerance)

    print("\n" + "=" * 70)
    print("✓ Simplification complete!")
    print("=" * 70)

    return gdf_simplified


def count_geometry_points(geom):
    """Count total coordinate points in a geometry"""
    if geom.geom_type == "Polygon":
        return len(list(geom.exterior.coords))
    elif geom.geom_type == "MultiPolygon":
        return sum(len(list(p.exterior.coords)) for p in geom.geoms)
    elif geom.geom_type == "LineString":
        return len(list(geom.coords))
    elif geom.geom_type == "Point":
        return 1
    else:
        return 0


def count_total_points(gdf):
    """Count total coordinate points in all geometries"""
    return sum(count_geometry_points(geom) for geom in gdf.geometry)


def calculate_geometry_size(gdf):
    """Estimate size of geometry data in bytes"""
    # Convert to GeoJSON and measure
    total_size = 0
    for geom in gdf.geometry:
        geojson = mapping(geom)
        json_str = json.dumps(geojson)
        total_size += len(json_str.encode("utf-8"))
    return total_size


def create_simplification_comparison(gdf_original, gdf_simplified, tolerance):
    """Create visual comparison of original vs simplified"""

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # Plot 1: Original
    gdf_original.plot(ax=axes[0], color="lightblue", edgecolor="blue", linewidth=0.8)
    axes[0].set_title(
        f"Original\n({count_total_points(gdf_original):,} points)",
        fontsize=14,
        fontweight="bold",
    )
    axes[0].set_xlabel("Longitude")
    axes[0].set_ylabel("Latitude")
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Simplified
    gdf_simplified.plot(ax=axes[1], color="lightcoral", edgecolor="red", linewidth=0.8)
    axes[1].set_title(
        f"Simplified (tolerance={tolerance})\n({count_total_points(gdf_simplified):,} points)",
        fontsize=14,
        fontweight="bold",
    )
    axes[1].set_xlabel("Longitude")
    axes[1].set_ylabel("Latitude")
    axes[1].grid(True, alpha=0.3)

    # Plot 3: Overlay
    gdf_original.plot(
        ax=axes[2],
        color="lightblue",
        edgecolor="blue",
        linewidth=1.5,
        alpha=0.5,
        label="Original",
    )
    gdf_simplified.plot(
        ax=axes[2],
        color="lightcoral",
        edgecolor="red",
        linewidth=1,
        alpha=0.7,
        label="Simplified",
    )
    axes[2].set_title("Overlay Comparison", fontsize=14, fontweight="bold")
    axes[2].set_xlabel("Longitude")
    axes[2].set_ylabel("Latitude")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    plt.tight_layout()

    # Save the plot
    output_file = f"simplification_comparison_tol{tolerance}.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"  ✓ Comparison plot saved as: {output_file}")



def compare_tolerances(shapefile_path, tolerances=[0.0001, 0.001, 0.01, 0.1]):
    """
    Compare different tolerance levels

    Args:
        shapefile_path: Path to input shapefile
        tolerances: List of tolerance values to test
    """
    print("\n" + "=" * 70)
    print("TOLERANCE COMPARISON")
    print("=" * 70)

    gdf_original = gpd.read_file(shapefile_path)
    original_points = count_total_points(gdf_original)

    print(f"\nOriginal: {original_points:,} points")
    print("\nTesting tolerances:")
    print("-" * 70)

    results = []

    for tol in tolerances:
        gdf_simplified = gdf_original.copy()
        gdf_simplified["geometry"] = gdf_original.geometry.simplify(
            tolerance=tol, preserve_topology=True
        )

        simplified_points = count_total_points(gdf_simplified)
        reduction_pct = ((original_points - simplified_points) / original_points) * 100

        # Check validity
        invalid_count = (~gdf_simplified.geometry.is_valid).sum()

        # Calculate area change
        if any(gdf_original.geometry.geom_type.isin(["Polygon", "MultiPolygon"])):
            original_area = gdf_original.geometry.area.sum()
            simplified_area = gdf_simplified.geometry.area.sum()
            area_change_pct = abs(original_area - simplified_area) / original_area * 100
        else:
            area_change_pct = 0

        results.append(
            {
                "tolerance": tol,
                "points": simplified_points,
                "reduction_pct": reduction_pct,
                "area_change_pct": area_change_pct,
                "invalid": invalid_count,
            }
        )

        status = "✓" if invalid_count == 0 else "⚠️"
        print(
            f"{status} Tolerance {tol:8.4f}: {simplified_points:8,} points "
            f"({reduction_pct:5.1f}% reduction, {area_change_pct:5.3f}% area change)"
        )

    # Recommend best tolerance
    print("\n💡 RECOMMENDATIONS")
    print("-" * 70)

    # Find tolerances with valid geometries
    valid_results = [r for r in results if r["invalid"] == 0]

    if valid_results:
        # Conservative: minimal area change
        conservative = min(valid_results, key=lambda x: x["area_change_pct"])
        print(f"\n✅ Conservative (minimal area change):")
        print(f"   Tolerance: {conservative['tolerance']}")
        print(
            f"   Points: {conservative['points']:,} ({conservative['reduction_pct']:.1f}% reduction)"
        )
        print(f"   Area change: {conservative['area_change_pct']:.3f}%")

        # Balanced: 30-50% reduction
        balanced = [r for r in valid_results if 30 <= r["reduction_pct"] <= 50]
        if balanced:
            best_balanced = min(balanced, key=lambda x: x["area_change_pct"])
            print(f"\n✅ Balanced (30-50% reduction):")
            print(f"   Tolerance: {best_balanced['tolerance']}")
            print(
                f"   Points: {best_balanced['points']:,} ({best_balanced['reduction_pct']:.1f}% reduction)"
            )
            print(f"   Area change: {best_balanced['area_change_pct']:.3f}%")

        # Aggressive: maximum reduction with <1% area change
        aggressive = [r for r in valid_results if r["area_change_pct"] < 1.0]
        if aggressive:
            best_aggressive = max(aggressive, key=lambda x: x["reduction_pct"])
            print(f"\n✅ Aggressive (maximum reduction, <1% area change):")
            print(f"   Tolerance: {best_aggressive['tolerance']}")
            print(
                f"   Points: {best_aggressive['points']:,} ({best_aggressive['reduction_pct']:.1f}% reduction)"
            )
            print(f"   Area change: {best_aggressive['area_change_pct']:.3f}%")

    return results


def simplify_first_feature(shapefile_path, tolerance=0.001):
    """
    Simplify just the first feature and show detailed comparison
    """
    print("\n" + "=" * 70)
    print("FIRST FEATURE SIMPLIFICATION DETAIL")
    print("=" * 70)

    gdf = gpd.read_file(shapefile_path)
    original_geom = gdf.iloc[0].geometry

    print(f"\nOriginal geometry:")
    print(f"  Type: {original_geom.geom_type}")
    print(f"  Points: {count_geometry_points(original_geom):,}")
    print(f"  Area: {original_geom.area:.6f}")
    print(f"  Bounds: {original_geom.bounds}")

    # Simplify
    simplified_geom = original_geom.simplify(
        tolerance=tolerance, preserve_topology=True
    )

    print(f"\nSimplified geometry (tolerance={tolerance}):")
    print(f"  Type: {simplified_geom.geom_type}")
    print(f"  Points: {count_geometry_points(simplified_geom):,}")
    print(f"  Area: {simplified_geom.area:.6f}")
    print(f"  Bounds: {simplified_geom.bounds}")

    # Calculate differences
    point_reduction = count_geometry_points(original_geom) - count_geometry_points(
        simplified_geom
    )
    point_reduction_pct = (point_reduction / count_geometry_points(original_geom)) * 100
    area_diff = abs(original_geom.area - simplified_geom.area)
    area_diff_pct = (area_diff / original_geom.area) * 100

    print(f"\nChanges:")
    print(f"  Points removed: {point_reduction:,} ({point_reduction_pct:.1f}%)")
    print(f"  Area change: {area_diff:.6f} ({area_diff_pct:.3f}%)")
    print(f"  Is valid: {simplified_geom.is_valid}")

    # Show coordinate comparison
    if original_geom.geom_type == "Polygon":
        orig_coords = list(original_geom.exterior.coords)
        simp_coords = list(simplified_geom.exterior.coords)

        print(f"\nFirst 5 original coordinates:")
        for i, (lon, lat) in enumerate(orig_coords[:5]):
            print(f"  {i+1}. ({lon:.6f}, {lat:.6f})")

        print(f"\nFirst 5 simplified coordinates:")
        for i, (lon, lat) in enumerate(simp_coords[:5]):
            print(f"  {i+1}. ({lon:.6f}, {lat:.6f})")

    return original_geom, simplified_geom


def analyze_first_polygon(shapefile_path):
    """
    Show all information for the first polygon feature without printing all points
    """
    print("\n" + "=" * 70)
    print("COMPREHENSIVE ANALYSIS OF FIRST POLYGON FEATURE")
    print("=" * 70)

    try:
        # Read the shapefile
        gdf = simplify_shapefile(shapefile_path, tolerance=0.1)

        if len(gdf) == 0:
            print("Error: Shapefile is empty")
            return None

        # Get first feature
        first_feature = gdf.iloc[0]
        geom = first_feature.geometry

        # 1. FILE INFORMATION
        print("\n📁 1. FILE INFORMATION")
        print("-" * 70)
        print(f"Shapefile path:      {shapefile_path}")
        print(f"Total features:      {len(gdf)}")
        print(f"CRS:                 {gdf.crs}")
        print(f"EPSG Code:           {gdf.crs.to_epsg() if gdf.crs else 'Not defined'}")

        # 2. ATTRIBUTE DATA
        print("\n📋 2. ATTRIBUTE DATA (All non-geometry columns)")
        print("-" * 70)
        max_col_width = max(len(col) for col in gdf.columns if col != "geometry")

        for col in gdf.columns:
            if col != "geometry":
                value = first_feature[col]
                # Format value based on type
                if isinstance(value, float):
                    formatted_value = f"{value:.6f}"
                elif value is None or (isinstance(value, float) and pd.isna(value)):
                    formatted_value = "NULL"
                else:
                    formatted_value = str(value)

                print(f"{col:<{max_col_width + 2}} : {formatted_value}")

        # 3. GEOMETRY TYPE AND BASIC INFO
        print("\n🗺️  3. GEOMETRY INFORMATION")
        print("-" * 70)
        print(f"Geometry type:       {geom.geom_type}")
        print(f"Is valid:            {geom.is_valid}")
        print(f"Is simple:           {geom.is_simple}")
        print(f"Is empty:            {geom.is_empty}")

        # 4. SPATIAL MEASUREMENTS
        print("\n📏 4. SPATIAL MEASUREMENTS")
        print("-" * 70)

        if geom.geom_type in ["Polygon", "MultiPolygon"]:
            print(f"Area:                {geom.area:.6f} square units")
            print(f"Perimeter:           {geom.length:.6f} units")

            # Calculate area in different units if CRS is known
            if gdf.crs and gdf.crs.is_geographic:
                # For geographic coordinates, give approximation
                print(f"\n  Note: For geographic coordinates (lat/lon):")
                print(f"  • Area is in square degrees")
                print(f"  • For accurate measurements, reproject to projected CRS")

        elif geom.geom_type == "LineString":
            print(f"Length:              {geom.length:.6f} units")

        # 5. BOUNDING BOX
        print("\n📦 5. BOUNDING BOX")
        print("-" * 70)
        bounds = geom.bounds
        print(f"West  (Min X):       {bounds[0]:.6f}")
        print(f"South (Min Y):       {bounds[1]:.6f}")
        print(f"East  (Max X):       {bounds[2]:.6f}")
        print(f"North (Max Y):       {bounds[3]:.6f}")
        print(f"Width:               {bounds[2] - bounds[0]:.6f}")
        print(f"Height:              {bounds[3] - bounds[1]:.6f}")

        # Calculate center point
        centroid = geom.centroid
        print(f"\nCentroid:")
        print(f"  X (Longitude):     {centroid.x:.6f}")
        print(f"  Y (Latitude):      {centroid.y:.6f}")

        # 6. COORDINATE INFORMATION (Summary only)
        print("\n📍 6. COORDINATE INFORMATION (Summary)")
        print("-" * 70)

        if geom.geom_type == "Polygon":
            exterior_coords = list(geom.exterior.coords)
            print(f"Exterior ring:")
            print(f"  Number of points:  {len(exterior_coords)}")
            print(
                f"  First point:       ({exterior_coords[0][0]:.6f}, {exterior_coords[0][1]:.6f})"
            )
            print(
                f"  Last point:        ({exterior_coords[-1][0]:.6f}, {exterior_coords[-1][1]:.6f})"
            )
            print(f"  Is closed:         {exterior_coords[0] == exterior_coords[-1]}")

            # Interior rings (holes)
            num_holes = len(geom.interiors)
            print(f"\nInterior rings (holes): {num_holes}")
            if num_holes > 0:
                for i, interior in enumerate(geom.interiors):
                    interior_coords = list(interior.coords)
                    print(f"  Hole {i+1}:")
                    print(f"    Number of points: {len(interior_coords)}")

            # Show first few and last few coordinates
            print(f"\nFirst 3 coordinates:")
            for i, coord in enumerate(exterior_coords[:3]):
                print(f"  {i+1:3d}. ({coord[0]:10.6f}, {coord[1]:9.6f})")

            if len(exterior_coords) > 6:
                print(f"  ... ({len(exterior_coords) - 6} coordinates omitted) ...")

            print(f"\nLast 3 coordinates:")
            for i, coord in enumerate(
                exterior_coords[-3:], start=len(exterior_coords) - 2
            ):
                print(f"  {i:3d}. ({coord[0]:10.6f}, {coord[1]:9.6f})")

        elif geom.geom_type == "MultiPolygon":
            print(f"Number of polygons:  {len(geom.geoms)}")
            total_points = 0

            for i, poly in enumerate(geom.geoms):
                exterior_coords = list(poly.exterior.coords)
                total_points += len(exterior_coords)
                print(f"\nPolygon {i+1}:")
                print(f"  Exterior points:   {len(exterior_coords)}")
                print(f"  Interior rings:    {len(poly.interiors)}")
                print(f"  Area:              {poly.area:.6f}")
                print(
                    f"  First point:       ({exterior_coords[0][0]:.6f}, {exterior_coords[0][1]:.6f})"
                )

            print(f"\nTotal coordinate points: {total_points}")

        elif geom.geom_type == "Point":
            print(f"Coordinates:         ({geom.x:.6f}, {geom.y:.6f})")

        elif geom.geom_type == "LineString":
            coords = list(geom.coords)
            print(f"Number of points:    {len(coords)}")
            print(f"First point:         ({coords[0][0]:.6f}, {coords[0][1]:.6f})")
            print(f"Last point:          ({coords[-1][0]:.6f}, {coords[-1][1]:.6f})")

        # 7. COORDINATE EXTREMES
        print("\n🎯 7. COORDINATE EXTREMES")
        print("-" * 70)

        if geom.geom_type in [
            "Polygon",
            "MultiPolygon",
            "LineString",
            "MultiLineString",
        ]:
            # Get all coordinates
            if geom.geom_type == "Polygon":
                all_coords = list(geom.exterior.coords)
            elif geom.geom_type == "MultiPolygon":
                all_coords = []
                for poly in geom.geoms:
                    all_coords.extend(list(poly.exterior.coords))
            elif geom.geom_type == "LineString":
                all_coords = list(geom.coords)

            if all_coords:
                lons = [c[0] for c in all_coords]
                lats = [c[1] for c in all_coords]

                westmost = min(lons)
                eastmost = max(lons)
                southmost = min(lats)
                northmost = max(lats)

                print(f"Westmost point:      {westmost:.6f}")
                print(f"Eastmost point:      {eastmost:.6f}")
                print(f"Southmost point:     {southmost:.6f}")
                print(f"Northmost point:     {northmost:.6f}")

        # 8. GEOJSON REPRESENTATION (Structure only)
        print("\n🌐 8. GEOJSON STRUCTURE")
        print("-" * 70)

        geojson_geom = mapping(geom)

        print(f"Type:                {geojson_geom['type']}")

        if geojson_geom["type"] == "Polygon":
            print(f"Coordinate arrays:   {len(geojson_geom['coordinates'])}")
            print(f"  Exterior ring:     {len(geojson_geom['coordinates'][0])} points")
            if len(geojson_geom["coordinates"]) > 1:
                for i in range(1, len(geojson_geom["coordinates"])):
                    print(
                        f"  Interior ring {i}:   {len(geojson_geom['coordinates'][i])} points"
                    )

        elif geojson_geom["type"] == "MultiPolygon":
            print(f"Number of polygons:  {len(geojson_geom['coordinates'])}")
            for i, poly_coords in enumerate(geojson_geom["coordinates"]):
                print(f"  Polygon {i+1}:       {len(poly_coords[0])} exterior points")

        # Show truncated GeoJSON
        geojson_str = json.dumps(geojson_geom, indent=2)
        if len(geojson_str) > 500:
            print("\nGeoJSON (truncated):")
            print(geojson_str[:500] + "\n    ... (truncated) ...\n  }")
        else:
            print("\nFull GeoJSON:")
            print(geojson_str)

        # 9. DINA SITE FORMAT
        print("\n🎯 9. READY FOR DINA SITE CREATION")
        print("-" * 70)

        dina_geom = {
            "type": geojson_geom["type"],
            "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
            "coordinates": geojson_geom["coordinates"],
        }

        print("DINA-compatible geometry structure:")
        print(f"  Type:              {dina_geom['type']}")
        print(f"  CRS:               EPSG:4326 (WGS84)")

        # Calculate coordinate array size
        coord_str = json.dumps(dina_geom["coordinates"])
        print(f"  Coordinates size:  {len(coord_str)} characters")

        if geom.geom_type == "Polygon":
            print(f"  Exterior points:   {len(dina_geom['coordinates'][0])}")
        elif geom.geom_type == "MultiPolygon":
            total = sum(len(poly[0]) for poly in dina_geom["coordinates"])
            print(f"  Total points:      {total}")

        # 10. STATISTICS SUMMARY
        print("\n📊 10. SUMMARY STATISTICS")
        print("-" * 70)

        stats = {
            "Geometry Type": geom.geom_type,
            "Is Valid": geom.is_valid,
            "Total Coordinate Points": None,
            "Area (if polygon)": (
                geom.area if geom.geom_type in ["Polygon", "MultiPolygon"] else "N/A"
            ),
            "Perimeter/Length": geom.length,
            "Bounding Box Width": bounds[2] - bounds[0],
            "Bounding Box Height": bounds[3] - bounds[1],
            "Has Holes": (
                len(geom.interiors) > 0 if geom.geom_type == "Polygon" else "N/A"
            ),
        }

        # Count total points
        if geom.geom_type == "Polygon":
            stats["Total Coordinate Points"] = len(list(geom.exterior.coords))
        elif geom.geom_type == "MultiPolygon":
            stats["Total Coordinate Points"] = sum(
                len(list(p.exterior.coords)) for p in geom.geoms
            )
        elif geom.geom_type == "LineString":
            stats["Total Coordinate Points"] = len(list(geom.coords))

        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key:<30} {value:.6f}")
            else:
                print(f"{key:<30} {value}")

        # 11. RECOMMENDATIONS
        print("\n💡 11. RECOMMENDATIONS FOR DINA UPLOAD")
        print("-" * 70)

        # Check CRS
        if gdf.crs:
            if gdf.crs.to_string() == "EPSG:4326":
                print("✅ CRS is already EPSG:4326 (WGS84) - ready for DINA")
            else:
                gdf = gdf.to_crs(epsg=4326)
                print(f"⚠️  CRS is {gdf.crs} - converted to EPSG:4326")
        else:
            print("⚠️  No CRS defined - assume EPSG:4326 or define before upload")

        # Check validity
        if not geom.is_valid:
            print("⚠️  Geometry is not valid - may need repair before upload")
        else:
            print("✅ Geometry is valid")

        # Check size
        if (
            stats["Total Coordinate Points"]
            and stats["Total Coordinate Points"] > 10000
        ):
            print(
                f"⚠️  Large number of points ({stats['Total Coordinate Points']}) - consider simplification"
            )
        elif stats["Total Coordinate Points"]:
            print(
                f"✅ Reasonable number of points ({stats['Total Coordinate Points']})"
            )

        # Suggest field mappings
        print("\n📝 Suggested field mappings for DINA:")
        string_cols = [
            col
            for col in gdf.columns
            if col != "geometry" and gdf[col].dtype == "object"
        ]
        if string_cols:
            print(f"  Potential name field:  {string_cols[0]}")
            if len(string_cols) > 1:
                print(f"  Potential code field:  {string_cols[1]}")

        print("\n" + "=" * 70)
        print("✓ Analysis complete!")
        print("=" * 70)

        return first_feature

    except Exception as e:
        print(f"\n✗ Error analyzing shapefile: {e}")
        import traceback

        traceback.print_exc()
        return None


def prepare_site(row):

    site_name = "NAFO-" + str(row.Label)
    site_geom = {
        "type": "Polygon",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "coordinates": [list(row.geometry.exterior.coords)],
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
        "-export_coords",
        action="store_true",
        help="Export all coordinates to a separate file",
    )

    args = parser.parse_args()

    try:
        result = analyze_first_polygon(args.shapefile)

        site_dto = prepare_site(result)

        if result is not None and args.export_coords:
            # Export coordinates to file
            geom = result.geometry
            output_file = "first_polygon_coordinates.txt"

            siteapi = SiteApi()

            site_schema = SiteSchema()
            json_data = site_schema.dump(site_dto)

            siteapi.create_entity(json_data)

            with open(output_file, "w") as f:
                f.write("ALL COORDINATES FOR FIRST POLYGON\n")
                f.write("=" * 70 + "\n\n")

                if geom.geom_type == "Polygon":
                    coords = list(geom.exterior.coords)
                    f.write(f"Exterior ring ({len(coords)} points):\n")
                    f.write("-" * 70 + "\n")
                    for i, (lon, lat) in enumerate(coords):
                        f.write(f"{i+1:4d}. ({lon:12.8f}, {lat:11.8f})\n")

                    for j, interior in enumerate(geom.interiors):
                        interior_coords = list(interior.coords)
                        f.write(
                            f"\nInterior ring {j+1} ({len(interior_coords)} points):\n"
                        )
                        f.write("-" * 70 + "\n")
                        for i, (lon, lat) in enumerate(interior_coords):
                            f.write(f"{i+1:4d}. ({lon:12.8f}, {lat:11.8f})\n")

                elif geom.geom_type == "MultiPolygon":
                    for poly_idx, polygon in enumerate(geom.geoms):
                        coords = list(polygon.exterior.coords)
                        f.write(
                            f"\nPolygon {poly_idx+1} - Exterior ring ({len(coords)} points):\n"
                        )
                        f.write("-" * 70 + "\n")
                        for i, (lon, lat) in enumerate(coords):
                            f.write(f"{i+1:4d}. ({lon:12.8f}, {lat:11.8f})\n")

            print(f"\n📄 All coordinates exported to: {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
