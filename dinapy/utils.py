def get_dina_records_by_field(api,field,value):
    collected_ids = []

    step = 500
    counter = 1
    data = []
    RECORD_COUNT = api.get_entity_by_field(field,value).json()["meta"]["totalResourceCount"]
    #print (RECORD_COUNT)
    while len(collected_ids) < RECORD_COUNT:
        params = {"filter[rsql]": f'{field}=={value}', "sort": "-createdOn","page[limit]": step, "page[offset]": (counter-1)*step}
        material_sample_list = api.get_entity_by_param(params)
        for material_sample in material_sample_list.json()["data"]:
            material_sample_id = material_sample["id"]
            if(material_sample_id not in collected_ids):
                #print("New record with id: ", collecting_event_id)
                data.append(material_sample)
                collected_ids.append(material_sample_id)
        counter +=1
        
    return data

