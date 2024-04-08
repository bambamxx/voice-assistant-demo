def dummy(msg):
    """
    A dummy function that passes along the input message as is. We use this function to channel multiple outputs through a single task. Seaplane as of now does not yet support multiple outputs out of DAGs.

    Args:
        msg (Message): The input message.

    Yields:
        str: The input message
    """
    yield msg.body
