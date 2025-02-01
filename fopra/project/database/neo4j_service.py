from neo4j import GraphDatabase
import logging
from models.report import Report, ExtendedReport
from config.database_config import DATABASE
from datetime import datetime

class Neo4jService:
    """Service for interacting with Neo4j database"""

    def __init__(self):
        self.uri = DATABASE['ip']
        self.user = DATABASE['username']
        self.password = DATABASE['password']
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.logger = logging.getLogger(__name__)
        self.setup_schema()

    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()

    def setup_schema(self):
        """Set up the database schema with constraints"""
        setup_queries = [
            """
            CREATE CONSTRAINT IF NOT EXISTS FOR (o:Operation) REQUIRE o.id IS UNIQUE;
            """,
            """
            CREATE CONSTRAINT IF NOT EXISTS FOR (t:Task) REQUIRE t.name IS UNIQUE;
            """,
            """
            CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE;
            """,
            """
            CREATE CONSTRAINT IF NOT EXISTS FOR (a:Agency) REQUIRE a.name IS UNIQUE;
            """,
            """
            CREATE CONSTRAINT IF NOT EXISTS FOR (r:Resource) REQUIRE r.name IS UNIQUE;
            """
        ]

        try:
            with self.driver.session() as session:
                for query in setup_queries:
                    session.run(query)
            self.logger.info("Schema setup completed successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup schema: {str(e)}")
            raise

    def store_report(self, report):
        """Store a fire department report in Neo4j"""
        if isinstance(report, Report):
            # Convert legacy Report to ExtendedReport format
            operation_data = {
                "operationID": str(hash(f"{report.datum}_{report.ort}_{report.einsatzart}")),
                "operationName": report.einsatzart,
                "disasterType": report.einsatzart,
                "location": report.ort,
                "dateTime": report.datum.isoformat(),
                "duration": report.dauer,
                "resources": report.beteiligte,
                "tasks": [{
                    "name": "Haupteinsatz",
                    "description": report.verlauf,
                    "location": report.ort,
                    "startTime": report.datum.isoformat(),
                    "endTime": None
                }],
                "observations": {
                    "challenges": [],
                    "successes": []
                },
                "externalSupport": {
                    "agencies": report.beteiligte
                }
            }
        else:
            # Handle ExtendedReport format
            operation_data = {
                "operationID": report.operationDetails.operationID,
                "operationName": report.operationDetails.operationName,
                "disasterType": report.operationDetails.disasterType,
                "location": report.operationDetails.location,
                "dateTime": report.operationDetails.dateTime.isoformat(),
                "duration": report.operationDetails.duration,
                "resources": report.resources,
                "tasks": [
                    {
                        "name": task.name,
                        "description": task.description,
                        "startTime": task.startTime.isoformat() if task.startTime else None,
                        "endTime": task.endTime.isoformat() if task.endTime else None,
                        "location": task.location,
                    }
                    for task in report.tasks
                ],
                "observations": {
                    "challenges": report.observations.challenges,
                    "successes": report.observations.successes,
                },
                "externalSupport": {"agencies": report.externalSupport.agencies}
            }

        query = """
        MERGE (o:Operation {id: $operationID})
        SET o.name = $operationName,
            o.disasterType = $disasterType,
            o.dateTime = $dateTime,
            o.duration = $duration
        MERGE (l:Location {name: $location})
        MERGE (o)-[:LOCATED_AT]->(l)

        WITH o
        UNWIND $resources AS resource
        MERGE (r:Resource {name: resource})
        MERGE (o)-[:USES]->(r)

        WITH o
        UNWIND $tasks AS task
        MERGE (t:Task {name: task.name})
        SET t.description = task.description,
            t.startTime = task.startTime,
            t.endTime = task.endTime
        MERGE (loc:Location {name: task.location})
        MERGE (t)-[:LOCATED_AT]->(loc)
        MERGE (o)-[:INCLUDES_TASK]->(t)

        WITH o
        UNWIND $observations.challenges AS challenge
        MERGE (c:Challenge {description: challenge})
        MERGE (o)-[:FACED]->(c)

        WITH o
        UNWIND $observations.successes AS success
        MERGE (s:Success {description: success})
        MERGE (o)-[:ACHIEVED]->(s)

        WITH o
        UNWIND $externalSupport.agencies AS agency
        MERGE (a:Agency {name: agency})
        MERGE (o)-[:SUPPORTED_BY]->(a)
        """

        try:
            with self.driver.session() as session:
                session.run(query, operation_data)
                self.logger.info(f"Stored report from {operation_data['dateTime']}")
        except Exception as e:
            self.logger.error(f"Failed to store report: {str(e)}")
            raise

    def query_all_operations(self):
        """Query and return all operations stored in the database"""
        query = """
        MATCH (o:Operation)-[:LOCATED_AT]->(l:Location)
        OPTIONAL MATCH (o)-[:USES]->(r:Resource)
        OPTIONAL MATCH (o)-[:INCLUDES_TASK]->(t:Task)-[:LOCATED_AT]->(taskLoc:Location)
        OPTIONAL MATCH (o)-[:FACED]->(c:Challenge)
        OPTIONAL MATCH (o)-[:ACHIEVED]->(s:Success)
        OPTIONAL MATCH (o)-[:SUPPORTED_BY]->(a:Agency)
        RETURN o, l, collect(r) as resources, collect(t) as tasks, collect(taskLoc) as taskLocations,
               collect(c) as challenges, collect(s) as successes, collect(a) as agencies
        """
        try:
            with self.driver.session() as session:
                return list(session.run(query))
        except Exception as e:
            self.logger.error(f"Failed to query operations: {str(e)}")
            raise