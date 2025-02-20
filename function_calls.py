
# A1

retrieve_data = {
    "name": "retrieve_data",
    "description": "Any variation referring to retrieving data from Github User Content site",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "A GitHub user content url e.g. https://raw.githubusercontent.com/..."
            },
            "email": {
                "type": "string",
                "description": "An email is required to download the files e.g. example@email.com"
            }
        }
    },
    "required": ["url", "email"]
}

# A2

format_content = {
    "name": "format_content",
    "description": "Format the contents of a file",
    "parameters": {
        "type": "object",
        "properties": {
            "prettier": {
                "type": "string",
                "description": "Prettier version to use to format the document e.g. prettier@X.X.X"
            },
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the contents to format e.g. /data/path/to/file.txt"
            }
        }
    },
    "required": ["input"]
}

# A3

count_days = {
    "name": "count_days",
    "description": "Any variation referring to retrieving count of days in a list",
    "parameters": {
        "type": "object",
        "properties": {
            "days": {
                "type": "string",
                "description": "Day of the week e.g. Monday, Tues, Wed, Thursday, Friday, Saturday, Sunday"
            },
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the dates e.g. /data/path/to/file.txt"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["days", "input", "output"]
}

# A4

sort_contacts = {
    "name": "sort_contacts",
    "description": "Any variation referring to retrieving and sorting an array of contacts",
    "parameters": {
        "type": "object",
        "properties": {
            "conditions": {
                "type": "array",
                "description": "Sort conditions for contacts e.g. last_name then first_name",
                "items": {
                    "type": "string"
                }
            },
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the contacts e.g. /data/path/to/file.json"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.json"
            }
        }
    },
    "required": ["conditions", "input", "output"],
}

# A5

recent_logs = {
    "name": "recent_logs",
    "description": "Any variation of extracting the most recent logs",
    "parameters": {
        "type": "object",
        "properties": {
            "count": {
                "type": "integer",
                "description": "Number of lines to return e.g. 10"
            },
            "input": {
                "type": "string",
                "description": "Filepath that contains the logs e.g. /data/path/to/file"
            },
            "output": {
                "type": "string",
                "description": "Filename and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["count", "input", "output"],
}

# A6

file_contents = {
    "name": "file_contents",
    "description": "Any variation referring to retrieving the first occurrence of each file and extract it",
    "parameters": {
        "type": "object",
        "properties": {
            "filetype": {
                "type": "string",
                "description": "Filetype to be searched e.g. .json .md"
            },
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the files to be indexed e.g. /data/path/to/file.md"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.json"
            }
        }
    },
    "required": ["filetype", "input", "output"],
}

# A7

extract_email = {
    "name": "extract_email",
    "description": "Any variation referring to retrieving and extracting the sender's email address",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the email message e.g. /data/path/to/file.txt"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["input", "output"],
}

# A8

extract_credit_card = {
    "name": "extract_credit_card",
    "description": "Any variation referring to retrieving and extracting the credit card number from an image file",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the credit card numbers e.g. /data/path/to/file.png"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["input", "output"],
}

# A8

extract_credit_card = {
    "name": "extract_credit_card",
    "description": "Any variation referring to retrieving and extracting the credit card number from an image file",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the credit card numbers e.g. /data/path/to/file.png"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["input", "output"],
}

# A8

extract_credit_card = {
    "name": "extract_credit_card",
    "description": "Any variation referring to retrieving and extracting the credit card number from an image file",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Filepath and name that contains the credit card numbers e.g. /data/path/to/file.png"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["input", "output"],
}

# A9

embedding_comments = {
    "name": "embedding_comments",
    "description": "Any variation referring to retrieving similar comment embeddings",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Filepath and name that contains a list of comments e.g. /data/path/to/file.txt"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["input", "output"],
}

# A10

ticket_sales = {
    "name": "ticket_sales",
    "description": "Any variation referring to retrieving and extracting total ticket sales",
    "parameters": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "description": "A description of the ticket type e.g. Gold, Silver, Bronze"
            },
            "input": {
                "type": "string",
                "description": "Filepath that contains the database file e.g. /data/path/to/file.db"
            },
            "output": {
                "type": "string",
                "description": "Filepath and name to save the output e.g. /data/path/to/output.txt"
            }
        }
    },
    "required": ["type", "input", "output"],
}

task_runner = {
    "name": "task_runner",
    "description": "Any variation of user requesting to create code, execute code, and run code",
    "parameters": {
        "type": "object",
        "properties" :{
            "input": {
                "type": "string",
                "description": "Filepath and filename that contains a information that will be used by the code must start with /data/ e.g. /data/path/to/input"
            },
            "output": {
                "type": "string",
                "description": "Filepath and filename to save the output must start with /data/ e.g. /data/path/to/output"
            }
        }
    }
}

function_calls = [
    retrieve_data,
    format_content,
    count_days,
    sort_contacts,
    recent_logs,
    file_contents,
    extract_email,
    extract_credit_card,
    embedding_comments,
    ticket_sales,
    task_runner,
]
