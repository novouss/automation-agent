from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
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
    api_key = os.environ["AIPROXY_TOKEN"],
    # api_key = OPENAI_KEY,
    base_url = "https://llmfoundry.straive.com/openai/v1"
)

def query_gpt(query: str):
    completions = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{
            "role": "system",
            "content": "You are a helpful assistant. Reply only with the answer the user is looking for, no added texts."
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

def function_gpt(prompt: str, tools: list(Dict[str, Any])):
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

def check_directory(path: str):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def retrieve_data(url: str, email: str):
    subprocess.run(["uv", "run", url, email])

def format_content(input: str):
    subprocess.run(["prettier", "--write", input])

def count_days(days: str, input: str, output: str):
    with open(input, "r") as file:
        dates = file.readlines()
    day_number = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
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
    check_directory(output)
    with open(output, "w") as file:
        file.write(str(count_days))

def sort_contacts(conditions: list[str], input: str, output: str):
    with open(input, "r") as file:
        contacts = json.load(file)
    sorted_contacts = sorted(contacts, key=lambda x: tuple(x[key] for key in conditions))
    # Write the sorted contacts to the output file
    check_directory(output)
    with open(output, "w") as file:
        json.dump(sorted_contacts, file, indent=4)

def recent_logs(count: int, input: str, output: str):
    log_files = [os.path.join(input, f) for f in os.listdir(input) if f.endswith(".log")]
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    recent_logs = []
    for log_file in log_files[:count]:
        with open(log_file, "r") as file:
            first_line = file.readLines().strip()
            recent_logs.append(first_line)
    # Write the first line of the most recent logs to the output file
    check_directory(output)
    with open(output, "w") as file:
        for log in recent_logs:
            file.write(log + "\n")
    
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
    check_directory(output)
    with open(output, "w") as file:
        json.dump(index, file)

def extract_email(input: str, output: str):
    with open(input, "r") as file:
        email = file.read()
    response = query_gpt(f"Extract the sender's email address from this email. {email}")
    # Write the sender's email address to the output file
    check_directory(output)
    with open(output, "w") as file:
        file.write(response)

def extract_credit_card(input: str, output: str):
    with open(input, "rb") as file:
        image = base64.b64encode(file.read()).decode("utf-8")
    image_base64 = f"data:image/png;base64,{image}"
    response = query_gpt_with_image("Extract the long Product Cover ID numbers (often spaced as XXXX-XXXX-XXXX-XXXX) from this image.", image_base64)
    # Write the credit card number to the output file
    check_directory(output)
    with open(output, "w") as file:
        file.write(response)

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
    check_directory(output)
    with open(output, "w") as file:
        file.write(most_similar_pair[0] + "\n")
        file.write(most_similar_pair[1] + "\n")

def ticket_sales(type: str, input: str, output: str):
    conn = sqlite3.connect(input)
    cur = conn.cursor()
    type = type.lower()
    cur.execute("SELECT SUM(Units * Price) AS total_sales FROM tickets WHERE LOWER(Type) LIKE '%" + type + "%';")
    sales = cur.fetchall()
    # Write the total ticket sales of type
    check_directory(output)
    with open(output, "w") as file:
        file.write(str(sales[0][0]))

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
    task = request.query_params["task"]
    if not task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'task' parameter")
    task = query_gpt("Translate this text to English: " + task)
    response = function_gpt(task, function_calls)

    if response.function_call:
        function_called = response.function_call.name
        function_args = json.loads(response.function_call.arguments)
        function_to_call = functions[function_called]
        # Checking for required parameters
        required_params = next((f["required"] for f in function_calls if f["name"] == function_called), [])
        for param in required_params:
            if param not in function_args:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required parameter: {param}")
        try:
            response_message = function_to_call(*list(function_args.values()))
        except FileNotFoundError as fnfe:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The file or directory {fnfe} does not exist or cannot be found!")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No function call found in the response.")
    return JSONResponse(content={"message": "Task completed successfully", "response": response_message}, status_code=status.HTTP_200_OK)

@app.get("/read", status_code=status.HTTP_200_OK)
def read_path(request: Request):
    path = request.query_params["path"]
    if not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'path' parameter")
    output = ""
    try:
        with open(path, "r") as file:
            output = file.read()
    except FileNotFoundError as fnfe: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The file or directory {fnfe} does not exist or cannot be found!")
    return output
