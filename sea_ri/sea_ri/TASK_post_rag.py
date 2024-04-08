import json


def post_rag(msg):
    """
    Constructs the final prompt to answer the input quesiton. Combining the reuglar prompt, question and RAG prompt.

    Args:
        msg (Message): The input message containing the JSON object with all required info, i.e., question, rag, source.

    Yields:
        str: A JSON string containging the finalized prompt and the model to use.
    """
    # load the input
    data = json.loads(msg.body)

    data[
        "prompt"
    ] = f"""<|system|>
You are a helpful asistant tasked with answer user questions based on the provided details. When possible provide the source. The output is meant for a voice assistant so make sure to provide it like you are talking. For example do not include lists or other things that can not be spoken. Make sure to end with a complete sentence that is not cut off</s>
<|user|>
question:  {data['question']}
information to answer question with: {data['RAG']}
source: {data['source']}
Do not say Answer:
</s>
<|assistant|>
"""

    # set model and model paramters
    data["model"] = "zephyr-7b"

    yield json.dumps(data)
