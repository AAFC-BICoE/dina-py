import csv
import argparse
import sys
import os
from marshmallow.exceptions import ValidationError
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.entities.StorageUnitCoordinate import *
from dinapy.entities.Relationships import *
from dinapy.apis.collectionapi.storageunitusageapi import StorageUnitUsageAPI
from dinapy.schemas.storageunitusageschema import StorageUnitUsage

from dinapy.utils import *
from dinapy.utils import *

def parse_csv_and_populate_dto(csv_file):

	with open(csv_file, 'r') as f:

		reader = csv.DictReader(f)
		
		serialized_objects = []
		
		for row in reader:

			attributes = StorageUnitCoordinateAttributesDTOBuilder()\
				.usageType("material-sample")\
				.wellRow(row['Row'],)\
				.wellColumn(int(row['Column']))\
				.build()

			if row['storageUnitId'] != '':
				storageUnitId = row['storageUnitId']
			else:
				storageUnitId = '0190f065-3d4b-7a6d-be78-a49548922396'
			relationships = RelationshipDTO.Builder()\
				.add_relationship("storageUnit", "storage-unit", storageUnitId,)\
				.build()
				# .add_relationship("storageUnitType", "storage-unit-type", row['storageUnitTypeId'])\
			
			dto = StorageUnitCoordinateDTOBuilder()\
				.attributes(attributes)\
				.relationships(relationships.relationships)\
				.build()
			
			schema = StorageUnitUsage()
			try:
				serialized_storage_unit_usage = schema.dump(dto)
				serialized_objects.append(serialized_storage_unit_usage)
			except ValidationError as e:
				print(f"Validation failed with error: {e.messages}")
			
		return serialized_objects
	
class MaterialSampleSchemaTest(unittest.TestCase):

	dto_list = parse_csv_and_populate_dto("pcrbatchitemdata-gorzelak.csv")

