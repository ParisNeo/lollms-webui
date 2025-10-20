import requests
from typing import Optional, Any, List, Dict
from enum import Enum
from lollms.databases.datalakes.lollms_database import LollmsDatabase

class SearchMode(str, Enum):
    naive = "naive"
    local = "local"
    global_ = "global"
    hybrid = "hybrid"

class LollmsLightRag(LollmsDatabase):
    def __init__(self, server_url: str, name: str, description: Optional[str] = None):
        """
        Initialize LightRAG client
        
        Args:
            server_url (str): Full URL of the LightRAG server
            name (str): Name of the database
            description (Optional[str]): Description of the database
        """
        super().__init__(name, description)
        self.server_url = server_url.rstrip('/')
        
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            response = requests.post(
                f"{self.server_url}/documents/text",
                json={"text": content}
            )
            response.raise_for_status()
            self.update_last_modified()
            return True
        except requests.RequestException:
            return False
            
    def query(self, text: str, **kwargs) -> str:
        try:
            response = requests.post(
                f"{self.server_url}/query",
                json={
                    "query": text,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to query: {str(e)}")
            
    def clear(self) -> bool:
        try:
            response = requests.delete(f"{self.server_url}/documents")
            response.raise_for_status()
            self.update_last_modified()
            return True
        except requests.RequestException:
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        health_info = self.health_check()
        return {
            "indexed_files": health_info.get("indexed_files", 0),
            "configuration": health_info.get("configuration", {})
        }
            
    def health_check(self) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.server_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to check health: {str(e)}")
            
    def backup(self, path: str) -> bool:
        # Implementation would depend on LightRAG backup capabilities
        raise NotImplementedError("Backup not implemented for LightRAG")
        
    def restore(self, path: str) -> bool:
        # Implementation would depend on LightRAG restore capabilities
        raise NotImplementedError("Restore not implemented for LightRAG")