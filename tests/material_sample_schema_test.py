# This file contains tests relating to PersonAPI.
# Currently only contains tests for the PersonSchema (serialization and deserialization tests).
# API mock call tests should be added.

import unittest
import pprint

from marshmallow.exceptions import ValidationError

import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now you can import modules from the dinaapi package
from dinapy.schemas.materialsampleschema import MaterialSampleSchema
from dinapy.entities.MaterialSample	import *
from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI


KEYCLOAK_CONFIG_PATH = "tests/keycloak-config.yml"
VALID_MATERIAL_SAMPLE_DATA2 = {
	"data": {
		"id": "182ed68e-7536-4ad4-868c-399c8e5d70f3",
		"type": "material-sample",
		"links": {
			"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3"
		},
		"attributes": {
			"version": 1,
			"group": "phillips-lab",
			"createdOn": "2024-03-07T16:35:26.865646Z",
			"createdBy": "s-seqdbsoil",
			"dwcCatalogNumber": None,
			"dwcOtherCatalogNumbers": [
				"HCC_31"
			],
			"materialSampleName": "HCC-2018-05-16-HCC_31",
			"materialSampleType": "MIXED_ORGANISMS",
			"materialSampleChildren": [],
			"preparationDate": None,
			"preservationType": None,
			"preparationFixative": None,
			"preparationMaterials": None,
			"preparationSubstrate": None,
			"managedAttributes": {
				"treatment": "HCC_31",
				"pretreatment": "Yes; air dried 1 month/No; kept frozen",
				"date_archived": "43175",
				"seq_db_legacy": "{\"Mixed Specimen\":{\"id\":9229,\"mixedSpecimenNumber\":\"HCC-2018-05-16-HCC_31\",\"otherIds\":\"HCC_31\",\"replicateInfo\":\"Randomized Complete Block Design; 4 experimental replicates\",\"substrateType\":\"Soil\",\"notes\":\"Conventional; Control\",\"researchStudyNotes\":\"Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling\",\"treatment\":\"HCC_31\",\"project\":\"\",\"dateArchived\":\"43175\",\"sampleStorageLocation\":\"AAFC Harrow\",\"sampleStorageConditions\":\"Dry/-80oC\",\"amountAvailable\":\"200-300g/10g\",\"pretreatment\":\"Yes; air dried 1 month/No; kept frozen\",\"alternativeContactInfo\":\"Brent Seuradge\",\"collectionInfo\":{\"id\":1053625,\"zeroPaddedDate\":\"\",\"latLon\":\"\"},\"mixsSpecification\":{\"id\":783666},\"group\":{\"id\":458,\"defaultRead\":false,\"defaultWrite\":false,\"defaultDelete\":false,\"defaultCreate\":false},\"biologicalCollection\":{\"id\":433,\"nagoyaRestricted\":false,\"uniqueId\":433},\"lastModified\":\"2021-03-05T00:56:08.407+00:00\"}}",
				"amount_available": "200-300g/10g",
				"research_study_notes": "Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling",
				"sample_storage_location": "AAFC Harrow",
				"alternative_contact_info": "Brent Seuradge",
				"sample_storage_conditions": "Dry/-80oC"
			},
			"preparationManagedAttributes": {},
			"extensionValues": {},
			"preparationRemarks": "Randomized Complete Block Design; 4 experimental replicates",
			"dwcDegreeOfEstablishment": None,
			"barcode": None,
			"publiclyReleasable": None,
			"notPubliclyReleasableReason": None,
			"tags": None,
			"materialSampleState": None,
			"materialSampleRemarks": "Conventional; Control",
			"stateChangedOn": None,
			"stateChangeRemarks": None,
			"associations": [],
			"allowDuplicateName": 'false',
			"restrictionFieldsExtension": {},
			"isRestricted": 'false',
			"restrictionRemarks": None,
			"sourceSet": None
		},
		"relationships": {
			"parentMaterialSample": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/parentMaterialSample",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/parentMaterialSample"
				}
			},
            "collectingEvent": {
                "data": {
                    "id": "2fbcc695-35e5-4977-939a-907c7b552fdf",
                    "type": "collecting-event"
                },
                "links": {
                    "self": "/api/v1/material-sample/01679480-bddb-4ae7-b4c7-098441527eb0/relationships/collectingEvent",
                    "related": "/api/v1/material-sample/01679480-bddb-4ae7-b4c7-098441527eb0/collectingEvent"
                }
            },
			"preparationMethod": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationMethod",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationMethod"
				}
			},
			"storageUnit": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/storageUnit",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/storageUnit"
				}
			},
			"projects": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/projects",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/projects"
				}
			},
			"preparedBy": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparedBy",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparedBy"
				}
			},
			"organism": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/organism",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/organism"
				}
			},
			"attachment": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/attachment",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/attachment"
				}
			},
			"collection": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/collection",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/collection"
				}
			},
			"preparationProtocol": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationProtocol",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationProtocol"
				}
			},
			"preparationType": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationType",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationType"
				}
			},
			"assemblages": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/assemblages",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/assemblages"
				}
			}
		}
	},
	"meta": {
		"totalResourceCount": 1, "external": [
			{
				"type": "person",
				"href": "agent/api/v1/person"
			},
			{
				"type": "metadata",
				"href": "objectstore/api/v1/metadata"
			}
		], "moduleVersion": "0.84"
	}
}
VALID_MATERIAL_SAMPLE_DATA = {
	"data": {
		"id": "182ed68e-7536-4ad4-868c-399c8e5d70f3",
		"type": "material-sample",
		"links": {
			"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3"
		},
		"attributes": {
			"version": 1,
			"group": "phillips-lab",
			"createdOn": "2024-03-07T16:35:26.865646Z",
			"createdBy": "s-seqdbsoil",
			"dwcCatalogNumber": None,
			"dwcOtherCatalogNumbers": [
				"HCC_31"
			],
			"materialSampleName": "HCC-2018-05-16-HCC_31",
			"materialSampleType": "MIXED_ORGANISMS",
			"materialSampleChildren": [],
			"preparationDate": None,
			"preservationType": None,
			"preparationFixative": None,
			"preparationMaterials": None,
			"preparationSubstrate": None,
			"managedAttributes": {
				"treatment": "HCC_31",
				"pretreatment": "Yes; air dried 1 month/No; kept frozen",
				"date_archived": "43175",
				"seq_db_legacy": "{\"Mixed Specimen\":{\"id\":9229,\"mixedSpecimenNumber\":\"HCC-2018-05-16-HCC_31\",\"otherIds\":\"HCC_31\",\"replicateInfo\":\"Randomized Complete Block Design; 4 experimental replicates\",\"substrateType\":\"Soil\",\"notes\":\"Conventional; Control\",\"researchStudyNotes\":\"Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling\",\"treatment\":\"HCC_31\",\"project\":\"\",\"dateArchived\":\"43175\",\"sampleStorageLocation\":\"AAFC Harrow\",\"sampleStorageConditions\":\"Dry/-80oC\",\"amountAvailable\":\"200-300g/10g\",\"pretreatment\":\"Yes; air dried 1 month/No; kept frozen\",\"alternativeContactInfo\":\"Brent Seuradge\",\"collectionInfo\":{\"id\":1053625,\"zeroPaddedDate\":\"\",\"latLon\":\"\"},\"mixsSpecification\":{\"id\":783666},\"group\":{\"id\":458,\"defaultRead\":false,\"defaultWrite\":false,\"defaultDelete\":false,\"defaultCreate\":false},\"biologicalCollection\":{\"id\":433,\"nagoyaRestricted\":false,\"uniqueId\":433},\"lastModified\":\"2021-03-05T00:56:08.407+00:00\"}}",
				"amount_available": "200-300g/10g",
				"research_study_notes": "Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling",
				"sample_storage_location": "AAFC Harrow",
				"alternative_contact_info": "Brent Seuradge",
				"sample_storage_conditions": "Dry/-80oC"
			},
			"preparationManagedAttributes": {},
			"extensionValues": {},
			"preparationRemarks": "Randomized Complete Block Design; 4 experimental replicates",
			"dwcDegreeOfEstablishment": None,
			"barcode": None,
			"publiclyReleasable": None,
			"notPubliclyReleasableReason": None,
			"tags": None,
			"materialSampleState": None,
			"materialSampleRemarks": "Conventional; Control",
			"stateChangedOn": None,
			"stateChangeRemarks": None,
			"associations": [],
			"allowDuplicateName": 'false',
			"restrictionFieldsExtension": {},
			"isRestricted": 'false',
			"restrictionRemarks": None,
			"sourceSet": None
		},
		"relationships": {
			"parentMaterialSample": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/parentMaterialSample",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/parentMaterialSample"
				},
						"data": {
							"id": "01902d3a-0ec1-7a57-8284-f4ba3aff1664",
							"type": "material-sample"
						},
			},
			"collectingEvent": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/collectingEvent",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/collectingEvent"
				}
			},
			"preparationMethod": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationMethod",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationMethod"
				}
			},
			"storageUnit": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/storageUnit",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/storageUnit"
				}
			},
			"projects": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/projects",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/projects"
				}
			},
			"preparedBy": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparedBy",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparedBy"
				}
			},
			"organism": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/organism",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/organism"
				}
			},
			"attachment": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/attachment",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/attachment"
				}
			},
			"collection": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/collection",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/collection"
				}
			},
			"preparationProtocol": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationProtocol",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationProtocol"
				}
			},
			"preparationType": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationType",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationType"
				}
			},
			"assemblages": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/assemblages",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/assemblages"
				}
			}
		}
	},
	"meta": {
		"totalResourceCount": 1, "external": [
			{
				"type": "person",
				"href": "agent/api/v1/person"
			},
			{
				"type": "metadata",
				"href": "objectstore/api/v1/metadata"
			}
		], "moduleVersion": "0.84"
	}
}


