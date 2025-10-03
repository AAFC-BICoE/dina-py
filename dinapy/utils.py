def get_dina_records_by_field(api,field,value):
    collected_ids = []

    step = 500
    counter = 1
    data = []
    RECORD_COUNT = api.get_entity_by_field(field,value).json()["meta"]["totalResourceCount"]
    #print (RECORD_COUNT)
    while len(collected_ids) < RECORD_COUNT:
        params = {"filter[rsql]": f'{field}=={value}', "sort": "-createdOn","page[limit]": step, "page[offset]": (counter-1)*step}
        record_list = api.get_entity_by_param(params)
        for record in record_list.json()["data"]:
            record_id = record["id"]
            if(record_id not in collected_ids):
                #print("New record with id: ", collecting_event_id)
                data.append(record)
                collected_ids.append(record_id)
        counter +=1
        
    return data

def get_dina_records_by_field_with_include(api,field,value,include_param):
    collected_ids = []

    step = 500
    counter = 1
    data = []
    RECORD_COUNT = api.get_entity_by_field(field,value).json()["meta"]["totalResourceCount"]
    while len(collected_ids) < RECORD_COUNT:
        print(len(collected_ids))
        params = {"filter[rsql]": f'{field}=={value}', "include": ','.join(include_param) if isinstance(include_param, list) else include_param, "sort": "-createdOn","page[limit]": step, "page[offset]": (counter-1)*step}
        record_list = api.get_entity_by_param(params)
        for record in record_list.json()["data"]:
            record_id = record["id"]
            if(record_id not in collected_ids):
                #print("New record with id: ", collecting_event_id)
                data.append(record)
                collected_ids.append(record_id)
        counter +=1
    return data

def get_dina_records_by_params(api,params):
    collected_ids = []

    step = 150
    counter = 1
    offset = 0
    data = []
    RECORD_COUNT = api.get_entity_by_param(params).json()["meta"]["totalResourceCount"]
    while len(collected_ids) < RECORD_COUNT:
        print(len(collected_ids))
        params = {"sort": "-createdOn","page[limit]": step, "page[offset]": offset}
        record_list = api.get_entity_by_param(params)
        for record in record_list.json()["data"]:
            record_id = record["id"]
            if(record_id not in collected_ids):
                #print("New record with id: ", collecting_event_id)
                data.append(record)
                collected_ids.append(record_id)
        counter +=1
        offset = step + counter*2
        
    return data

def prepare_bulk_payload(entities: list, include_fields: list = None) -> dict:
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
        else:
            minimal["attributes"] = entity.get_attributes()
            
        bulk_data.append(minimal)
        
    return {"data": bulk_data}