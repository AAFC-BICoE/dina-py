import csv
import argparse
import sys
import os
from marshmallow.exceptions import ValidationError
import unittest
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.entities.StorageUnitUsage import *
from dinapy.entities.Relationships import *
from dinapy.apis.collectionapi.storageunitusageapi import StorageUnitUsageAPI
from dinapy.schemas.storageunitusageschema import StorageUnitUsage

from dinapy.utils import *
from dinapy.utils import *

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

class MaterialSampleSchemaTest(unittest.TestCase):
			
	storageUnitId = '0190f065-3d4b-7a6d-be78-a49548922396'
	relationships = RelationshipDTO.Builder()\
		.add_relationship("storageUnit", "storage-unit", storageUnitId)\
		.build()
		# .add_relationship("storageUnitType", "storage-unit-type", row['storageUnitTypeId'])\
	
	dto = StorageUnitUsageDTOBuilder()\
		.set_usageType("material-sample")\
		.set_relationships(relationships)\
		.build()
	
	schema = StorageUnitUsage()

	try:
		serialized_storage_unit_usage = schema.dump(dto)
	except ValidationError as e:
		print(f"Validation failed with error: {e.messages}")
