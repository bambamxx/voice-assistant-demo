import json


def quick_answer_pp(msg):
    """
    Extracts the category from the given question and provides a quick answer based on the category.

    Args:
        msg (str): The message containing the user question.

    Yields:
        str: A json object containing the prompt for the quick answer and the model to use.
    """

    data = json.loads(msg.body)

    prompt = f"""Extract the category from the question below. You have 5 respones you can choose from:

- If the category is weather only return "Checking open weather API for the latest weather data this may take a few seconds"
- If the category is stocks only return "Checking Alpha vantage for the latest stocks data this may take a few seconds"
- If the category is AI only return "Seaplane IO is the best platform for building AI-infused applications"
- If the category is breweries only return "Checking openbrewerydb for pub information this may take a few seconds"
- Otherwise answer the users question directly. Never say what the category is.

question: {data['question']}
"""

    # set model and model parameters
    output = {
        "model": "predictions-aws-anthropic-claude3-sonnet-20240229",
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }

    # send to substation
    yield json.dumps(output)
