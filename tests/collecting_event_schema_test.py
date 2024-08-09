# This file contains tests relating to CollectingEventAPI.
# Currently only contains tests for the CollectingEventSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest
import pprint



import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
# Add the root directory of the project to the Python path

# Now you can import modules from the dinaapi package
from dinapy.schemas.collectingeventschema import CollectingEventSchema
from marshmallow.exceptions import ValidationError
from dinapy.entities.CollectingEvent import *

KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"

VALID_COLLECTING_EVENT_DATA = {
	"data": {
		"id": "f08516e5-add2-4baa-89bc-5b8abd0ec8ba",
		"type": "collecting-event",
		"links": {
			"self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba"
		},
		"attributes": {
			"version": 0,
			"dwcFieldNumber": None,
			"dwcRecordNumber": None,
			"otherRecordNumbers": None,
			"group": "phillips-lab",
			"createdBy": "s-seqdbsoil",
			"createdOn": "2024-01-26T17:09:33.932301Z",
			"geoReferenceAssertions": [
				{
					"dwcDecimalLatitude": 44.2,
					"dwcDecimalLongitude": -80.7,
					"dwcCoordinateUncertaintyInMeters": None,
					"createdOn": "2024-01-26T17:09:33.931468083Z",
					"dwcGeoreferencedDate": None,
					"georeferencedBy": None,
					"literalGeoreferencedBy": None,
					"dwcGeoreferenceProtocol": None,
					"dwcGeoreferenceSources": None,
					"dwcGeoreferenceRemarks": None,
					"dwcGeodeticDatum": None,
					"isPrimary": 'true',
					"dwcGeoreferenceVerificationStatus": None
				}
			],
			"eventGeom": {
				"type": "Point",
				"crs": {
					"type": "name",
					"properties": {
						"name": "EPSG:4326"
					}
				},
				"coordinates": [
					-80.7,
					44.2
				]
			},
			"dwcVerbatimCoordinates": "44.2 -80.7",
			"dwcRecordedBy": None,
			"startEventDateTime": "2017-08-07",
			"endEventDateTime": None,
			"verbatimEventDateTime": None,
			"dwcVerbatimLocality": None,
			"host": None,
			"managedAttributes": {
				"site_codes": "BS",
				"cover_crops": "Yes; Annual Ryegrass",
				"seq_db_legacy": "{\"Collection Info\":{\"id\":1053400,\"latitude\":\"44.2\",\"longitude\":\"-80.7\",\"year\":\"2017\",\"month\":\"08\",\"day\":\"07\",\"zeroPaddedDate\":\"2017-008-007\",\"notes\":\"Blocks of soil kept intact and on ice until transport back to lab\",\"elevation\":384.0,\"depth\":\"0-0.15\",\"lastModified\":\"2021-02-18T22:57:53.120+00:00\",\"latLon\":\"44.2 -80.7\",\"siteCodes\":\"BS\",\"protocol\":{\"id\":224,\"type\":\"COLLECTION_EVENT\",\"name\":\"Phillips_OMAFRA_SYU_SampleCollectionProtocol.docx\",\"version\":\"\",\"description\":\"\",\"steps\":\"\",\"notes\":\"\",\"reference\":\"\",\"equipment\":\"\",\"forwardPrimerConcentration\":\"\",\"reversePrimerConcentration\":\"\",\"reactionMixVolume\":\"\",\"reactionMixVolumePerTube\":\"\",\"group\":{\"id\":458,\"groupName\":\"GI_Phillips\",\"description\":\"\",\"defaultRead\":false,\"defaultWrite\":false,\"defaultDelete\":false,\"defaultCreate\":false,\"lastModified\":\"2021-01-15T16:25:33.348+00:00\"},\"reactionComponents\":[{\"reactionComponentId\":1016,\"name\":\"\",\"concentration\":\"\",\"lastModified\":\"2021-02-17T18:29:31.605+00:00\",\"id\":1016}],\"lastModified\":\"2021-02-17T18:29:31.479+00:00\"}},\"MIxS Specifications\":{\"id\":783441,\"envPackage\":\"Soil\",\"dnaStorageConditions\":\"neg 80oC; up to 6 months\",\"sampVolWeDnaExt\":\"0.25g\",\"calcium\":\"2440\",\"magnesium\":\"250\",\"orgMatter\":\"4\",\"ph\":7.4,\"potassium\":\"69\",\"sodium\":\"14\",\"waterContent\":\"0.2281041792852818\",\"curLandUse\":\"farmstead\",\"curVegetation\":\"corn\",\"cropRotation\":\"Yes; Corn-Hay/cereal forage\",\"tillage\":\"Conventional\",\"horizon\":\"A horizon\",\"waterContentSoilMeth\":\"Gravimetric\",\"poolDnaExtracts\":\"Yes; 2 x 0.25g\",\"storeCond\":\"6months/-20oC\",\"linkClimateInfo\":\"https://climate.weather.gc.ca/climate_normals/index_e.html\",\"annualSeasonTemp\":\"6.6\",\"linkClassInfo\":\"https://sis.agr.gc.ca/cansis/soils/on/DYK/~~~~~/A/description.html\",\"faoClass\":\"Orthic Gray Brown Luvisol\",\"texture\":\"sandy loam\",\"coverCrops\":\"Yes; Annual Ryegrass\",\"growingDegreeDays\":\"2004.5\",\"cationExchangeCapacity\":\"14.5\",\"availablePhosphorus\":\"25\",\"aggregateStability\":\"-14.528593500000001\",\"lastModified\":\"2021-02-18T22:57:53.123+00:00\"}}",
				"available_phosp": "25",
				"aggregate_stability": "-14.528593500000001",
				"growing_degree_days": "2004.5",
				"cation_exchange_capacity": "14.5"
			},
			"dwcVerbatimLatitude": "44.2",
			"dwcVerbatimLongitude": "-80.7",
			"dwcVerbatimCoordinateSystem": None,
			"dwcVerbatimSRS": None,
			"dwcVerbatimElevation": None,
			"dwcVerbatimDepth": None,
			"dwcCountry": None,
			"dwcCountryCode": None,
			"dwcStateProvince": None,
			"habitat": None,
			"dwcMinimumElevationInMeters": 384,
			"dwcMinimumDepthInMeters": 0,
			"dwcMaximumElevationInMeters": None,
			"dwcMaximumDepthInMeters": 0.15,
			"substrate": "Soil",
			"remarks": "Blocks of soil kept intact and on ice until transport back to lab",
			"publiclyReleasable": None,
			"notPubliclyReleasableReason": None,
			"tags": None,
			"geographicPlaceNameSource": None,
			"geographicPlaceNameSourceDetail": None,
			"extensionValues": {
				"mixs_soil_v4": {
					"ph": "7.4",
					"horizon": "A horizon",
					"texture": "sandy loam",
					"tillage": "Conventional",
					"fao_class": "Orthic Gray Brown Luvisol",
					"store_cond": "6months/-20oC",
					"env_package": "Soil",
					"cur_land_use": "farmstead",
					"crop_rotation": "Yes; Corn-Hay/cereal forage",
					"water_content": "0.2281041792852818",
					"cur_vegetation": "corn",
					"link_class_info": "https://sis.agr.gc.ca/cansis/soils/on/DYK/~~~~~/A/description.html",
					"link_climate_info": "https://climate.weather.gc.ca/climate_normals/index_e.html",
					"pool_dna_extracts": "Yes; 2 x 0.25g",
					"annual_season_temp": "6.6",
					"samp_vol_we_dna_ext": "0.25g",
					"water_content_soil_meth": "Gravimetric"
				},
				"mixs_soil_v5": {
					"dna_storage_conditons": "neg 80oC; up to 6 months"
				},
				"mixs_sediment_v4": {
					"sodium": "14",
					"calcium": "2440",
					"magnesium": "250",
					"potassium": "69",
					"org_matter": "4"
				}
			}
		},
		"relationships": {
			"collectionMethod": {
				"links": {
					"self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/collectionMethod",
					"related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/collectionMethod"
				}
			},
			"protocol": {
				"links": {
					"self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/protocol",
					"related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/protocol"
				}
			},
			"collectors": {
				"links": {
					"self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/collectors",
					"related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/collectors"
				}
			},
			"attachment": {
				"links": {
					"self": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/relationships/attachment",
					"related": "/api/v1/collecting-event/f08516e5-add2-4baa-89bc-5b8abd0ec8ba/attachment"
				}
			}
		}
	},
	"meta": {
		"totalResourceCount": 1,
		"external": [
			{
				"href": "agent/api/v1/person",
				"type": "person"
			},
			{
				"href": "objectstore/api/v1/metadata",
				"type": "metadata"
			}
		],
		"moduleVersion": "0.84"
	}
}


class CollectingEventSchemaTest(unittest.TestCase):
	def test_deserialize_serialize_collecting_event(self):
		# Create a schema instance and validate the data
		schema = CollectingEventSchema()
		try:
			result = schema.load(VALID_COLLECTING_EVENT_DATA)
			result2 = schema.dump(result)
			pp = pprint.PrettyPrinter(indent=0)
			pp.pprint(result)
			pp.pprint(result2)
			self.assertIsInstance(result, CollectingEventDTO)
		except ValidationError as e:
			self.fail(f"Validation failed with error: {e.messages}")

	def test_serialize_collecting_event(self):
		schema = CollectingEventSchema()
		collecting_event_attributes = CollectingEventAttributesDTOBuilder().group("aafc").build()
		collecting_event = CollectingEventDTOBuilder().attributes(collecting_event_attributes).build()
		try:
			serialized_collecting_event = schema.dump(collecting_event)
			pp = pprint.PrettyPrinter(indent=0)
			pp.pprint(serialized_collecting_event)
			self.assertIsInstance(serialized_collecting_event, dict)
		except ValidationError as e:
			self.fail(f"Validation failed with error: {e.messages}")
if __name__ == "__main__":
	unittest.main()
