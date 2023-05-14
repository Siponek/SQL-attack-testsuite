from typing import Any
import pytest
import requests
from bs4 import BeautifulSoup
from pathlib import Path


list_of_files = list(Path("./pages").rglob("*.php"))
# List of endpoints to test
endpoints = [file.name for file in list_of_files]
for endpoint in endpoints:
    print(endpoint)
print("Total endpoints: ", len(endpoints))
# List of payloads to test
payloads = [
    "' UNION SELECT 1, VERSION() -- ",
    "' UNION SELECT 1, USER() -- ",
    # ... you can add more payloads here ...
]

# Expected values in response for corresponding payloads
expected_values = [
    '5.7.42',  # Assuming MySQL version is 5.7.32
    'root@localhost',  # Assuming MySQL user is root@localhost
    # ... you can add more expected values here ...
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}

@pytest.fixture(scope="module")
def session():
    return requests.Session()

@pytest.mark.parametrize("endpoint, payload, expected_value", [(e, p, v) for e in endpoints for p, v in zip(payloads, expected_values)])
def test_sql_injection(session: requests.Session, endpoint: Any, payload: Any, expected_value: Any):
    url = f"http://localhost:8000/{endpoint}?search={payload}"
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print the reposnse text
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    
    # Check if the payload was successful
    print(soup.text)
    assert expected_value not in soup.text, f"Payload '{payload}' did not work"
