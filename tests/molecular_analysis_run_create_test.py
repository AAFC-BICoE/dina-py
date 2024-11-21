from time import sleep
import json
import pprint
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

# MOCK_SEQ_REACTION_ARRAY_UUID = [
#     "ffc289d3-79b0-4e3f-9afb-7e7443899e34",
#     "7de2b17b-88b5-4d8c-885a-89483d48dd8c",
#     "87034e47-8387-49da-b5b3-9e4925afd867",
#     "81492540-29ee-4737-b2dc-3e7b30c35c28",
#     "31452c50-d796-4b73-8283-506da7f009ef",
#     "fbe9b49e-aef5-40cd-96ac-407645809c35",
#     "343bedf4-d5c3-4081-ab18-be2cd5d3aac4",
#     "ae5f41d8-e694-4972-a726-a41b9d849e3d",
#     "67438fff-80a1-4c9b-b418-a5ec19b24f49",
#     "740621bc-61a1-40e4-9cee-9bea8e7ed74d"
# ]

def main():
    # Create a Molecular Analysis Run
    molecular_analysis_run_api = MolecularAnalysisRunApi()
    molecular_analysis_run_attributes = MolecularAnalysisRunAttributesDTOBuilder(
        ).set_createdBy("dina-admin").set_name("test MARun 3").set_group("aafc").build()
    molecular_analysis_run = MolecularAnalysisRunDTOBuilder(
        ).set_attributes(molecular_analysis_run_attributes).build()
    molecular_analysis_run_schema = MolecularAnalysisRunSchema()

    serialized_molecular_analysis_run = molecular_analysis_run_schema.dump(molecular_analysis_run)

    run_response = molecular_analysis_run_api.create_entity(serialized_molecular_analysis_run)
    run_id = run_response.json()['data']['id']
    print("Run: " + run_id + "\n")

    run_to_item_relationship = (
        RelationshipDTO.Builder()
            .add_relationship(
                "run",                      # Relationship Name
                "molecular-analysis-run",   # Type
                run_id                      # UUID
        )
        .build()
    )

    # test MARun 2 UUID
    # 05997165-27de-4d7e-a8aa-d059913bec3b

    # Create 10 Molecular Analysis Run Items
    for i in range(10):
        molecular_analysis_run_item_api = MolecularAnalysisRunItemApi()
        molecular_analysis_run_item_attributes = MolecularAnalysisRunItemAttributesDTOBuilder(
            ).set_createdBy("dina-admin").set_usageType("seq-reaction").build()
        molecular_analysis_run_item = MolecularAnalysisRunItemDTOBuilder(
            ).set_attributes(molecular_analysis_run_item_attributes).set_relationships(run_to_item_relationship).build()
        molecular_analysis_run_item_schema = MolecularAnalysisRunItemSchema()

        serialized_molecular_analysis_run_item = molecular_analysis_run_item_schema.dump(molecular_analysis_run_item)

        item_response = molecular_analysis_run_item_api.create_entity(serialized_molecular_analysis_run_item)
        item_id = item_response.json()['data']['id']
        print("Run Item: " + i + " " + item_id + "\n")

        item_to_seqr_relationship = (
            RelationshipDTO.Builder()
                .add_relationship(
                    "molecularAnalysisRunItem",     # Relationship Name
                    "molecular-analysis-run-item",  # Type
                    item_id                         # UUID
            )
            .build()
        )

        seq_reaction_api = SeqReactionApi()
        seq_reaction_attributes = SeqReactionAttributesDTOBuilder(
            ).set_createdBy("dina-admin").set_group("aafc").build()
        seq_reaction = SeqReactionDTOBuilder(
            ).set_attributes(seq_reaction_attributes).set_relationships(item_to_seqr_relationship).build()
        seq_reaction_schema = SeqReactionSchema()

        serialized_seq_reaction = seq_reaction_schema.dump(seq_reaction)

        seqr_response = seq_reaction_api.create_entity(serialized_seq_reaction)
        seqr_id = seqr_response.json()['data']['id']
        print("Seq Reaction: " + i + " " + seqr_id + "\n\n")

if __name__ == "__main__":
    main()
