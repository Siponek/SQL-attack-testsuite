# Python version: 3.11.0
from typing import Any
import pytest
import requests
from bs4 import BeautifulSoup
from pathlib import Path


list_of_files = list(Path("./pages").rglob("*.php"))
# List of endpoints to test
endpoints = [file.name for file in list_of_files]
for endpoint in endpoints:
    print(endpoint, end=" ")
print("Total endpoints: ", len(endpoints))


# List of payloads to test
payloads = [
    "' UNION SELECT 1, VERSION() -- ",
    "' UNION SELECT 1, USER() -- ",
    "' UNION SELECT NULL, NULL, name, price FROM items; --",
]

# Expected values in response for corresponding payloads
expected_values = [
    # Assuming MySQL version is 5.7.32
    "5.7.42",
    # Assuming MySQL user is root@localhost
    "root@localhost",
    # ... you can add more expected values here ...
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}

QUERY_PARAMS: dict = {
    "find": {
        "type": "search",
    },
    "login": {
        "type": ["user", "pass"],
    },
    "search_by_price": {
        "type": "max",
    },
    "search": {
        "type": "search",
    },
}


# def get_substring_in_keys(dictionary: dict, url: str) -> list:
#     """Find a substring in keys of an dictionary and return the first occurence.
#     WARNING: This function returns the first occurence so it depends on order of files.

#     Args:
#         dictionary (dict): Dictionary to search in.
#         url (str): String to search for.

#     Returns:
#         dict: Return dictionary with matching keys.
#     """
#     tmp_dict: dict = {
#         key: dictionary.get(key) for key in dictionary if key in url
#     }
#     # python 3.7 python dicts are ordered by default
#     first_key: str = next(iter(tmp_dict))
#     return tmp_dict.get(first_key)


def get_query_type(dictionary: dict, url: str) -> list:
    for key in dictionary:
        if key in url:
            return dictionary[key]["type"]
    raise ValueError(
        f"No testing type found for given route {url}. Make sure that the page has either exec, echo, find, or ping in the name."
    )


# find.php find2.php find3.php login.php login2.php login3.php search.php search_by_price.php search_by_price2.php search_by_price3.php search_by_price4.php Total endpoints:  11
# Testing query types
# Qu
# ery types:  ['search', 'search', 'search', ['user', 'pass'], ['user', 'pass'], ['user', 'pass'], 'search', 'max', 'max', 'max', 'max']


@pytest.fixture(scope="module")
def session():
    return requests.Session()


@pytest.mark.parametrize(
    "endpoint, payload, expected_value, query_type",
    [
        (e, p, v, get_query_type(dictionary=QUERY_PARAMS, url=e))
        for e in endpoints
        for p, v in zip(payloads, expected_values)
    ],
)
def test_sql_injection(
    session: requests.Session,
    endpoint: str,
    payload: str,
    expected_value: str,
    query_type: str,
):
    url: str
    response: requests.Response
    if type(query_type) == list:
        url = f"http://localhost:8000/{endpoint}"
        response = session.post(
            url,
            headers=headers,
            data={query_type[0]: payload, query_type[1]: payload},
        )
    else:
        url = f"http://localhost:8000/{endpoint}?{query_type}={payload}"
        response = session.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"

    # Check if the payload was successful
    print(soup.text)
    assert expected_value not in soup.text, f"Payload '{payload}' did not work"
