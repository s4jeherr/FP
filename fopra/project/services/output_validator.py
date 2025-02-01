from pydantic import ValidationError
import json
import logging
from models.report import ExtendedReport

def validate_report(report_data: dict) -> ExtendedReport:
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
            validated_report = ExtendedReport(**report_data)
            logger.info("Report validation successful")
            return validated_report
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Error during report validation: {str(e)}")
        return None