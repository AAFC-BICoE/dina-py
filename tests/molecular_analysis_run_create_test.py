from time import sleep
import json
from pprint import pprint
import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Molecular Analysis Run Imports
from dinapy.apis.seqdbapi.molecular_analysis_run_api import MolecularAnalysisRunApi
from dinapy.entities.MolecularAnalysisRun import MolecularAnalysisRunDTOBuilder, MolecularAnalysisRunAttributesDTOBuilder
from dinapy.schemas.molecular_analysis_run_schema import MolecularAnalysisRunSchema
# Molecular Analysis Run Item Imports
from dinapy.apis.seqdbapi.molecular_analysis_run_item_api import MolecularAnalysisRunItemApi
from dinapy.entities.MolecularAnalysisRunItem import MolecularAnalysisRunItemDTOBuilder, MolecularAnalysisRunItemAttributesDTOBuilder
from dinapy.schemas.molecular_analysis_run_item_schema import MolecularAnalysisRunItemSchema
# Seq Reaction Imports
from dinapy.apis.seqdbapi.seqreactionapi import SeqReactionApi
from dinapy.entities.SeqReaction import SeqReactionDTOBuilder, SeqReactionAttributesDTOBuilder
from dinapy.schemas.seqreactionschema import SeqReactionSchema
# Molecular Analysis Result Imports
from dinapy.apis.seqdbapi.molecular_analysis_result_api import MolecularAnalysisResultApi
from dinapy.entities.MolecularAnalysisResult import MolecularAnalysisResultDTOBuilder, MolecularAnalysisResultAttributesDTOBuilder
from dinapy.schemas.molecular_analysis_result_schema import MolecularAnalysisResultSchema

from dinapy.entities.Relationships import RelationshipDTO

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
    # Create a Molecular Analysis Run
    MOCK_RUN_NAME = "test run with results"

    molecular_analysis_run_api = MolecularAnalysisRunApi()
    molecular_analysis_run_attributes = MolecularAnalysisRunAttributesDTOBuilder(
        ).set_createdBy("dina-admin").set_name(MOCK_RUN_NAME).set_group("aafc").build()
    molecular_analysis_run = MolecularAnalysisRunDTOBuilder(
        ).set_attributes(molecular_analysis_run_attributes).build()
    molecular_analysis_run_schema = MolecularAnalysisRunSchema()

    serialized_molecular_analysis_run = molecular_analysis_run_schema.dump(molecular_analysis_run)

    run_response = molecular_analysis_run_api.create_entity(serialized_molecular_analysis_run)
    run_id = run_response.json()['data']['id']
    print("Run: " + run_id + "\n")

    # Create 10 Molecular Analysis Results, Molecular Analysis Run Items, and Seq Reactions
    for i in range(10):
        # Create a Molecular Analysis Result
        molecular_analysis_result_api = MolecularAnalysisResultApi()
        molecular_analysis_result_attributes = MolecularAnalysisResultAttributesDTOBuilder(
            ).set_createdBy("dina-admin").set_group("aafc").build()
        molecular_analysis_result = MolecularAnalysisResultDTOBuilder(
            ).set_attributes(molecular_analysis_result_attributes).build()
        molecular_analysis_result_schema = MolecularAnalysisResultSchema()

        serialized_molecular_analysis_result = molecular_analysis_result_schema.dump(molecular_analysis_result)

        result_response = molecular_analysis_result_api.create_entity(serialized_molecular_analysis_result)
        result_id = result_response.json()['data']['id']
        print("Result " + str(i) + ": " + result_id)

        # Create Relationships for each Run Item
        run_item_relationships = (
            RelationshipDTO.Builder()
                .add_relationship(
                    "molecular-analysis-run",   # Relationship Name
                    "run",                      # Type
                    run_id                      # UUID
                )
                .add_relationship(
                    "molecular-analysis-result",    # Relationship Name
                    "result",                       # Type
                    result_id                       # UUID
                )
            .build()
        )

        # Create Molecular Analysis Run Item
        molecular_analysis_run_item_api = MolecularAnalysisRunItemApi()
        molecular_analysis_run_item_attributes = MolecularAnalysisRunItemAttributesDTOBuilder(
            ).set_createdBy("dina-admin").set_usageType("seq-reaction").build()
        molecular_analysis_run_item = MolecularAnalysisRunItemDTOBuilder(
            ).set_attributes(molecular_analysis_run_item_attributes).set_relationships(run_item_relationships).build()
        molecular_analysis_run_item_schema = MolecularAnalysisRunItemSchema()

        serialized_molecular_analysis_run_item = molecular_analysis_run_item_schema.dump(molecular_analysis_run_item)

        item_response = molecular_analysis_run_item_api.create_entity(serialized_molecular_analysis_run_item)
        item_id = item_response.json()['data']['id']
        print("Run Item " + str(i) + ": " + item_id)

        # Create Relationships for each Seq Reaction
        item_to_seqr_relationship = (
            RelationshipDTO.Builder()
                .add_relationship(
                    "molecular-analysis-run-item",  # Relationship Name
                    "molecular-analysis-run-item",  # Type
                    item_id                         # UUID
            )
            .build()
        )

        # Create Seq Reaction
        seq_reaction_api = SeqReactionApi()
        seq_reaction_attributes = SeqReactionAttributesDTOBuilder(
            ).set_createdBy("dina-admin").set_group("aafc").build()
        seq_reaction = SeqReactionDTOBuilder(
            ).set_attributes(seq_reaction_attributes).set_relationships(item_to_seqr_relationship).build()
        seq_reaction_schema = SeqReactionSchema()

        serialized_seq_reaction = seq_reaction_schema.dump(seq_reaction)

        seqr_response = seq_reaction_api.create_entity(serialized_seq_reaction)
        seqr_id = seqr_response.json()['data']['id']
        print("Seq Reaction " + str(i) + ": " + seqr_id + "\n")

