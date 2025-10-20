"""Class that extracts common functionality for Molecular Analysis Result entity"""  

from .seqdbapi import SeqDBApi	

class MolecularAnalysisResultApi(SeqDBApi):

  def __init__(self, base_url: str = None) -> None:
    """
    Parameters:
        config_path (str, optional): Path to a config file (default: None).
        base_url (str, optional): URL to the URL to perform the API requests against. If not
        provided then local deployment URL is used. Should end with a forward slash.
    """
    super().__init__( base_url)
    self.base_url += "molecular-analysis-result"

  def get_relationship_entity(self, entity_id, endpoint):
    entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
    new_request_url = self.base_url + '/'+ str(entity_id) + f'/relationships/{endpoint}'
    print(new_request_url)
    jsn_resp = self.get_req_dina(request_url = new_request_url)
    return jsn_resp if jsn_resp else ''   
  
  def get_entity_with_param(self, entity_id,param):
    entity_id = str(entity_id) if isinstance(entity_id, int) else entity_id
    new_request_url = self.base_url + '/' + entity_id
    jsn_resp = self.get_req_dina(new_request_url, params = param)
    return jsn_resp if jsn_resp else '' 
  
  def get_entity_by_param(self, param=None):
    print(self.base_url,param)
    jsn_resp = self.get_req_dina(self.base_url, params = param)
    return jsn_resp if jsn_resp else ''