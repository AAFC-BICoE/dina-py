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

    # test MARun 2 UUID in dev2
    # marun2 = "05997165-27de-4d7e-a8aa-d059913bec3b"

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
