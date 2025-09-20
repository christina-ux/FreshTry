import aiohttp
import asyncio
import requests
import time
import logging
from functools import lru_cache
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger("api_client")

class APIClient:
    """
    Unified API client for handling connections to external services
    with connection pooling, retries, and caching.
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30, max_retries: int = 3, 
                 backoff_factor: float = 0.5, pool_connections: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.pool_connections = pool_connections
        self._session = None
        self._async_session = None
    
    @property
    def session(self):
        """Lazy initialization of connection-pooled session"""
        if self._session is None:
            self._session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=self.pool_connections,
                pool_maxsize=self.pool_connections,
                max_retries=self.max_retries,
                pool_block=False
            )
            self._session.mount('http://', adapter)
            self._session.mount('https://', adapter)
        return self._session
    
    async def get_async_session(self):
        """Lazy initialization of async session"""
        if self._async_session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._async_session = aiohttp.ClientSession(timeout=timeout)
        return self._async_session
    
    async def close_async_session(self):
        """Close async session"""
        if self._async_session is not None:
            await self._async_session.close()
            self._async_session = None
    
    def close(self):
        """Close the session"""
        if self._session is not None:
            self._session.close()
            self._session = None
    
    def _construct_url(self, endpoint: str) -> str:
        """Construct full URL from endpoint"""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        if self.base_url is None:
            raise ValueError("Base URL is required when using relative endpoints")
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    @lru_cache(maxsize=128)
    def _get_cached(self, url: str, params_key: str) -> Dict[str, Any]:
        """Cached GET request - key includes the params to ensure uniqueness"""
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, use_cache: bool = False) -> Union[Dict[str, Any], List, str]:
        """Send GET request with retries and optional caching"""
        url = self._construct_url(endpoint)
        
        if use_cache and params is None:
            try:
                return self._get_cached(url, "")
            except Exception as e:
                logger.warning(f"Cache miss for {url}: {e}")
        
        if use_cache and params is not None:
            params_key = str(sorted(params.items()))
            try:
                return self._get_cached(url, params_key)
            except Exception as e:
                logger.warning(f"Cache miss for {url} with params {params_key}: {e}")
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                
                # Try to parse as JSON, fall back to text
                try:
                    return response.json()
                except ValueError:
                    return response.text
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential backoff
                sleep_time = self.backoff_factor * (2 ** attempt)
                logger.warning(f"Request to {url} failed, retrying in {sleep_time}s: {e}")
                time.sleep(sleep_time)
    
    async def get_async(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None) -> Union[Dict[str, Any], List, str]:
        """Send async GET request with retries"""
        url = self._construct_url(endpoint)
        session = await self.get_async_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    
                    # Try to parse as JSON, fall back to text
                    try:
                        return await response.json()
                    except ValueError:
                        return await response.text()
                        
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential backoff
                sleep_time = self.backoff_factor * (2 ** attempt)
                logger.warning(f"Async request to {url} failed, retrying in {sleep_time}s: {e}")
                await asyncio.sleep(sleep_time)
    
    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, data: Any = None,
             params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Union[Dict[str, Any], List, str]:
        """Send POST request with retries"""
        url = self._construct_url(endpoint)
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(url, json=json, data=data, params=params, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                
                # Try to parse as JSON, fall back to text
                try:
                    return response.json()
                except ValueError:
                    return response.text
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential backoff
                sleep_time = self.backoff_factor * (2 ** attempt)
                logger.warning(f"Request to {url} failed, retrying in {sleep_time}s: {e}")
                time.sleep(sleep_time)
    
    async def post_async(self, endpoint: str, json: Optional[Dict[str, Any]] = None, data: Any = None,
                        params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Union[Dict[str, Any], List, str]:
        """Send async POST request with retries"""
        url = self._construct_url(endpoint)
        session = await self.get_async_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.post(url, json=json, data=data, params=params, headers=headers) as response:
                    response.raise_for_status()
                    
                    # Try to parse as JSON, fall back to text
                    try:
                        return await response.json()
                    except ValueError:
                        return await response.text()
                        
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise
                
                # Exponential backoff
                sleep_time = self.backoff_factor * (2 ** attempt)
                logger.warning(f"Async request to {url} failed, retrying in {sleep_time}s: {e}")
                await asyncio.sleep(sleep_time)
    
    # Implement other HTTP methods (put, delete, etc.) following the same pattern...
    
    def health_check(self, endpoint: str = "health") -> bool:
        """Check if the API is healthy"""
        try:
            response = self.get(endpoint, timeout=5)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False