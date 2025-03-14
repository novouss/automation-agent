from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import List, Dict, Any
from openai import OpenAI

from function_calls import function_calls
# from keys import OPENAI_KEY

import os
import json
import base64
import string
import sqlite3
import subprocess
import numpy as np
from langdetect import detect
from scipy.spatial import distance
from dateutil.parser import parse

app = FastAPI()

URL = "https://llmfoundry.straive.com/openai/v1/"
API_KEY = os.environ["AIPROXY_TOKEN"]
# API_KEY = OPENAI_KEY

client = OpenAI(
    base_url = URL,
    api_key = API_KEY
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["OPTIONS", "GET", "POST"],
    allow_headers = ["*"]
)

def query_text(query: str, system: str = "Reply only with the answer the user is looking for no added texts"):
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

def query_image(query: str, image: str):
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

def query_embeddings(text: str):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def function_gpt(prompt: str, tools: List[Dict[str, Any]]):
    completions = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{
            "role": "user", "content": prompt
        }],
        functions = tools,
        function_call = "auto"
    )
    return completions.choices[0].message

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
        subprocess.run(["npx", "-y", prettier, "--config", "./.prettierrc", "--write", input], check=True, capture_output=True)
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
    if days.endswith("days"):
        days = days[:len("days")]
    elif days.endswith("day"):
        days = days[:len("day")]
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
    response = query_text(f"Extract the sender's email address from this email. {email}")
    # Write the sender's email address to the output file
    make_directory(output)
    with open(output, "w") as file:
        file.write(response)
    return "Extracted email has been saved at: " + output

def extract_credit_card(input: str, output: str):
    with open(input, "rb") as file:
        image = base64.b64encode(file.read()).decode("utf-8")
    image_base64 = f"data:image/png;base64,{image}"
    response = query_image("Extract the long Product Cover ID numbers (often a variation of XXXX XXXX XXXX XXXX) from this image ", image_base64)
    # Write the credit card number to the output file
    make_directory(output)
    with open(output, "w") as file:
        file.write(response)
    return "Extracted credit card has been saved at: " + output

def embedding_comments(input: str, output: str):
    with open(input, "r") as file:
        comments = [line.strip() for line in file.readlines()]
    # Compute embeddings for each comment
    embeddings = []
    for comment in comments:
        embedding = query_embeddings(comment)
        embeddings.append(embedding)
    embeddings_array = np.array(embeddings)
    # Much more efficient approach https://stackoverflow.com/questions/53455909/python-optimized-most-cosine-similar-vector
    cosine_distances = distance.cdist(embeddings_array, embeddings_array, "cosine")
    min_distance = float("inf")
    most_similar_pair = (None, None)
    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            if cosine_distances[i, j] < min_distance:
                min_distance = cosine_distances[i, j]
                most_similar_pair = (comments[i], comments[j])
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

def task_runner(**kwargs):
    # start_time = time.time()
    args = kwargs
    filename = []
    libraries = []
    code_source = ""
    code_path = "/data/"
    
    for index, line in enumerate(args["task"].split("\n")):
        if line.startswith("```"):
            continue
        if line.startswith("# "):
            line_split = line.split()
            if index == 1: # Filename index
                filename = [text for text in line_split if text.endswith(".py")]
            elif index == 2 and not line.endswith("None"): # Libraries index
                libraries = [text.strip(string.punctuation) for text in line_split[3:] if text.strip(string.punctuation).isalnum()] 
            continue
        code_source += line + "\n"
        
    # print(f"Time taken for parsing: {time.time() - start_time} seconds")
    if not filename: # Filename failsafe, if filename wasn't generated
        filename = "python-code.py"
    filepath = code_path + filename[0]
    
    # Python file creation
    make_directory(filepath)
    with open(filepath, "w") as file:
        file.write(code_source)
    # print(f"Time taken for file creation: {time.time() - start_time} seconds")
    
    command = ["uv", "add", "--frozen"]
    for lib in libraries:
        run = command + [lib]
        subprocess.run(run, check=True, capture_output=True)
    # print(f"Time taken for library installation: {time.time() - start_time} seconds")
    
    try:
        # Running the file
        command = ["uv", "run", filepath]
        # print("3.5 Running uv files")
        subprocess.run(command, check=True, capture_output=True)
        # print("3.6 Passed Subprocess")
        # print(f"Time taken for script execution: {time.time() - start_time} seconds")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"The generated code failed to run {str(e.stderr.decode())}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{command} failed to run due to: {str(e)}")
    return str(command) + " has ran successfully!"

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
    "ticket_sales": ticket_sales,
    "task_runner": task_runner,
}

def handle_function_call(response):
    # print("1.1 Response", response)
    if not response.function_call:
        # print("1.1.1 No function_call")
        return { "name": "task_runner", "args": {} }
    
    function_called = response.function_call.name
    # print("1.2 Function called", function_called)
    
    function_args = json.loads(response.function_call.arguments)
    # print("Args", function_args)
    
    required_params = next((f["required"] for f in function_calls if f["name"] == function_called), [])
    # print("1.3 Required", required_params)
    
    for param in required_params:
        # Break if no required params were needed
        if not required_params:
            break
        # Checking for required parameters
        if param not in function_args:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Handler missing required parameter: {param}")
        # Checking for asking data outside of /data/
        if param in ["input", "output"] and not function_args[param].startswith("/data/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sorry, you don't have permission to access {function_args[param]}")
    # Continue to run if required parameters are met
    # print("1.4 Passed paramters")
    return { "name": function_called, "args": function_args }

@app.post("/run", status_code=status.HTTP_200_OK)
def run_task(request: Request):
    try:
        # Retrieve task request
        task = request.query_params["task"]
        if not is_english(task):
            # If task wasn't written in English, translate it
            task = query_text("Translate this text in English: " + task)
        
        # Run task to function calls
        response = function_gpt(task, function_calls)
        # Tasks under function call responses
        function_call = handle_function_call(response)
        function_to_call = functions[function_call["name"]]
        response_message = ""
        if function_call["name"].startswith("task_runner"):
            # print("3.1 Passed queries")
            args = ""
            if function_call["args"].get("input"):
                args += f"Use {function_call["args"].get("input")} as input."
            if function_call["args"].get("output"):
                args += f"Use {function_call["args"].get("output")} as output."
            response = query_text(task, f"Reply only with Python answers.Comment 'filename:' to line 1 and add the name of the file.Comment 'non-native libraries' to line 2 and add non-native python libraries used in the project,if none say None.Double check to ensure there is no errors running the script.Use native Python Libraries as much as possible.{args}")
            function_call["args"].update({ "task" : response })
            response_message = function_to_call(**function_call["args"])
        else:
            response_message = function_to_call(**function_call["args"])
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Entry missing required parameter: {ke}")
    except FileNotFoundError as fnfe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The file or directory {fnfe} does not exist or cannot be found!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{str(e)}")
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
    except IsADirectoryError as de:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You seem to be trying to read a directory {de}")
    except FileNotFoundError as fnfe: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The file or directory {fnfe} does not exist or cannot be found!")
    return PlainTextResponse(output)

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