if __name__ == "__main__":
    main()

# test run with results UUIDs in dev2
# Run: d35d3e13-49d8-47eb-9536-a6ee7abc7db0

# Result 0: 82bdd6c4-50d7-4717-833b-792dac8c62b8
# Run Item 0: 0142a2c5-a950-4962-8856-445c7f5770d9
# Seq Reaction 0: 177a9363-4a4b-4f80-a736-bb1cfefcd9b5

# Result 1: c89e1368-8038-4f46-b37b-bdf1fdc5f9be
# Run Item 1: 0a46b4ea-61ef-40b8-9b41-013195fd30a6
# Seq Reaction 1: 0546827d-708f-4ac1-b3bf-386782048ca3

# Result 2: 12f6dcf4-173f-41cc-9a6c-43203633eb7f
# Run Item 2: 851b0e91-cbd5-41bb-8b13-6dff96f9faba
# Seq Reaction 2: 32daf295-eff5-4628-a314-a5d36af8645d

# Result 3: 6fd4b045-5c18-4182-a56b-ad4858efc9f2
# Run Item 3: 69b1f2b6-62aa-4e48-82d7-c6b71d1a9dd4
# Seq Reaction 3: 3776bab6-ae16-40ef-8c5e-c387c048c5b2

# Result 4: 69a9ee8c-9c99-46e9-9dda-c96c55066dc4
# Run Item 4: 9d9441bf-eab3-4a34-96aa-0f9f7b11b290
# Seq Reaction 4: 139ab393-717a-4541-bd09-9b4fd104e89c

# Result 5: 73018b50-1d3b-435e-a506-a8e97d965414
# Run Item 5: 3fbb1a06-5cf1-4181-b96e-c7d9e4fb2ec5
# Seq Reaction 5: e7fe25da-52dd-43c5-8c33-eb30fca46cbc

# Result 6: c8b62dbe-9420-442b-aee3-b870165a0c13
# Run Item 6: 415fe61a-1920-4dd5-a264-9cba1f83602d
# Seq Reaction 6: 14590fa1-4649-4109-b19f-0c573faa7da6

# Result 7: 814c9c79-0b58-4534-9459-aa20ba580e26
# Run Item 7: d5301681-3e4e-4206-9daf-23b8072ade70
# Seq Reaction 7: 80350e98-ab86-48cb-89c2-89197cb3d4a7

# Result 8: c448cf1c-72a2-4fa9-b9f6-278abbcd9d55
# Run Item 8: 9eea0be4-7109-4743-a72e-e2b8738e130d
# Seq Reaction 8: c9e94405-5884-499a-9cfb-6aea683ef5a9

# Result 9: 018fe165-12f0-417d-895b-39f84222b26d
# Run Item 9: 71f8e269-7483-4f88-9bc0-d5651d476c04
# Seq Reaction 9: 91fe4965-ef82-41b1-b3ae-cd0457085c1f