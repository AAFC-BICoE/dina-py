def get_field_from_config(dina_api_config: dict, api: str, resource: str, property: str, field: str):
    """
    dina_api_config: Parsed dictionary of constants from yml
    
    api: API field in dina_api_config. Ex: objectstore-api
    
    resource: Type of resource from API. Ex: metadata
    
    property: Property of resource. One of: relationships, attributes
    
    field: Field of resource. Ex: acMetadataCreator
    """
    return (
                dina_api_config.get(api)
                .get(resource)
                .get(property)
                .get(field)
            )