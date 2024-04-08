import json


def text_to_speech_pre_processing(msg):
    """
    Structure the input data to send it to the text to speech model. Including model name and reference audio file.

    Args:
        msg (str): The input message containing JSON data, including the URL where we can find the user audio recording..

    Yields:
        str: A JSON string containign the model and model parameterrs for the speech to text model.
    """
    # load the input data
    data = json.loads(msg.body)

    # create the output object
    output = {}

    # check if this is a quick answer by anthropic or a full answer by another LLM
    if (
        data["input_data"]["model"]
        == "predictions-aws-anthropic-claude3-sonnet-20240229"
    ):
        output_text = data["request"]["output"]["content"][0]["text"]
    else:
        output_text = data["output"]
        output["category"] = data["input_data"]["category"]

    # create the prompt and select the model and model parameters
    output["text"] = output_text
    output["model"] = "styletts2"
    output["reference"] = (
        "https://seaplane-seari-demo.s3.us-west-1.amazonaws.com/696_92939_000016_000006.wav"
    )
    output["diffusion_steps"] = 0

    # send to substation for processing
    yield json.dumps(output)
