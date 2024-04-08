import json
import boto3
import os
from seaplane.object import object_store
import uuid


def upload_to_s3(filename, bucket_name, object_name):
    """
    Uploads a file to an S3 bucket. This bucket needs to be fully public for the demo to work. In addition if you want to use the provided front-end it should have a CORS policy allowing all origins.

    Args:
        filename (str): The path of the file to be uploaded.
        bucket_name (str): The name of the S3 bucket.
        object_name (str): The name of the object in the S3 bucket.

    Returns:
        str: The URL of the uploaded file.

    Raises:
        Exception: If there is an error uploading the file to S3.
    """

    # create S3 client using credentials in .env file
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    # try upload to S3.
    try:
        s3.upload_file(filename, bucket_name, object_name)
        print("File uploaded to S3 successfully.")
    except Exception as e:
        print("Error uploading file to S3:", e)

    # Generate the URL for the uploaded file
    url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"

    # return the URL of the uploaded file.
    return url


def text_to_speech_post_processing(msg):
    """
    Uploads the output of the text-to-speech model to an S3 bucket and returns the URL.

    Args:
        msg (Message): The input message containging the seaplane bucketname and objectname that holds the audio recording in wav format.

    Returns:
        str: A JSON string containing the URL of the uploaded audio file.
    """
    # load the input data
    data = json.loads(msg.body)

    # create output object
    output = {}
    output["bucket"] = data["output"]["bucket"]
    output["object"] = data["output"]["object"]
    output["request_id"] = msg.meta["_seaplane_request_id"]
    category = data["input_data"].get("category", "first_run")

    # check if this category required RAG i.e if this output should be played or if the answer was already given by the quick answer path.
    if category in ["weather", "breweries", "stocks"]:
        output["play_second_audio"] = True
    else:
        output["play_second_audio"] = False

    # download the audio from the seaplane object store
    audio = object_store.download(output["bucket"], output["object"])
    filename = f"{str(uuid.uuid4())}.wav"

    # write object to file
    with open(filename, "wb") as file:
        # Write the variable to the file
        file.write(audio)

    # upload into s3 (seaplanes object store does not yet support public access to files, this is why we are using S3 for the demo.)
    url = upload_to_s3(filename, "seaplane-seari-demo", filename)
    output["url"] = url

    # yield the URL To the audio file and additonal parameters that tell the front end if it should play this auido or not.
    yield json.dumps(output)

    # remove the audio file after uploading to S3
    os.remove(filename)
