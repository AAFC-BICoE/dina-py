from ..dinaapi import DinaAPI


class PersonAPI(DinaAPI):
    def __init__(self, config_file: None) -> None:
        super.__init__(config_file)
        self.base_url += "agent-api/person/"

    def find(self, uuid: str):
        full_url = self.base_url + uuid

        return self.get_req_dina(full_url)
