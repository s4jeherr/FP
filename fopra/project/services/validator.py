import json
import logging
from pydantic import ValidationError
from models.validation_model import *


class Validator:
    def validate_report(report_data: dict) -> Report:
        """Validate report data against schema"""
        logger = logging.getLogger(__name__)

        try:
            # Try to parse as JSON if string
            if isinstance(report_data, str):
                try:
                    report_data = json.loads(report_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {str(e)}")
                    return None

            # Validate against schema
            try:
                validated_report = Report(**report_data)
                logger.info("Report validation successful")
                return validated_report
            except ValidationError as e:
                logger.error(f"Validation error: {str(e)}")
                return None

        except Exception as e:
            logger.error(f"Error during report validation: {str(e)}")
            return None