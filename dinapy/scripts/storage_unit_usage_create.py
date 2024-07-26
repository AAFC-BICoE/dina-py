import csv

from dinapy.apis.collectionapi.storageunitusageapi import StorageUnitUsageAPI

from dinapy.entities.StorageUnitCoordinate import *
from dinapy.entities.Relationships import *
 
from dinapy.utils import *


def main():

	storage_unit_usage_api = StorageUnitUsageAPI()

	dto_list = parse_csv_and_populate_dto("file_name")

	for dto in dto_list:
		storage_unit_usage_api.create_entity(dto)



if __name__ == '__main__':
	main()
	
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

			relationships = RelationshipDTO.Builder()\
				.add_relationship("storageUnit", "storage-unit", row['storageUnitId'],)\
				.build()
				# .add_relationship("storageUnitType", "storage-unit-type", row['storageUnitTypeId'])\
			
			dto = StorageUnitCoordinateDTOBuilder()\
				.attributes(attributes)\
				.relationships(relationships)\
				.build()
			dtos.append(dto)

		return dtos