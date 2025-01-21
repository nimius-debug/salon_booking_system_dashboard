# api/client.py
import requests
from config.settings import Settings

class APIClient:
    def __init__(self, token):
        self.token = token
        self.headers = {"Access-Token": token}
    
    def get_customers(self, search="", search_type="contains", search_field="all",
                     orderby="first_name_last_name", order="asc", per_page=-1, page=-1):
        params = {
            "search": search,
            "search_type": search_type,
            "search_field": search_field,
            "orderby": orderby,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(
            Settings.CUSTOMERS_URL,
            headers=self.headers,
            params=params
        )
        return response