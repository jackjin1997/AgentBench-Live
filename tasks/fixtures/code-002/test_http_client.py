"""Tests for HTTP client retry logic."""

import time
from unittest.mock import MagicMock, patch

import requests
import pytest

from http_client import ApiClient


@pytest.fixture
def client():
    return ApiClient("https://api.example.com", max_retries=3, timeout=10)


def _mock_response(status_code: int) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(
            response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


class TestRetryLogic:
    @patch("http_client.requests.request")
    def test_success_no_retry(self, mock_req, client):
        mock_req.return_value = _mock_response(200)
        resp = client.get("/data")
        assert resp.status_code == 200
        assert mock_req.call_count == 1

    @patch("http_client.requests.request")
    def test_retry_on_500(self, mock_req, client):
        mock_req.side_effect = [
            _mock_response(500),
            _mock_response(500),
            _mock_response(200),
        ]
        # Patch sleep to speed up test
        with patch("http_client.time.sleep"):
            resp = client.get("/data")
        assert resp.status_code == 200
        assert mock_req.call_count == 3

    @patch("http_client.requests.request")
    def test_retry_on_429(self, mock_req, client):
        mock_req.side_effect = [
            _mock_response(429),
            _mock_response(200),
        ]
        with patch("http_client.time.sleep"):
            resp = client.get("/data")
        assert resp.status_code == 200
        assert mock_req.call_count == 2

    @patch("http_client.requests.request")
    def test_retry_on_502(self, mock_req, client):
        mock_req.side_effect = [
            _mock_response(502),
            _mock_response(200),
        ]
        with patch("http_client.time.sleep"):
            resp = client.get("/data")
        assert resp.status_code == 200

    @patch("http_client.requests.request")
    def test_retry_on_503(self, mock_req, client):
        mock_req.side_effect = [
            _mock_response(503),
            _mock_response(200),
        ]
        with patch("http_client.time.sleep"):
            resp = client.get("/data")
        assert resp.status_code == 200

    @patch("http_client.requests.request")
    def test_no_retry_on_404(self, mock_req, client):
        mock_req.return_value = _mock_response(404)
        with pytest.raises(requests.HTTPError):
            client.get("/missing")
        assert mock_req.call_count == 1

    @patch("http_client.requests.request")
    def test_exhausted_retries_raises(self, mock_req, client):
        mock_req.side_effect = [
            _mock_response(500),
            _mock_response(500),
            _mock_response(500),
            _mock_response(500),  # max_retries=3 means 1 initial + 3 retries = 4 attempts
        ]
        with patch("http_client.time.sleep"):
            with pytest.raises(requests.HTTPError):
                client.get("/failing")

    @patch("http_client.requests.request")
    def test_exponential_backoff_delays(self, mock_req, client):
        mock_req.side_effect = [
            _mock_response(500),
            _mock_response(500),
            _mock_response(200),
        ]
        delays = []
        with patch("http_client.time.sleep", side_effect=lambda d: delays.append(d)):
            client.get("/data")
        assert len(delays) == 2
        # First delay ~1s (base), second ~2s (doubled), both with jitter up to 0.5
        assert 0.5 <= delays[0] <= 1.5
        assert 1.5 <= delays[1] <= 2.5
