from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from openai import OpenAI

from sentence_transformers import SentenceTransformer
from function_calls import function_calls
from keys import OPENAI_KEY

import os
import json
import base64
import sqlite3
import subprocess
import numpy as np
from langdetect import detect
from scipy.spatial import distance
from dateutil.parser import parse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["OPTIONS", "GET", "POST"],
    allow_headers = ["*"]
)

client = OpenAI(
    # api_key = os.environ["AIPROXY_TOKEN"],
    api_key = OPENAI_KEY,
    base_url = "https://llmfoundry.straive.com/openai/v1"
)

def query_gpt(query: str, system: str = "Reply only with the answer the user is looking for, no added texts."):
    completions = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{
            "role": "system",
            "content": system
        },
        {
            "role": "user",
            "content": query
        }]
    )
    return completions.choices[0].message.content

def query_gpt_with_image(query: str, image: str):
    completions = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{
            "role": "system",
            "content": "You are a helpful assistant. Reply only with the answer the user is looking for, no added texts"
        },          
        {
        	"role": "user",
        	"content": [
                {
                    "type": "text",
                    "text": query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image
                    }
                }]
    	}]
    )
    return completions.choices[0].message.content

def function_gpt(prompt: str, tools: List[Dict[str, Any]]):
    completions = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{
            "role": "user", "content": prompt
        }],
        functions = tools,
        function_call = "auto"
    )
    output = completions.choices[0].message
    return output

def make_directory(path: str):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def is_english(text: str):
    return detect(text) == "en"

