from time import sleep
import json
from pprint import pprint
import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Molecular Analysis Run Imports
from dinapy.apis.seqdbapi.molecularanalysisrunapi import MolecularAnalysisRunApi
from dinapy.entities.MolecularAnalysisRun import MolecularAnalysisRunDTOBuilder, MolecularAnalysisRunAttributesDTOBuilder
from dinapy.schemas.molecularanalysisrunschema import MolecularAnalysisRunSchema
# Molecular Analysis Run Item Imports
from dinapy.apis.seqdbapi.molecularanalysisrunitemapi import MolecularAnalysisRunItemApi
from dinapy.entities.MolecularAnalysisRunItem import MolecularAnalysisRunItemDTOBuilder, MolecularAnalysisRunItemAttributesDTOBuilder
from dinapy.schemas.molecularanalysisrunitemschema import MolecularAnalysisRunItemSchema
# Seq Reaction Imports
from dinapy.apis.seqdbapi.seqreactionapi import SeqReactionApi
from dinapy.entities.SeqReaction import SeqReactionDTOBuilder, SeqReactionAttributesDTOBuilder
from dinapy.schemas.seqreactionschema import SeqReactionSchema

from dinapy.entities.Relationships import RelationshipDTO

os.environ["keycloak_username"] = "dina-admin"
os.environ["keycloak_password"] = "dina-admin"

def main():
    # Create a Molecular Analysis Run
    MOCK_RUN_NAME = "test run"

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

    # Create Relationship linking to created Molecular Analysis Run
    run_to_item_relationship = (
        RelationshipDTO.Builder()
            .add_relationship(
                "molecular-analysis-run",   # Relationship Name
                "run",                      # Type
                run_id                      # UUID
        )
        .build()
    )

    # Create 10 Molecular Analysis Run Items and Seq Reactions to link
    for i in range(10):
        # Create Molecular Analysis Run Item
        molecular_analysis_run_item_api = MolecularAnalysisRunItemApi()
        molecular_analysis_run_item_attributes = MolecularAnalysisRunItemAttributesDTOBuilder(
            ).set_createdBy("dina-admin").set_usageType("seq-reaction").build()
        molecular_analysis_run_item = MolecularAnalysisRunItemDTOBuilder(
            ).set_attributes(molecular_analysis_run_item_attributes).set_relationships(run_to_item_relationship).build()
        molecular_analysis_run_item_schema = MolecularAnalysisRunItemSchema()

        serialized_molecular_analysis_run_item = molecular_analysis_run_item_schema.dump(molecular_analysis_run_item)

        item_response = molecular_analysis_run_item_api.create_entity(serialized_molecular_analysis_run_item)
        item_id = item_response.json()['data']['id']
        print("Run Item " + str(i) + ": " + item_id)

        # Create Relationship linking to created Molecular Analysis Run Item
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

# test MARun 3 UUIDs in dev2
# Run: acd740e0-7e7d-4ad7-9751-1754d1c54458

# Run Item 0: 09b5abcf-76ba-4fda-b60e-6e1f6c159233
# Seq Reaction 0: 9fc86d73-95b9-4450-9018-778635f21f1c

# Run Item 1: 90a5aab1-3e36-4d5b-af2d-acf102687141
# Seq Reaction 1: 0473959d-4d3c-4072-bc9c-f7e49d3c8724

# Run Item 2: a51405be-93fa-451a-add6-d9859451aa91
# Seq Reaction 2: 7a446380-2f7d-47cf-8369-c70aa820b695

# Run Item 3: 7ca10b2b-4fb9-4ff0-a0ef-9fa236ad64d8
# Seq Reaction 3: 75657297-cff2-4b44-8413-973cbc7b7d8e

# Run Item 4: d9935ce2-7360-4792-a60e-26213d0ea9a9
# Seq Reaction 4: 2cbb1a4c-1c58-4ab4-ab1f-849b5d325f52

# Run Item 5: c0521a5e-fbfa-4b2a-ae74-55a3d358a97c
# Seq Reaction 5: 47821630-4399-4394-8909-949c45662eb9

# Run Item 6: e3efe617-25a0-4258-9890-8a9ff4e0d0d3
# Seq Reaction 6: 65c18431-52fe-4951-b595-be9e1784b092

# Run Item 7: 34bd329b-c12f-4dc8-8369-e983ecd78948
# Seq Reaction 7: 8b905db5-ba27-43fe-a731-c1973b5d30e3

# Run Item 8: 719a790d-0ef4-416c-b2d1-c0a55e0108a1
# Seq Reaction 8: 5fc3f435-2f19-420c-89bc-6409ce480f0d

# Run Item 9: 82a9c526-2a33-4b5f-a02f-e61f5099d88e
# Seq Reaction 9: 187b987d-dc00-4fe4-b4e5-f40ece95ad57