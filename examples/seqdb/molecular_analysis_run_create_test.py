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
from dinapy.schemas.molecular_analysis_run_pydantic import (
    MolecularAnalysisRunDocument, MolecularAnalysisRunData, MolecularAnalysisRunAttributes
)
# Molecular Analysis Run Item Imports
from dinapy.apis.seqdbapi.molecular_analysis_run_item_api import MolecularAnalysisRunItemApi
from dinapy.schemas.molecular_analysis_run_item_pydantic import (
    MolecularAnalysisRunItemDocument, MolecularAnalysisRunItemData, MolecularAnalysisRunItemAttributes
)
# Seq Reaction Imports
from dinapy.apis.seqdbapi.seqreactionapi import SeqReactionApi
from dinapy.schemas.seq_reaction_pydantic import (
    SeqReactionDocument, SeqReactionData, SeqReactionAttributes
)
# Molecular Analysis Result Imports
from dinapy.apis.seqdbapi.molecular_analysis_result_api import MolecularAnalysisResultApi
from dinapy.schemas.molecular_analysis_result_pydantic import (
    MolecularAnalysisResultDocument, MolecularAnalysisResultData, MolecularAnalysisResultAttributes
)

from dinapy.schemas.pydantic_base import RelationshipData, RelationshipLinkage

def main():
    # Create a Molecular Analysis Run
    MOCK_RUN_NAME = "test run with results"

    molecular_analysis_run_api = MolecularAnalysisRunApi()
    serialized_molecular_analysis_run = MolecularAnalysisRunDocument(
        data=MolecularAnalysisRunData(
            type="molecular-analysis-run",
            attributes=MolecularAnalysisRunAttributes(
                createdBy="dina-admin",
                name=MOCK_RUN_NAME,
                group="aafc"
            )
        )
    ).serialize()

    run_response = molecular_analysis_run_api.create_entity(serialized_molecular_analysis_run)
    run_id = run_response.json()['data']['id']
    print("Run: " + run_id + "\n")

    # Create 10 Molecular Analysis Results, Molecular Analysis Run Items, and Seq Reactions
    for i in range(10):
        # Create a Molecular Analysis Result
        molecular_analysis_result_api = MolecularAnalysisResultApi()
        serialized_molecular_analysis_result = MolecularAnalysisResultDocument(
            data=MolecularAnalysisResultData(
                type="molecular-analysis-result",
                attributes=MolecularAnalysisResultAttributes(
                    createdBy="dina-admin",
                    group="aafc"
                )
            )
        ).serialize()

        result_response = molecular_analysis_result_api.create_entity(serialized_molecular_analysis_result)
        result_id = result_response.json()['data']['id']
        print("Result " + str(i) + ": " + result_id)

        # Create Molecular Analysis Run Item with relationships to Run and Result
        molecular_analysis_run_item_api = MolecularAnalysisRunItemApi()
        serialized_molecular_analysis_run_item = MolecularAnalysisRunItemDocument(
            data=MolecularAnalysisRunItemData(
                type="molecular-analysis-run-item",
                attributes=MolecularAnalysisRunItemAttributes(
                    createdBy="dina-admin",
                    usageType="seq-reaction"
                ),
                relationships={
                    "molecular-analysis-run": RelationshipData(
                        data=RelationshipLinkage(type="run", id=run_id)
                    ),
                    "molecular-analysis-result": RelationshipData(
                        data=RelationshipLinkage(type="result", id=result_id)
                    )
                }
            )
        ).serialize()

        item_response = molecular_analysis_run_item_api.create_entity(serialized_molecular_analysis_run_item)
        item_id = item_response.json()['data']['id']
        print("Run Item " + str(i) + ": " + item_id)

        # Create Seq Reaction with relationship to Run Item
        seq_reaction_api = SeqReactionApi()
        serialized_seq_reaction = SeqReactionDocument(
            data=SeqReactionData(
                type="seq-reaction",
                attributes=SeqReactionAttributes(
                    createdBy="dina-admin",
                    group="aafc"
                ),
                relationships={
                    "molecular-analysis-run-item": RelationshipData(
                        data=RelationshipLinkage(
                            type="molecular-analysis-run-item",
                            id=item_id
                        )
                    )
                }
            )
        ).serialize()

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