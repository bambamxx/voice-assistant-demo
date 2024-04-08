import json
import time
import requests
import os
import uuid


def speech_to_text_pre_processing(msg):

    # load input data
    data = json.loads(msg.body)

    # download the audio from the URL
    audio_file = requests.get(data["audio_url"])

    # transcribe using openAI whisper
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
    files = {
        "file": ("audio.mp3", audio_file.content),
        "model": (None, "whisper-1"),
    }
    response = requests.post(url, headers=headers, files=files)
    transcript = response.text

    # set the model, paramters and prompt for the categorization
    output = {}
    output[
        "prompt"
    ] = f"""[INST]
Extract the category from the question below. Category can either be weather, stocks, breweries, flightstatus or other. Your return should only include a JSON object and nothing else. 
If the cateogry is weather provide only the following output json 
{{"category" : "weather", "location" : LOCATION}}
if the category is stocks provide only the following output json
{{"category" : "stocks", "ticker", TICKER}}
if the category is breweries provide only the following json
{{"category" : "breweries", location : LOCATION}}
If the category is flight status provide only the following json
{{"category" : "flight_status", "flight_number" : FLIGHT_NUMBER}}
If the category is other provide only the following output json
{{"category" : "other" , "question" : QUESTION}}
message: {transcript}
[/INST]
"""

    output["model"] = "mistral-7b-instruct-v0.1"
    output["temperature"] = 0.01
    output["question"] = transcript
    yield json.dumps(output)
