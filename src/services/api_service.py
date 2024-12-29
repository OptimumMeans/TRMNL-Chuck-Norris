from datetime import datetime, UTC
import logging
from typing import Optional, Dict, Any
import requests
from ..config import Config

logger = logging.getLogger(__name__)

class APIService:
    
    CHUCK_NORRIS_API = "https://api.chucknorris.io/jokes/random"
    
    def __init__(self):
        self.last_update = None
        self._cached_data = None
        self._cache_timestamp = None
    
    def get_data(self) -> Optional[Dict[str, Any]]:
        '''Get data from the Chuck Norris API.'''
        try:
            if self._is_cache_valid():
                return self._cached_data
            
            data = self._fetch_data()
            
            self._update_cache(data)
            self.last_update = datetime.now(UTC)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching Chuck Norris fact: {str(e)}")
            return None
    
    def _fetch_data(self) -> Dict[str, Any]:
        '''Fetch a random Chuck Norris fact.'''
        response = requests.get(self.CHUCK_NORRIS_API)
        response.raise_for_status()
        
        joke_data = response.json()
        
        return {
            'timestamp': datetime.now(UTC).isoformat(),
            'status': 'ok',
            'fact': joke_data['value'],
            'icon_url': joke_data['icon_url'],
            'fact_id': joke_data['id']
        }
    
    def _update_cache(self, data: Dict[str, Any]) -> None:
        self._cached_data = data
        self._cache_timestamp = datetime.now(UTC)
    
    def _is_cache_valid(self) -> bool:
        if not self._cache_timestamp:
            return False
            
        cache_age = (datetime.now(UTC) - self._cache_timestamp).total_seconds()
        return cache_age < Config.CACHE_TIMEOUT