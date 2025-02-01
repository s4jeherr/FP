from ollama import Client
from services.custom_llm import CustomLLMService
from utils.utils import *
import logging
import os
import time
import paramiko

def build_prompt(instructions, reports):
    #load prompt
    try:
        with open(instructions,"r") as f:
            prompt = f.read()
    except FileNotFoundError:
        print(f"Instructions file {instructions} not found.")
        return ""

    #load operational reports
    prompt_parts = [prompt]

    directory = os.path.join(os.getcwd(), reports)
    counter = 1

    try:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, os.fsdecode(file))
            with open(file_path, "r") as f:
                prompt_parts.append(f"Operational Report {counter}: \n")
                prompt_parts.append(f.read()+"\n")
                counter += 1
    except FileNotFoundError:
        print(f"Reports directory {reports} not found.")
        return ""

    return "".join(prompt_parts)

def main():
    logger = setup_logging()
    logger.info("Starting Ontology Generation")

    llm = CustomLLMService()

    # List of models to pull and use
    models_to_pull = ["mistral"]

    # Iterate through each model, pull it, use it, and remove it
    for model in models_to_pull:
        # Pull the model
        llm.pull_model(model)

        #Debug Test
        #generate_response(model, "Return the number 10", client)

        # Process for English
        language = "English"
        prompt_dir = "prompt.txt"
        report_dir = "prompt_reports"
        output_dir = "output/ontology_output"

        prompt = build_prompt(prompt_dir, report_dir)
        if prompt:
            start = time.time()
            response = llm.get_response(model, prompt)
            end = time.time()
            save_to_file(response, f"{model}_{language}", f"{output_dir}/{file_name}{time.time()}")
            log_time(model, language, (end - start))

        # Process for German
        language = "German"
        prompt_dir = "prompt_german.txt"
        report_dir = "prompt_reports_german"

        prompt = build_prompt(prompt_dir, report_dir)
        if prompt:
            start = time.time()
            response = llm.get_response(model, prompt)
            end = time.time()
            save_to_file(response, f"{model}_{language}", f"{output_dir}/{file_name}{time.time()}")
            log_time(model, language, (end - start))

        # Remove the model after use
        #llm.remove_model(model)

    # Close the SSH connection
    llm.close()
    print("SSH connection closed.")

if __name__ == '__main__':
    main()