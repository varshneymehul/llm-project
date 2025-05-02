import json
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

import os
from dotenv import load_dotenv

# from langchain.schema import SystemMessage, HumanMessage

# Load API Key
load_dotenv()
api_key = os.getenv("API_KEY")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash", api_key=api_key, temperature=0.0
)

# print(llm([HumanMessage(content="HI")]).content)
print(llm.invoke(["hi"]).content)

message = "You are a helpful assistant. Provide concise summaries of the text. If the file contains any code write about every function present in the file, else describe the file contents clearly like how you would explain it to a 5 year old"

# print(llm.invoke([message]).content)


def get_file_content(file_path):
    """Reads the content of a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def summarize_file(file_content):
    prompt = message + "\n" + file_content

    retries = 3
    for attempt in range(retries):
        try:
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            if "429" in str(e):
                print("Quota exceeded. Retrying after delay...")
                time.sleep(35)  # Wait longer based on retry_delay
            else:
                raise e
    return "Error: Failed after multiple retries."


def summarize_folder(folder_path):
    """Iterate through the folder, summarize each file, and return summaries."""
    summaries = {}

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in files:
            file_path = os.path.join(root, filename)

            try:
                # Read the file content
                file_content = get_file_content(file_path)

                # Get the summary of the content
                summary = summarize_file(file_content)
                time.sleep(1.5)  # Add delay between API calls

                # Store the summary in the dictionary with relative file path
                relative_path = os.path.relpath(file_path, folder_path)
                summaries[relative_path] = summary
            except Exception as e:
                print(f"Error summarizing {filename}: {e}")

    return summaries


summaries = summarize_folder(
    "/Users/mehulvarshney/Documents/College/Sem 4/IntroToLLM/project/turning-ideas"
)
print(len(summaries))

for key in summaries.keys():
    print(key)


# Function to write summaries to a text file
def write_summaries_to_file(summaries, output_file):
    """Writes the very detailed summaries to a text file. If the file contains any code write about every function present in the file, else describe the file contents clearly like how you would explain it to a 5 year old"""
    with open(output_file, "w", encoding="utf-8") as file:
        for file_path, summary in summaries.items():
            file.write(f"Summary of {file_path}:\n")
            file.write(f"{summary}\n")
            file.write("\n" + "=" * 50 + "\n")


os.makedirs(f"summaries", exist_ok=True)
write_summaries_to_file(summaries, "summaries/summaries.txt")
