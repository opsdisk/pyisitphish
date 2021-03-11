#!/usr/bin/env python

# Standard Python libraries.
import argparse
import json
import sys

# Third party Python libraries.
import requests
from requests_toolbelt.utils import dump

# Custom Python libraries.


__version__ = "1.0.0"


def debug_requests_response(response):
    """Provide debug print info for a requests response object."""

    data = dump.dump_all(response)
    print(data.decode("utf-8"))


class IsItPhishClient:
    def __init__(self, secrets_dict={}, secrets_file_location="./secrets.json", **kwargs):
        """Initialize a isitphish client.  The secrets dict should look like:

            secrets_dict = {
                "isitphish": {
                    "host": host,
                    "token": token,
                }
            }
        """

        if secrets_dict:
            secrets = secrets_dict

        elif secrets_file_location:
            try:
                with open(secrets_file_location) as config_file:
                    secrets = json.loads(config_file.read())
            except OSError:
                print(f"Error: {secrets_file_location} does not exist.  Exiting...")
                sys.exit(1)

        else:
            print(
                "Error initializing an IsItPhish client.  Provide a secrets dictionary or secrets file location. "
                "Exiting..."
            )
            sys.exit(1)

        # Ensure key/values exist in secrets.
        try:
            self.host = secrets["isitphish"]["host"]
            self.token = secrets["isitphish"]["token"]

        except KeyError:
            print(f"Error reading key-values in 'secrets' variable.  Exiting...")
            sys.exit(1)

        # Build BASE_URL.
        self.BASE_URL = f"https://{self.host}"

        # Minimize Python requests (and the underlying urllib3 library) logging level.
        # logging.getLogger("requests").setLevel(logging.INFO)
        # logging.getLogger("urllib3").setLevel(logging.INFO)

        # Extract User-Agent, default to "isitphish-api-client-v{__version__}".
        self.user_agent = kwargs.get("user_agent", f"isitphish-api-client-v{__version__}")

        # fmt: off
        self.headers = {
            "User-Agent": self.user_agent,
            "x-api-key": self.token,
        }
        # fmt: on

        self.payload = {}

        # Extract timeout, default to 30 seconds.
        self.timeout = kwargs.get("timeout", 30)

        # Extract max attempts, default to 3.
        self.max_attempts = kwargs.get("max_attempts", 3)

        self.base_path = "/v2"

        # Extract api_self_signed, defaults to False.
        self.api_self_signed = kwargs.get("api_self_signed", False)

        # if self.api_self_signed:
        #     urllib3.disable_warnings()

        self.debug_print = False

    def api_query(self, endpoint, **kwargs):
        """Executes a properly formatted API call to the isitphish API with the supplied arguments."""

        url = f"{self.BASE_URL}{endpoint}"

        # Set HTTP headers.
        headers = kwargs.get("headers", {})

        if not isinstance(headers, dict):
            raise ValueError("headers keyword passed to api_query is not a valid dict object")

        # Merge dictionaries.
        # https://treyhunner.com/2016/02/how-to-merge-dictionaries-in-python/
        headers = {**self.headers, **headers}

        # Extract HTTP verb, defaults to GET.
        method = kwargs.get("method", "GET")
        method = method.upper()

        # Extract additional parameters, defaults to an empty dictionary.
        parameters = kwargs.get("parameters", {})

        if not isinstance(parameters, dict):
            raise ValueError("parameters keyword passed to api_query is not a valid dict object")

        # Extract payload.
        payload = kwargs.get("payload", {})
        payload = {**self.payload, **payload}

        # Used to track number of failed HTTP requests.
        attempts = 0

        while True:
            try:
                if method == "POST":
                    response = requests.post(
                        url, headers=headers, json=payload, verify=(not self.api_self_signed), timeout=self.timeout
                    )

                    if response.status_code not in [200]:
                        debug_requests_response(response)

                    break

                else:
                    print(f"Invalid HTTP method passed to api_query: {method}")
                    raise ValueError(f"Invalid HTTP method passed to api_query: {method}")

            except (
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
            ):
                attempts += 1
                if self.max_attempts < attempts:
                    print(
                        f"Unable to reach isitphish API after {self.max_attempts} tries.  Consider increasing the "
                        "timeout."
                    )
                    sys.exit(1)
                else:
                    print("Packet loss when attempting to reach the isitphish API.")

        if self.debug_print:
            debug_requests_response(response)

        return response

    # Retrieve URL score.
    def retrieve_url_score(self, url):
        """Retrieve URL score"""

        print(f"Retrieving score for URL: {url}")

        payload = {"url": url}

        response = self.api_query("/v2/query", method="POST", payload=payload)
        json_response = response.json()

        url_score = {}

        if response.status_code == 200:
            url_score = json_response["body"]
            print(f"URL '{url}' score is: {url_score}")
        else:
            print(f"Unable to retrieve score for URL: {url}.  Response: {json_response}")

        return url_score


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="isitphish API client")
    parser.add_argument("-u", dest="url", action="store", required=False, help="URL to query for isitphish score.")
    args = parser.parse_args()

    iip_client = IsItPhishClient()
    iip_client.retrieve_url_score(args.url)
