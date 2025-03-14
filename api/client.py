# api/client.py
import streamlit as st
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from config.settings import Settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API exceptions"""
    pass

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    pass

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    pass

class RateLimitExceeded(APIError):
    """Raised when rate limit is exceeded"""
    pass

class APIClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Access-Token": self.token}
        self.base_url = Settings.API_BASE_URL

    def _handle_response(self, response: requests.Response) -> List[Dict[str, Any]]:
        """Handle API response and raise appropriate errors"""
        if response.status_code == 200:
            return response.json().get("items", [])
        
        error_msg = f"API Request Failed: {response.status_code} - {response.text}"
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired access token")
        elif response.status_code == 404:
            raise NotFoundError("Requested resource not found")
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 60)
            raise RateLimitExceeded(f"Rate limit exceeded. Retry after {retry_after} seconds")
        elif 500 <= response.status_code < 600:
            raise APIError(f"Server error: {response.text}")
        else:
            raise APIError(error_msg)

    @classmethod
    @st.cache_resource
    def create_client(cls, _token: str) -> "APIClient":
        """Create and cache a single instance of APIClient"""
        return cls(_token)

    @st.cache_data(ttl=3600, hash_funcs={"api.client.APIClient": lambda _: 0})
    def get_customers(
        _self,
        search: str = "",
        search_type: str = "contains",
        search_field: str = "all",
        orderby: str = "first_name_last_name",
        order: str = "asc",
        per_page: int = -1,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get customers with filtering and sorting options
        
        Args:
            search: Search string
            search_type: Search type (start_with, end_with, contains)
            search_field: Search field (all, first_name, last_name, phone)
            orderby: Order by field
            order: Sort order (asc/desc)
            per_page: Items per page
            page: Page number
            
        Returns:
            List of customer dictionaries
        """
        params = {
            "search": search,
            "search_type": search_type,
            "search_field": search_field,
            "orderby": orderby,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        
        try:
            response = requests.get(
                f"{_self.base_url}/customers",
                headers=_self.headers,
                params=params,
                timeout=10
            )
            return _self._handle_response(response)
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.error(f"Network error: {str(e)}")
            return []
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []

    @st.cache_data(ttl=600, hash_funcs={"api.client.APIClient": lambda _: 0})
    def get_bookings(
        _self,
        start_date: str,
        end_date: str,
        shop: Optional[int] = None,
        services: Optional[List[int]] = None,
        customers: Optional[List[int]] = None,
        orderby: str = "date_time",
        order: str = "desc",
        per_page: int = -1,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get bookings within a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            shop: Shop ID filter
            services: List of service IDs filter
            customers: List of customer IDs filter
            orderby: Order by field
            order: Sort order (asc/desc)
            per_page: Items per page
            page: Page number
            
        Returns:
            List of booking dictionaries
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "orderby": orderby,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        
        if shop: params["shop"] = shop
        if services: params["services"] = services
        if customers: params["customers"] = customers
        
        try:
            response = requests.get(
                f"{_self.base_url}/bookings",
                headers=_self.headers,
                params=params,
                timeout=10
            )
            return _self._handle_response(response)
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.error(f"Network error: {str(e)}")
            return []
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []
   
    ################GET Booking Stats#########################
    @st.cache_data(ttl=3600, hash_funcs={"api.client.APIClient": lambda _: 0})
    def get_booking_stats(
        _self,
        group_by: str = "month",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        shop: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get booking statistics grouped by time period
        
        Args:
            group_by: Grouping period (day, month, year)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            shop: Shop ID filter
            
        Returns:
            List of statistics dictionaries
        """
        params = {
            "group_by": group_by,
            "start_date": start_date or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": end_date or datetime.now().strftime("%Y-%m-%d")
        }
        if shop: params["shop"] = shop
        
        try:
            response = requests.get(
                f"{_self.base_url}/bookings/stats",
                headers=_self.headers,
                params=params,
                timeout=10
            )
            return _self._handle_response(response)
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.error(f"Network error: {str(e)}")
            return []
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []

    @st.cache_data(ttl=300, hash_funcs={"api.client.APIClient": lambda _: 0})
    def get_upcoming_bookings(
        _self,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get upcoming confirmed bookings
        
        Args:
            hours: Number of hours to look ahead
            
        Returns:
            List of upcoming booking dictionaries
        """
        try:
            response = requests.get(
                f"{_self.base_url}/bookings/upcoming",
                headers=_self.headers,
                params={"hours": hours},
                timeout=10
            )
            return _self._handle_response(response)
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.error(f"Network error: {str(e)}")
            return []
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return []

    @st.cache_data(ttl=60, hash_funcs={"api.client.APIClient": lambda _: 0})
    def get_api_health(_self) -> Tuple[bool, str]:
        """Check API health status
        
        Returns:
            Tuple (health status, status message)
        """
        try:
            response = requests.get(
                f"{_self.base_url}/health",
                headers=_self.headers,
                timeout=5
            )
            if response.status_code == 200:
                return True, "API is healthy"
            return False, f"API health check failed: {response.text}"
        except Exception as e:
            return False, f"Health check failed: {str(e)}"
        

    st.cache_data(ttl=3600, hash_funcs={"api.client.APIClient": lambda _: 0})
    def get_services(_self) -> Dict[int, str]:
        """Get service ID to name mapping"""
        try:
            response = requests.get(
                f"{_self.base_url}/services",
                headers=_self.headers,
                params={"per_page": -1},
                timeout=10
            )
            if response.status_code == 200:
                # Parse the response structure correctly
                response_data = response.json()
                services_list = response_data.get("items", [])
                return {svc["id"]: svc["name"] for svc in services_list}
            return {}
        except Exception as e:
            logger.error(f"Error fetching services: {str(e)}")
            return {}
    
    def update_booking(self, booking_id: str, data: Dict[str, Any]) -> bool:
        """Update a booking
        
        Args:
            booking_id: Booking ID to update
            data: Updated booking data
            
        Returns:
            bool: Success status
        """
        try:
            response = requests.put(
                f"{self.base_url}/bookings/{booking_id}",
                headers=self.headers,
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating booking: {str(e)}")
            return False