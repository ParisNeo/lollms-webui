from abc import ABC, abstractmethod
from typing import Optional, Any, List, Dict
from datetime import datetime

class LollmsDatabase(ABC):
    """
    Base class for all Lollms database implementations
    """
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize the database
        
        Args:
            name (str): Name of the database
            description (Optional[str]): Description of the database
        """
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.last_modified = datetime.now()
        
    @abstractmethod
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a document to the database
        
        Args:
            content (str): The content to add
            metadata (Optional[Dict[str, Any]]): Additional metadata about the document
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def query(self, text: str, **kwargs) -> str:
        """
        Query the database
        
        Args:
            text (str): Query text
            **kwargs: Additional query parameters
            
        Returns:
            str: Query response
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all documents from the database
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Check database health
        
        Returns:
            Dict[str, Any]: Health status information
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get database information
        
        Returns:
            Dict[str, Any]: Database information
        """
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "type": self.__class__.__name__
        }
    
    @abstractmethod
    def backup(self, path: str) -> bool:
        """
        Backup the database
        
        Args:
            path (str): Backup destination path
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def restore(self, path: str) -> bool:
        """
        Restore the database from backup
        
        Args:
            path (str): Backup source path
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def update_last_modified(self):
        """Update the last modified timestamp"""
        self.last_modified = datetime.now()