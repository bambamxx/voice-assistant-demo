import json
import requests


def brewery(msg):
    """
    Retrieves brewery data based on the provided input message. Take the city from the input message and query the openbrewerydb API for the top 10 breweries in that city.

    Args:
        msg (Message): The message containing the input data. A JSON string containing the location of the user extracted by the LLM.

    Yields:
        str: A JSON string containing the RAG section of the prompt.

    Returns:
        None
    """

    # load the input data and extract the city
    data = json.loads(msg.body)
    city = data["cat_json"]["location"].replace(" ", "_")

    # get the brewery data
    r = requests.get(
        f"https://api.openbrewerydb.org/v1/breweries?by_city={city}&per_page=10"
    )

    # construct the RAG section of the prompt
    data[
        "RAG"
    ] = f"""
Here is the basic information about the breweries, pick the one that fits the users request best.
{r.text}
"""

    # set the source of the RAG
    data["source"] = "openbrewery db"

    # send the output
    yield json.dumps(data)
