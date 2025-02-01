from database.neo4j_service import Neo4jService
from services.custom_llm import CustomLLMService as llm
from services import output_validator as ou
from utils.utils import *
import time
import os

def main():
    logger = setup_logging()
    logger.info("Running Main...")

    try:
        # Initialize services
        db = Neo4jService()
    except Exception as e:
        logger.error(f"Error during db init")


    #instructions and report dir
    instructions_dir = "db_prompt.txt"
    input_report_dir = "prompt_reports/oppenheim.txt"
    #Ollama model to use
    model = "mistral"

    #generate LLM output and log
    output = llm.get_response(build_prompt(instructions_dir, input_report_dir), model))
    #save_to_file(output, f'log_{model}_{time.time()}', 'logs')

    #Test json
    ts = test_json()

    #validate LLM output (valid json)
    validated_report = ou.validate_report(ts)

    #save to DB

    if validated_report:
        #run only once
        db.setup_schema()

        db.insert_report(validated_report)

        # Query all operations
        #operations = db.query_all_operations()
        #for operation in operations:
        #print(operation)

        db.close()
    else:
        logger.error("Terminating due to invalid report")

def build_prompt(instructions, report):
    # Read the instructions file
    if not os.path.isfile(instructions):
        raise FileNotFoundError(f"Instructions file '{instructions}' not found. Please check the path.")

    with open(instructions, "r") as f:
        instructions_content = f.read()

    if not instructions_content.strip():
        raise ValueError(f"The instructions file '{instructions}' is empty.")

    # Read the report file
    if not os.path.isfile(report):
        raise FileNotFoundError(f"Report file '{report}' not found. Please check the path.")

    with open(report, "r") as f:
        report_content = f.read()

    #print(instructions_content + report_content)
    return instructions_content + report_content

def test_json():
    return {
        "operationDetails": {
            "operationID": "OP12345",
            "operationName": "Flood Relief Operation",
            "disasterType": "Flood",
            "dateTime": "2025-01-22T10:00:00",
            "duration": 12.5,
            "location": "Springfield"
        },
        "resources": ["Helicopter", "Boat", "Medical Kits"],
        "tasks": [
            {
                "name": "Evacuation",
                "description": "Evacuate residents from flooded areas.",
                "startTime": "2025-01-22T10:30:00",
                "endTime": "2025-01-22T15:00:00",
                "location": "Downtown Springfield"
            },
            {
                "name": "Distribution of Supplies",
                "description": "Distribute food and water to shelters.",
                "startTime": "2025-01-22T12:00:00",
                "endTime": "2025-01-22T18:00:00",
                "location": "Community Shelter"
            }
        ],
        "observations": {
            "challenges": ["Roads blocked by debris", "Limited communication networks"],
            "successes": ["Rescued 200 residents", "Delivered 500 meals"]
        },
        "externalSupport": {
            "agencies": ["Red Cross", "National Guard"]
        }
    }


if __name__ == "__main__":
    main()