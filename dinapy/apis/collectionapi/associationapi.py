from .collectionapi import CollectionModuleApi


class AssociationAPI(CollectionModuleApi):
    """Client for the collection-api/association endpoint."""

    def __init__(self, base_url: str = None) -> None:
        super().__init__(base_url)
        self.base_url += "association"

    def get_associations(self, include: list[str] = None, **filter_params):
        """Retrieve all associations, with optional filters and includes.

        Args:
            include: List of relationships to include (e.g. ["associatedSample", "sample"]).
            **filter_params: Additional filter parameters, e.g.
                filter_params={"filter[sample.uuid][EQ]": "<uuid>"}

        Returns:
            Response: the API response.

        Example::

            api = AssociationAPI()
            api.get_associations(
                include=["associatedSample", "sample"],
                **{"filter[sample.uuid][EQ]": "019df927-..."}
            )
        """
        params = dict(filter_params)
        if include:
            params["include"] = ",".join(include)
        return self.get_entity_by_param(params or None)

    def get_associations_by_sample_uuid(self, sample_uuid: str, include: list[str] = None):
        """Retrieve all associations for a given sample UUID.

        Args:
            sample_uuid: UUID of the sample to filter by.
            include: List of relationships to include (e.g. ["associatedSample", "sample"]).

        Returns:
            Response: the API response.
        """
        params = {"filter[sample.uuid][EQ]": sample_uuid}
        if include:
            params["include"] = ",".join(include)
        return self.get_entity_by_param(params)
