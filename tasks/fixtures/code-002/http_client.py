"""Simple HTTP client without retry logic."""

import requests


class ApiClient:
    """A minimal HTTP client."""

    def __init__(self, base_url: str, max_retries: int = 3, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an HTTP request. Currently no retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: URL path (appended to base_url)
            **kwargs: Passed to requests.request()

        Returns:
            requests.Response object

        Raises:
            requests.HTTPError: On 4xx/5xx responses after retries exhausted.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)
