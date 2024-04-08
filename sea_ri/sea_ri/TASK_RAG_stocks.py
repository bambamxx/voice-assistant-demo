import json
import requests
import os


def rag_stocks(msg):
    """
    Retrieves the last known stock value for a given ticker symbol using Alpha Vantage API and constructs the RAG section of the prompt

    Args:
        msg (Message): The input message containing a JSON string with the required fields i.e., ticker symbol.

    Yields:
        str: A JSON string containing the stock data in the RAG prmpt and the source.
    """

    # load the input data
    data = json.loads(msg.body)
    stock = data["cat_json"]["ticker"]

    # query alpha vantage
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={os.getenv("STOCKS_API_KEY")}'
    r = requests.get(url)
    data = r.json()

    # retrieve the last known stock value
    last_date = data["Meta Data"]["3. Last Refreshed"]
    data["RAG"] = data["Time Series (Daily)"][last_date]

    # set the source of the RAG
    data["source"] = "Alpha Vantage"

    yield json.dumps(data)
