import requests


def test_requests_installed():
    assert requests.__version__ == "2.32.3"