def retrieve_data(url: str, email: str):
    try:
        subprocess.run(["uv", "run", url, email], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Data retrieval failed with error: {str(e.stderr.decode())}")
    return f"{url} has ran successfully!"

def format_content(prettier: str, input: str):
    try:
        subprocess.run(["npx", "-y", prettier, "--write", input], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Content Formatting failed with error: {str(e.stderr.decode())}")
    return input + " has been formatted"

def normalize_day(day: str) -> str:
    day = day.lower().rstrip('s')
    if day.endswith("day"):
        return day[:-3]
    return day

def count_days(days: str, input: str, output: str):
    with open(input, "r") as file:
        dates = file.readlines()
    day_number = {
        "mon": 0,
        "tue": 1,
        "wed": 2,
        "thurs": 3,
        "fri": 4,
        "sat": 5,
        "sun": 6
    }
    days = days.lower()
    count_days = 0
    for date_str in dates:
        date_str = date_str.strip()
        try:
            date = parse(date_str)
            if date.weekday() == day_number[days]:
                count_days += 1
        except ValueError:
            continue
    # Write the count to the output file
    make_directory(output)
    with open(output, "w") as file:
        file.write(str(count_days))
    return "Result of counted days has been saved at: " + output

def sort_contacts(conditions: list[str], input: str, output: str):
    with open(input, "r") as file:
        contacts = json.load(file)
    sorted_contacts = sorted(contacts, key=lambda x: tuple(x[key] for key in conditions))
    # Write the sorted contacts to the output file
    make_directory(output)
    with open(output, "w") as file:
        json.dump(sorted_contacts, file, indent=4)
    return "Sorted contacts has been saved at: " + output

def recent_logs(count: int, input: str, output: str):
    log_files = [os.path.join(input, f) for f in os.listdir(input) if f.endswith(".log")]
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    recent_logs = []
    for log_file in log_files[:count]:
        with open(log_file, "r") as file:
            first_line = file.readLines().strip()
            recent_logs.append(first_line)
    # Write the first line of the most recent logs to the output file
    make_directory(output)
    with open(output, "w") as file:
        for log in recent_logs:
            file.write(log + "\n")
    return "Recent logs has been saved at: " + output
    
def file_contents(filetype: str, input: str, output: str):
    index = {}

    if filetype == "":
        filetype = ".md"
    # This is hell
    for root, _, files in os.walk(input):
        for file in files:
            if file.endswith(filetype):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("# "):
                            title = line[2:].strip()
                            relative_path = os.path.relpath(file_path, input)
                            index[relative_path] = title
                            break

    # Write the file index and contents to output file
    make_directory(output)
    with open(output, "w") as file:
        json.dump(index, file)
    return "File contents has been saved at: " + output

def extract_email(input: str, output: str):
    with open(input, "r") as file:
        email = file.read()
    response = query_gpt(f"Extract the sender's email address from this email. {email}")
    # Write the sender's email address to the output file
    make_directory(output)
    with open(output, "w") as file:
        file.write(response)
    return "Extracted email has been saved at: " + output

def extract_credit_card(input: str, output: str):
    with open(input, "rb") as file:
        image = base64.b64encode(file.read()).decode("utf-8")
    image_base64 = f"data:image/png;base64,{image}"
    response = query_gpt_with_image("Extract the long Product Cover ID numbers (often a variation of XXXX XXXX XXXX XXXX) from this image ", image_base64)
    # Write the credit card number to the output file
    make_directory(output)
    with open(output, "w") as file:
        file.write(response)
    return "Extracted credit card has been saved at: " + output

def embedding_comments(input: str, output: str):
    with open(input, "r") as file:
        comments = [line.strip() for line in file.readlines()]
    model = SentenceTransformer("all-distilroberta-v1")
    embeddings = model.encode(comments)
    # Much more efficient approach https://stackoverflow.com/questions/53455909/python-optimized-most-cosine-similar-vector
    cosine_distances = distance.cdist(embeddings, embeddings, "cosine")
    min_distance = np.inf
    most_similar_pair = (None, None)
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            if cosine_distances[i, j] < min_distance:
                min_distance = cosine_distances[i, j]
                most_similar_pair = (comments[i], comments[j])
    # Write the most similar embeddings to output file
    make_directory(output)
    with open(output, "w") as file:
        file.write(most_similar_pair[0] + "\n")
        file.write(most_similar_pair[1] + "\n")
    return "Most similar lines have been saved at: " + output

def ticket_sales(type: str, input: str, output: str):
    conn = sqlite3.connect(input)
    cur = conn.cursor()
    type = type.lower()
    cur.execute("SELECT SUM(Units * Price) AS total_sales FROM tickets WHERE LOWER(Type) LIKE '%" + type + "%';")
    sales = cur.fetchall()
    # Write the total ticket sales of type
    make_directory(output)
    with open(output, "w") as file:
        file.write(str(sales[0][0]))
    return "Result of total ticket sales has been saved at: " + output

functions = {
    "retrieve_data": retrieve_data,
    "format_content": format_content,
    "count_days": count_days,
    "sort_contacts": sort_contacts,
    "recent_logs": recent_logs,
    "file_contents": file_contents,
    "extract_email": extract_email,
    "extract_credit_card": extract_credit_card,
    "embedding_comments": embedding_comments,
    "ticket_sales": ticket_sales
}

@app.post("/run", status_code=status.HTTP_200_OK)
def run_task(request: Request):
    try:
        # Retrieve task request
        task = request.query_params["task"]
        if not is_english(task):
            # If task wasn't written in English, translate it
            task = query_gpt("Translate this text in English: " + task)
        # Run task to function calls
        response = function_gpt(task, function_calls)
        # print(task, response, sep="\n")
        # Tasks under function call responses
        if response.function_call:
            function_called = response.function_call.name
            function_args = json.loads(response.function_call.arguments)
            function_to_call = functions[function_called]
            required_params = next((f["required"] for f in function_calls if f["name"] == function_called), [])
            for param in required_params:
                # Checking for required parameters
                if param not in function_args:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required parameter: {param}")
                # Checking for asking data outside of /data/
                if param in ["input", "output"] and not function_args[param].startswith("/data/"):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sorry, you don't have permission to access {function_args[param]}")
            # Continue to run if required parameters are met
            response_message = function_to_call(*list(function_args.values()))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No function call found in the response.")
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing {ke} parameter")
    except FileNotFoundError as fnfe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The file or directory {fnfe} does not exist or cannot be found!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return JSONResponse(content={"message": "Task completed successfully", "response": response_message}, status_code=status.HTTP_200_OK)

@app.get("/read", status_code=status.HTTP_200_OK)
def read_path(request: Request):
    try:
        path = request.query_params["path"]
        output = ""
        with open(path, "r") as file:
            output = file.read()
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing {ke} parameter")
    except FileNotFoundError as fnfe: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The file or directory {fnfe} does not exist or cannot be found!")
    return output

@app.get("/greet", status_code=status.HTTP_200_OK)
def debug_tool(request: Request):
    return "Hello!"

@app.get("/files", status_code=status.HTTP_200_OK)
def debug_files(request: Request):
    try:
        path = request.query_params["path"]
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing {ke} parameter")
    return os.listdir(path)
