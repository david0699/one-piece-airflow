import pytest
import requests
from unittest.mock import Mock, patch
from api_utils.api_utils import fetch_data_from_api

def test_fetch_data_success():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"key": "value"}

    with patch("requests.get", return_value=mock_response):
        result = fetch_data_from_api("https://fake.api/data")

    assert result == {"key": "value"}

def test_fetch_data_http_error():
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 error")

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_data_from_api("https://fake.api/data")

def test_fetch_data_request_exception():
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("boom")):
        with pytest.raises(requests.exceptions.ConnectionError):
            fetch_data_from_api("https://fake.api/data")