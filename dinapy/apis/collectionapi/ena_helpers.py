"""
Helper functions for processing DINA collection API responses for ENA submission.

The collection API returns JSON with 'data' (material samples) and 'included' (related entities).
The ENA mappers expect deserialized DTO objects. These helpers bridge the gap.

Example usage:
    >>> from dinapy.apis.collectionapi.materialsampleapi import MaterialSampleAPI
    >>> from dinapy.apis.collectionapi.ena_helpers import process_collection_for_ena
    >>> 
    >>> # Fetch collection
    >>> api = MaterialSampleAPI()
    >>> response = api.get_by_collection(
    ...     collection_uuid="your-collection-id",
    ...     include=['collectingEvent', 'organism']
    ... )
    >>> 
    >>> # Convert all samples to ENA format
    >>> ena_samples = process_collection_for_ena(
    ...     response.json(),
    ...     email="your.email@example.com"
    ... )
    >>> 
    >>> # Submit to ENA
    >>> for ena_sample in ena_samples:
    ...     receipt = workflow.submit_sample_xml(ena_sample, action="ADD")
"""

from typing import Dict, List, Optional, Tuple


def find_included_by_relationship(included_data: List[dict], relationship: dict) -> Optional[Dict]:
    """
    Find an included entity by matching the relationship reference.
    
    Args:
        included_data: List of included entities from JSONAPI response
        relationship: Relationship object with 'type' and 'id' from data.relationships
    
    Returns:
        The matching included entity dict, or None if not found
    
    Example:
        >>> included = response.json()['included']
        >>> relationship = sample['relationships']['collectingEvent']
        >>> ce_data = find_included_by_relationship(included, relationship)
    """
    if not relationship or not included_data:
        return None
    
    # Get the reference from relationship
    rel_data = relationship.get('data')
    if not rel_data:
        return None
    
    # Handle both single relationship and many (list)
    if isinstance(rel_data, list):
        if len(rel_data) == 0:
            return None
        rel_data = rel_data[0]  # Take first for now
    
    rel_type = rel_data.get('type')
    rel_id = rel_data.get('id')
    
    # Find matching included entity
    for included in included_data:
        if included.get('type') == rel_type and included.get('id') == rel_id:
            return included
    
    return None


def prepare_sample_for_ena_mapping(
    sample_data: dict,
    included_data: List[dict]
) -> Tuple[object, Optional[object], Optional[dict]]:
    """
    Prepare a material sample and its relationships for ENA mapping.
    
    This function:
    1. Deserializes the material sample using MaterialSampleSchema
    2. Finds and deserializes the related collectingEvent (if present)
    3. Extracts organism data for taxon resolution
    4. Returns DTOs ready for the ENA mappers
    
    Args:
        sample_data: Single material sample from response['data']
        included_data: List of included entities from response['included']
    
    Returns:
        tuple: (material_sample_dto, collecting_event_dto, organism_data_dict)
               Any of these can be None if not found/present
    
    Example:
        >>> response = material_sample_api.get_by_collection(collection_uuid)
        >>> samples = response.json()['data']
        >>> included = response.json()['included']
        >>> 
        >>> for sample in samples:
        >>>     ms_dto, ce_dto, org_data = prepare_sample_for_ena_mapping(sample, included)
        >>>     ena_sample = material_sample_to_ena(ms_dto, ce_dto, organism_data=org_data)
    """
    from dinapy.schemas.materialsampleschema import MaterialSampleSchema
    from dinapy.schemas.collectingeventschema import CollectingEventSchema
    
    # Deserialize material sample
    material_sample_schema = MaterialSampleSchema()
    material_sample_dto = material_sample_schema.load({'data': sample_data})
    
    # Find and deserialize collecting event
    collecting_event_dto = None
    relationships = sample_data.get('relationships', {})
    ce_relationship = relationships.get('collectingEvent')
    
    if ce_relationship:
        ce_data = find_included_by_relationship(included_data, ce_relationship)
        if ce_data:
            try:
                ce_schema = CollectingEventSchema()
                collecting_event_dto = ce_schema.load({'data': ce_data})
            except Exception as e:
                print(f"Warning: Could not deserialize collecting event: {e}")
    
    # Extract organism data (for taxon resolution)
    # The mapper already handles the raw organism data from JSONAPI included array
    organism_data = None
    org_relationship = relationships.get('organism')
    
    if org_relationship:
        # Just pass the raw organism data - the mapper handles both formats:
        # 1. From included array: {"id": "...", "type": "organism", "attributes": {...}}
        # 2. From API call: {"data": {"id": "...", "type": "organism", "attributes": {...}}}
        organism_data = find_included_by_relationship(included_data, org_relationship)
    
    return material_sample_dto, collecting_event_dto, organism_data


def process_collection_for_ena(
    collection_response: dict,
    taxon_id: Optional[int] = None,
    email: Optional[str] = None
) -> List[object]:
    """
    Process an entire collection API response and convert all samples to ENA Sample models.
    
    This is a convenience function that handles the complete workflow:
    - Extracts samples and included data from collection response
    - Prepares DTOs for each sample
    - Maps to ENA Sample models
    - Returns list ready for submission
    
    Args:
        collection_response: Full JSON response from get_by_collection()
        taxon_id: Optional NCBI taxon ID to use for all samples
        email: Email for NCBI API requests (for auto-resolving taxon IDs)
    
    Returns:
        List of ENA Sample models ready for submission
    
    Example:
        >>> api = MaterialSampleAPI()
        >>> response = api.get_by_collection(
        ...     collection_uuid="your-collection-id",
        ...     include=['collectingEvent', 'organism']
        ... )
        >>> 
        >>> ena_samples = process_collection_for_ena(
        ...     response.json(),
        ...     email="your.email@example.com"
        ... )
        >>> 
        >>> # Submit to ENA
        >>> workflow = ENASubmissionWorkflow(username="...", password="...", test=True)
        >>> for ena_sample in ena_samples:
        ...     receipt = workflow.submit_sample_xml(ena_sample, action="ADD")
        ...     print(f"Submitted: {receipt.get_accession('SAMPLE')}")
    """
    from dinapy.ena.mappers.dina_to_ena.mappers_dto import material_sample_to_ena
    
    samples_data = collection_response.get('data', [])
    included_data = collection_response.get('included', [])
    
    ena_samples = []
    taxon_cache = {}  # Shared cache for taxon ID and geocoding lookups
    
    for sample_data in samples_data:
        try:
            # Prepare DTOs
            ms_dto, ce_dto, org_data = prepare_sample_for_ena_mapping(sample_data, included_data)
            
            # Convert to ENA Sample
            ena_sample = material_sample_to_ena(
                material_sample=ms_dto,
                collecting_event=ce_dto,
                taxon_id=taxon_id,
                organism_data=org_data,
                email=email,
                taxon_cache=taxon_cache,  # Reuse cache across samples
                include_unmapped=True
            )
            
            ena_samples.append(ena_sample)
            
        except Exception as e:
            sample_id = sample_data.get('id', 'unknown')
            print(f"Error processing sample {sample_id}: {e}")
            continue
    
    return ena_samples
