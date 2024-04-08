import json


def category_post_processing(msg):
    """
    Process the category information from the given message. This task sets the routing parameter for the RAG DAG.

    Args:
        msg (Message): The message containing the category information in json format under message.body

    Returns:
        None

    Yields:
        ret (Message): The message containing the category information and the user question.

    """
    # load the input data and create new output dictionary
    data = json.loads(msg.body)
    output = {}

    # get the category if all information available
    try:
        output["cat_json"] = json.loads(data["output"])
        output["question"] = data["input_data"]["question"]
        output["category"] = output["cat_json"]["category"]

        # set the return value
        ret = msg.result(json.dumps(output))

        # set filters found to use in conditional routing in dag
        ret.category = output["cat_json"]["category"]

        # yield the return value for the next task
        yield ret

    # debug log in case JSON retrieval fails
    except:
        print("unable to get JSON")
