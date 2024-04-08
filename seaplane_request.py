import json
import os
from seaplane.config import config
from seaplane.sdk_internal_utils.http import headers
from seaplane.sdk_internal_utils.token_auth import with_token
import requests

# set seaplane API key
API_KEY = os.getenv("SEAPLANE_API_KEY")
config.set_api_key(API_KEY)


# get Seaplane access token
def get_token():
    """
    Retrieves an authentication token from the FlightDeck API.

    Returns:
        str: The authentication token.
    """
    url = "https://flightdeck.cplane.cloud/identity/token"
    headers = {"Authorization": "Bearer " + API_KEY}

    response = requests.post(url, headers=headers)
    return response.text


@with_token
def get_archive(token: str, app: str, request_id: str):
    """
    Retrieve the archive content from an app based on the app name and request id.

    Args:
        token (str): The authentication token.
        app (str): The seaplane application name.
        request_id (str): The ID of the request.

    Returns:
        bytes: The content of the archive.
    """
    url = f"{config.carrier_endpoint}/endpoints/{app}/response/{request_id}/archive"
    resp = requests.get(
        url,
        headers=headers(get_token()),
        params={"pattern": ".>", "format": "json_array"},
    )
    return resp.content


def post_request(url):
    """
    Send a POST request to the seaplane API with the provided URL.

    Args:
        url (str): The URL endpiont of your application.

    Returns:
        bytes: The response content from the API.
    """
    import json
    import requests

    # Construct data component with the audio URL
    data = {"audio_url": url}

    # Convert to JSON
    json_data = json.dumps(data)

    print(json_data)

    # Get the token
    token = get_token()

    # Set the token and URL
    url = "https://carrier.cplane.cloud/v1/endpoints/sea-ri/request"

    # Set the headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }

    # Make the POST request
    api_response = requests.post(url, headers=headers, data=json_data)
    print(api_response.content)

    # return the response
    return api_response.content
