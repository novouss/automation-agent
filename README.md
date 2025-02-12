# Project 1 - LLM-based Automation Agent

## Background

You have joined the operations team at **DataWorks Solutions**, a company that processes large volumes of log files, reports, and code artifacts to generate actionable insights for internal stakeholders. In order to improve operational efficiency and consistency, the company has mandated that routine tasks be automated and integrated into their Continuous Integration (CI) pipeline.

Due to the unpredictable nature of incoming data (from logs, ticket systems, source code, surveys, etc.) the team has decided to use a Large Language Model (LLM) as an intermediate transformer. In this role, the LLM will perform small, reasonably deterministic tasks.

Your assignment is to build an automation agent that accepts plain‑English tasks, carries out the required (multi‑step) process leveraging an LLM where required. The finished processing artifacts must be exactly verifiable against pre‑computed expected results.

## API Capabilities

- Use a [Dockerfile](Dockerfile) to build and run the application
- Capable of doing the following requests through to its api:
    - Generate data files required for the next tasks
    - Format markdowns using `prettier@3.4.2`
    - Count the number of days in a list dates
    - Sort contacts by column order
    - Writing the first lines of most recent `.log` files
    - Extract first occurring H1 Headers in markdown files
    - Extract sender from an email
    - Extract ~~credit card~~ numbers from an image
    - Pair most similar comments using embeddings and cosine similarity
    - Write the total sales of all items in a particular ticket type

## How to run

1. Build the image by running `sudo docker build -t raymond-gorospe:v1 .`
2. Run the docker image `sudo docker run -p 8000:8000 raymond-gorospe:v1`

## How to POST/GET

Request through a RESTAPI format:

- Run the `curl -X POST http://localhost:8000/run?task=<task description>` to execute a task.
- Run the `curl -X GET http://localhost:8000/read?path=<file path>` to read contents of files. 

## Debugging

Debugging the inner workings of an docker image file can be difficult. Use the following commands to test.

- Run the `curl -X GET http://localhost:8000/greet` allows the api to return a greeting message you, indicating the app works!
- Run the `curl -X GET http://localhost:8000/files?path=<file path>` allows the api to return a list of files.