class MaterialSampleSchemaTest(unittest.TestCase):
	# def test_create_delete_entity(self):
	# 	schema = MaterialSampleSchema()
	# 	material_sample_api = MaterialSampleAPI()
	# 	try:
	# 		material_sample_attributes = MaterialSampleAttributesDTOBuilder().group("aafc").materialSampleName("test").materialSampleType("WHOLE_ORGANISM")\
	# 		.build()
	# 		material_sample = MaterialSampleDTOBuilder().attributes(material_sample_attributes).build()
	# 		serialized_material_sample = schema.dump(material_sample)
	# 		pp = pprint.PrettyPrinter(indent=0)
	# 		pp.pprint(serialized_material_sample)
	# 		response = material_sample_api.create_entity(serialized_material_sample)
	# 		id = response.json()['data']['id']
	# 		if response.status_code == 201:
	# 			response = material_sample_api.remove_entity(id)
	# 			self.assertEqual(response.status_code,204)
	# 	except ValidationError as e:
	# 		self.fail(f"Validation failed with error: {e.messages}")

	def test_serialize_materialsample(self):
		schema = MaterialSampleSchema()
		material_sample_attributes = MaterialSampleAttributesDTOBuilder().group("aafc").materialSampleName("test").materialSampleType("WHOLE_ORGANISM")\
		.build()
		material_sample = MaterialSampleDTOBuilder().attributes(material_sample_attributes).build()
		serialized_material_sample = schema.dump(material_sample)
		print(serialized_material_sample)
		self.assertIsInstance(serialized_material_sample, dict)

	def test_valid_materialsample_schema(self):
		# Create a schema instance and validate the data
		schema = MaterialSampleSchema()
		try:
			result = schema.load(VALID_MATERIAL_SAMPLE_DATA)
			result2 = schema.dump(result)
			pp = pprint.PrettyPrinter(indent=0)
			pp.pprint(result)
			self.assertIsInstance(result, MaterialSampleDTO)
		except ValidationError as e:
			self.fail(f"Validation failed with error: {e.messages}")

	def test_invalid_materialsample_schema(self):
		# Example invalid data with missing required fields
		invalid_data = {
		"data": {
		"id": "182ed68e-7536-4ad4-868c-399c8e5d70f3",
		"type": "material-sample",
		"links": {
			"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3"
		},
		"attributes": {
			"version": 1,
			#"group": "phillips-lab",
			"createdOn": "2024-03-07T16:35:26.865646Z",
			"createdBy": "s-seqdbsoil",
			"dwcCatalogNumber": None,
			"dwcOtherCatalogNumbers": [
				"HCC_31"
			],
			"materialSampleName": "HCC-2018-05-16-HCC_31",
			"materialSampleType": "MIXED_ORGANISMS",
			"materialSampleChildren": [],
			"preparationDate": None,
			"preservationType": None,
			"preparationFixative": None,
			"preparationMaterials": None,
			"preparationSubstrate": None,
			"managedAttributes": {
				"treatment": "HCC_31",
				"pretreatment": "Yes; air dried 1 month/No; kept frozen",
				"date_archived": "43175",
				"seq_db_legacy": "{\"Mixed Specimen\":{\"id\":9229,\"mixedSpecimenNumber\":\"HCC-2018-05-16-HCC_31\",\"otherIds\":\"HCC_31\",\"replicateInfo\":\"Randomized Complete Block Design; 4 experimental replicates\",\"substrateType\":\"Soil\",\"notes\":\"Conventional; Control\",\"researchStudyNotes\":\"Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling\",\"treatment\":\"HCC_31\",\"project\":\"\",\"dateArchived\":\"43175\",\"sampleStorageLocation\":\"AAFC Harrow\",\"sampleStorageConditions\":\"Dry/-80oC\",\"amountAvailable\":\"200-300g/10g\",\"pretreatment\":\"Yes; air dried 1 month/No; kept frozen\",\"alternativeContactInfo\":\"Brent Seuradge\",\"collectionInfo\":{\"id\":1053625,\"zeroPaddedDate\":\"\",\"latLon\":\"\"},\"mixsSpecification\":{\"id\":783666},\"group\":{\"id\":458,\"defaultRead\":false,\"defaultWrite\":false,\"defaultDelete\":false,\"defaultCreate\":false},\"biologicalCollection\":{\"id\":433,\"nagoyaRestricted\":false,\"uniqueId\":433},\"lastModified\":\"2021-03-05T00:56:08.407+00:00\"}}",
				"amount_available": "200-300g/10g",
				"research_study_notes": "Replicated field trial; Grid/ Randomized 'W' pattern across plot; Temporal sampling",
				"sample_storage_location": "AAFC Harrow",
				"alternative_contact_info": "Brent Seuradge",
				"sample_storage_conditions": "Dry/-80oC"
			},
			"preparationManagedAttributes": {},
			"extensionValues": {},
			"preparationRemarks": "Randomized Complete Block Design; 4 experimental replicates",
			"dwcDegreeOfEstablishment": None,
			"barcode": None,
			"publiclyReleasable": None,
			"notPubliclyReleasableReason": None,
			"tags": None,
			"materialSampleState": None,
			"materialSampleRemarks": "Conventional; Control",
			"stateChangedOn": None,
			"stateChangeRemarks": None,
			"associations": [],
			"allowDuplicateName": 'false',
			"restrictionFieldsExtension": {},
			"isRestricted": 'false',
			"restrictionRemarks": None,
			"sourceSet": None
		},
		"relationships": {
			"parentMaterialSample": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/parentMaterialSample",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/parentMaterialSample"
				}
			},
			"collectingEvent": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/collectingEvent",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/collectingEvent"
				}
			},
			"preparationMethod": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationMethod",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationMethod"
				}
			},
			"storageUnit": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/storageUnit",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/storageUnit"
				}
			},
			"projects": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/projects",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/projects"
				}
			},
			"preparedBy": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparedBy",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparedBy"
				}
			},
			"organism": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/organism",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/organism"
				}
			},
			"attachment": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/attachment",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/attachment"
				}
			},
			"collection": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/collection",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/collection"
				}
			},
			"preparationProtocol": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationProtocol",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationProtocol"
				}
			},
			"preparationType": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/preparationType",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/preparationType"
				}
			},
			"assemblages": {
				"links": {
					"self": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/relationships/assemblages",
					"related": "/api/v1/material-sample/182ed68e-7536-4ad4-868c-399c8e5d70f3/assemblages"
				}
			}
		}
	},
	"meta": {
		"totalResourceCount": 1, "moduleVersion": "0.84"
	}
}
		# Create a schema instance and attempt to validate the invalid data
		schema = MaterialSampleSchema()
		with self.assertRaises(ValidationError):
			test = schema.load(invalid_data)
			print(test)

if __name__ == "__main__":
	unittest.main()
