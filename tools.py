from datetime import datetime

import requests


class RequestsTools:
    hostname = "https://api-204c5-8080.app.zerops.io/api/public/"
    url = 'ipv4-range'

    def client_get(self, range_id: str = None):
        """Requests client for GET method"""

        try:
            if range_id:
                r = requests.get(url=f"{self.hostname}{self.url}/{range_id}")
            else:
                r = requests.get(url=f"{self.hostname}{self.url}")
            return r
        except Exception as e:
            raise e

    def client_post(self, data=None):
        """Requests client for POST method"""

        try:
            r = requests.post(f"{self.hostname}{self.url}", json=data if data else None)
            return r

        except Exception as e:
            raise e

    def client_delete(self, range_id: str = None):
        """Requests client for DELETE method"""

        try:
            r = requests.delete(f"{self.hostname}{self.url}/{range_id}")
            return r
        except Exception as e:
            raise e

    def client_put(self, data, range_id: str = None):
        """Requests client for PATCH method"""
        try:
            if range_id:
                r = requests.put(f"{self.hostname}{self.url}/{range_id}", json=data)
            else:
                r = requests.put(f"{self.hostname}{self.url}", json=data)
            return r
        except Exception as e:
            raise e

    def clean_range(self, range_id: str = None):
        post_response = self.client_delete(range_id)

        return post_response


class Ignored(object):
    def __repr__(self):
        return 'Ignored()'

    def __eq__(self, other):
        return True
