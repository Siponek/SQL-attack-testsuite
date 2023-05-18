import pytest
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import yaml
import colorama
from colorama import Fore
from enum import Enum

colorama.init(autoreset=True)

BASE_URL = "http://localhost:8000/"
PHP_FILES_PATH = "./pages"
CONFIG_FILE_PATH = "attack_payloads.yaml"


class RequestType(Enum):
    GET = 1
    POST = 2


php_files: list = list(Path(PHP_FILES_PATH).rglob("*.php"))
endpoints: list = [file.name for file in php_files]

with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

headers: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}

QUERY_PARAMS: dict = {
    "find": {"type": "search", "request_type": RequestType.GET},
    "login": {"type": ["user", "pass"], "request_type": RequestType.POST},
    "search_by_price": {"type": "max", "request_type": RequestType.GET},
    "search": {"type": "search", "request_type": RequestType.GET},
}


def get_route_based_info(dictionary: dict, url: str) -> dict:
    for key in dictionary:
        if key in url:
            return dictionary[key]
    raise ValueError(
        f"No testing type found for given route {Fore.LIGHTRED_EX + url + Fore.RESET}. Make sure that the page has either search, search_by_price, login or find in the name."
    )


@pytest.fixture(scope="module")
def session() -> requests.Session:
    return requests.Session()


@pytest.mark.parametrize(
    "endpoint,test_name, payload_dict, query_info, test_type",
    [
        (
            e,
            test_name,
            attack_dict,
            get_route_based_info(dictionary=QUERY_PARAMS, url=e),
            t,
        )
        for e in endpoints
        for t in ["functional_test", "error_based", "union"]
        for test_name, attack_dict in get_route_based_info(
            dictionary=config, url=e
        )
        .get(t)
        .items()
    ],
)
def test_sql_inject(
    session: requests.Session,
    endpoint: str,
    test_name: str,
    payload_dict: dict,
    query_info: dict,
    test_type: str,
) -> None:
    """The function that tests the SQL injection. Takes into account the type of the request and the type of the test [Functional test or Penetration Union / Error-based].

    Args:
        session (requests.Session): _description_
        endpoint (str): _description_
        test_name (str): _description_
        payload_dict (dict): _description_
        query_info (dict): _description_
        test_type (str): _description_
    """
    url_to_test: str
    response: requests.Response
    if query_info["request_type"] == RequestType.POST:
        url_to_test = f"{BASE_URL}{endpoint}"
        response = session.post(
            url_to_test,
            data=dict(zip(query_info["type"], payload_dict.get("payload"))),
        )
    else:
        url_to_test = f"{BASE_URL}{endpoint}?{query_info['type']}={payload_dict.get('payload')}"
        response = session.get(url_to_test, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"

    # if test_type in ["functional_test", "error_based"]:
    if test_type in ["union", "error_based"]:
        assert (
            payload_dict["expected"] not in soup.text
        ), f"{Fore.LIGHTCYAN_EX}{endpoint}/{test_name} failed"
    else:
        assert (
            payload_dict["expected"] in soup.text
        ), f"{Fore.LIGHTCYAN_EX}{endpoint}/{test_name} failed"
