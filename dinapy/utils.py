def get_dina_records_by_field(api,field,value,step_size=500):
    """Fetches records from the Dina API filtered by a specific field and value.

    Args:
        api (DinaAPI): An instance of a DinaAPI subclass to interact with the API
        field (str): The field to filter by
        value (str): The value to filter by
        step_size (int, optional): The number of records to fetch in each API call. Defaults to 500.

    Returns:
        data: A list of records matching the filter criteria
    """
    step = step_size
    offset = 0
    data = []

    params = {
        f"filter[{field}][EQ]": value,
        "sort": "-createdOn"
    }

    while True:
        params["page[limit]"] = step
        params["page[offset]"] = offset
        record_list = api.get_entity_by_param(params)
        batch = record_list.json()["data"]
        data.extend(batch)
        offset += step

        # Check if we got less than step (last page)
        if len(batch) < step:
            break
        
    return data

def get_dina_records_by_field_with_include(api,field,value,include_param,step_size=500):
    """Fetches records from the Dina API filtered by a specific field and value, including additional relationships.

    Args:
        api (DinaAPI): An instance of a DinaAPI subclass to interact with the API
        field (str): The field to filter by
        value (str): The value to filter by
        include_param (str): The relationships to include in the response, formatted as a comma-separated string
        step_size (int, optional): The number of records to fetch in each API call. Defaults to 500.

    Returns:
        data: A list of records matching the filter criteria
    """
    step = step_size
    offset = 0
    data = []

    params = {
        f"filter[{field}][EQ]": value,
        "include": include_param,
        "sort": "-createdOn"
    }

    while True:
        params["page[limit]"] = step
        params["page[offset]"] = offset
        record_list = api.get_entity_by_param(params)
        batch = record_list.json()["data"]
        data.extend(batch)
        offset += step

        # Check if we got less than step (last page)
        if len(batch) < step:
            break
        
    return data

def get_dina_records_by_params(api,params,step_size=150):
    """Fetches records from the Dina API filtered by the provided parameters.

    Args:
        api (DinaAPI): An instance of a DinaAPI subclass to interact with the API
        params (dict): The parameters for filtering and sorting the records
        step_size (int, optional): The number of records to fetch in each API call. Defaults to 150.

    Returns:
        data: A list of records matching the filter criteria
    """
    step = step_size
    offset = 0
    data = []
    while True:
        params["sort"] = "-createdOn"
        params["page[limit]"] = step
        params["page[offset]"] = offset
        record_list = api.get_entity_by_param(params)
        batch = record_list.json()["data"]
        data.extend(batch)
        offset += step

        # Check if we got less than step (last page)
        if len(batch) < step:
            break
        
    return data

def prepare_bulk_payload(entities: list, include_fields: list = None, include_relationships: list = None) -> dict:
    """Prepares a minimal bulk payload from a list of entities.
    
    Args:
        entities (list): List of entity objects to be included in bulk operation
        include_fields (list, optional): List of attribute fields to include in payload.
            If None, includes all fields.
            
    Returns:
        dict: A bulk payload formatted for the API
    """
    bulk_data = []
    
    for entity in entities:
        # Create minimal payload structure
        minimal = {
            "id": entity.get_id(),
            "type": entity.get_type(),
            "attributes": {}
        }
        
        # Only include specified fields
        if include_fields:
            for field in include_fields:
                if field in entity.attributes:
                    minimal["attributes"][field] = entity.get_attributes().get(field)
        if include_relationships:
                minimal["relationships"] = {}
                for relationship in include_relationships:
                    if relationship in entity.relationships:
                        minimal["relationships"][relationship] = entity.get_relationships().get(relationship)
            
        bulk_data.append(minimal)
        
    return {"data": bulk_data}