#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import cgi
import uuid
import os
import boto3
import json
from seaplane_request import post_request, get_archive
import time
from urllib.parse import urlparse, parse_qs


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        SimpleHTTPRequestHandler.end_headers(self)


def upload_to_s3(filename, bucket_name, object_name):
    """
    Uploads a file to an S3 bucket.

    Args:
        filename (str): The path of the file to upload.
        bucket_name (str): The name of the S3 bucket.
        object_name (str): The name of the object in the S3 bucket.

    Returns:
        str: The URL of the uploaded file.

    Raises:
        Exception: If there is an error uploading the file to S3.
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    try:
        s3.upload_file(filename, bucket_name, object_name)
        print("File uploaded to S3 successfully.")
    except Exception as e:
        print("Error uploading file to S3:", e)

    # Generate the URL for the uploaded file
    url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
    return url


class S(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """
        Handle GET requests to the server.
        Returns:
            None
        """
        # Parse the URL to extract request parameters
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        # Extract the request ID if present, or set it to None
        request_id = query_params.get("request_id", [None])[0]

        # poll seaplane endpoint for results
        while True:
            my_data = get_archive("sea-ri", request_id)
            data = json.loads(my_data)
            print(data)
            print(len(data))
            time.sleep(1)

            # break out of loop once we receive the second data
            if len(data) == 2:
                break

        # check if we should send the data or not
        if data[1]["play_second_audio"]:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data[1]).encode())
        else:
            self.send_response(204)

    def do_POST(self):
        """
        Handle POST requests to the server.
        Returns:
            None
        """
        # Extracting data from the form
        form_data = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers["Content-Type"],
            },
        )

        # get the audio from the request
        audio_file = form_data["file"]

        # create a temporary file name
        temp_name = f"{str(uuid.uuid4())}.mp3"

        # Saving audio data to a file
        with open(temp_name, "wb") as f:
            f.write(audio_file.file.read())

        # send to s3
        bucket_name = "seaplane-seari-demo"
        url = upload_to_s3(temp_name, bucket_name, temp_name)
        print(url)

        # remove local file
        os.remove(temp_name)

        # call seaplane
        r = post_request(url)
        data = json.loads(r)
        request_id = data["request_id"]

        # request the output from seaplane
        while True:
            my_data = get_archive("sea-ri", request_id)
            data = json.loads(my_data)
            print(data)
            time.sleep(1)

            # update response once status is completed
            if len(data) == 1:
                break

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data[0]).encode())


def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ("", 8000)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd...")
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
