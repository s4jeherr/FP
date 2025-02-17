from database.neo4j_service import Neo4jService
from services.custom_llm import CustomLLMService as llm
from services.validator import Validator as vr
from utils.utils import setup_logging, save_to_file
import time
import os

def initialize_services(logger):
    try:
        neo4j_service = Neo4jService()
        llm_client = llm()
        neo4j_service.setup_schema()
        return neo4j_service, llm_client
    except Exception as e:
        logger.error(f"Error during service initialization: {e}")
        raise

def process_reports(neo4j_service, llm_client, instructions_dir, input_report_dir, models, logger):
    for model in models:
        for input_report in os.listdir(input_report_dir):
            try:
                report_json = llm_client.get_response(build_prompt(instructions_dir, os.path.join(input_report_dir, input_report)), model)
                validated_report = vr.validate_report(report_json)

                output_dir = 'logs/json_generation/validated' if validated_report else 'logs/json_generation/notvalidated'

                if validated_report:
                    neo4j_service.store_report(validated_report)
                else:
                    logger.error(f"Skipping {input_report} due to invalid report")

                save_to_file(report_json, f'log_{input_report}_{int(time.time())}.txt', f'{output_dir}/{model}')

            except Exception as e:
                logger.error(f"Error processing {input_report} with model {model}: {e}")

        llm_client.remove_model(model)

def cleanup_services(neo4j_service, llm_client, logger):
    try:
        llm_client.close()
        neo4j_service.close()
    except Exception as e:
        logger.error(f"Error during service cleanup: {e}")

def build_prompt(instructions, report):
    if not os.path.isfile(instructions):
        raise FileNotFoundError(f"Instructions file '{instructions}' not found. Please check the path.")
    with open(instructions, "r") as f:
        instructions_content = f.read()
    if not instructions_content.strip():
        raise ValueError(f"The instructions file '{instructions}' is empty.")

    if not os.path.isfile(report):
        raise FileNotFoundError(f"Report file '{report}' not found. Please check the path.")
    with open(report, "r") as f:
        report_content = f.read()

    return instructions_content + report_content

#only used for debugging purposes
def test_json(example_report):
    if not os.path.isfile(example_report):
        raise FileNotFoundError(f"Example report file '{example_report}' not found. Please check the path.")
    with open(example_report, "r") as f:
        return f.read()

def main():
    logger = setup_logging()
    logger.info("Running Main...")

    instructions_dir = "data/db_prompt.txt"
    input_report_dir = "data/ontology/prompt_reports"
    models = ["mistral", "llama3.3", "mistral-nemo", "qwen2", "phi4"]

    neo4j_service, llm_client = initialize_services(logger)

    try:
        process_reports(neo4j_service, llm_client, instructions_dir, input_report_dir, models, logger)
    finally:
        cleanup_services(neo4j_service, llm_client, logger)

if __name__ == "__main__":
    main()