import csv
import argparse
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dinapy.entities.StorageUnitCoordinate import *
from dinapy.entities.Relationships import *
from dinapy.apis.collectionapi.storageunitusageapi import StorageUnitUsageAPI

from dinapy.utils import *
from dinapy.utils import *

def parse_csv_and_populate_dto(csv_file):

	with open(csv_file, 'r') as f:

		reader = csv.DictReader(f)
		
		dtos = []
		
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
				.relationships(relationships)\
				.build()
			dtos.append(dto)
			
		return dtos
	
def main(file_name):

	storage_unit_usage_api = StorageUnitUsageAPI()

	dto_list = parse_csv_and_populate_dto(file_name)

	for dto in dto_list:
		response = storage_unit_usage_api.create_entity(dto)
		if response.status_code == 201:
			print("ok")
		print(response.json())

if __name__ == '__main__':

	# def update_csv(csv_file,id):
	# 	with open(csv_file, 'w') as f:

		# Create the parser
	parser = argparse.ArgumentParser(description="Process a CSV file")

		# Add the arguments
	parser.add_argument('-f', '--file', type=str, required=True, help="The CSV file to process")

		# Parse the arguments
	args = parser.parse_args()

		# Call the main function with the file name argument
	main(args.file)