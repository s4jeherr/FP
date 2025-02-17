from neo4j import GraphDatabase
import logging
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
        """Store an emergency operation report in Neo4j"""
        operation_data = {
            "operationID": report.operationDetails.operationID,
            "operationName": report.operationDetails.operationName,
            "disasterType": report.operationDetails.disasterType,
            "location": report.operationDetails.location,
            "dateTime": report.operationDetails.dateTime,  # Already a string
            "duration": report.operationDetails.duration,
            "resources": report.resources,
            "tasks": [
                {
                    "name": task.name,
                    "description": task.description,
                    "startTime": task.startTime,  # Already a string
                    "endTime": task.endTime,  # Already a string
                    "location": task.location if task.location else None,
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
        UNWIND CASE WHEN size($resources) > 0 THEN $resources ELSE [null] END AS resource
        WITH o, resource WHERE resource IS NOT NULL
        MERGE (r:Resource {name: resource})
        MERGE (o)-[:USES]->(r)

        WITH o
        UNWIND CASE WHEN size($tasks) > 0 THEN $tasks ELSE [null] END AS task
        WITH o, task WHERE task IS NOT NULL
        MERGE (t:Task {name: task.name, operationID: $operationID})  // Uniqueness per operation
        SET t.description = task.description,
            t.startTime = task.startTime,
            t.endTime = task.endTime
        FOREACH (_ IN CASE WHEN task.location IS NOT NULL THEN [1] ELSE [] END |
            MERGE (loc:Location {name: task.location})
            MERGE (t)-[:LOCATED_AT]->(loc)
        )
        MERGE (o)-[:INCLUDES_TASK]->(t)

        WITH o
        UNWIND CASE WHEN size($observations.challenges) > 0 THEN $observations.challenges ELSE [null] END AS challenge
        WITH o, challenge WHERE challenge IS NOT NULL
        MERGE (c:Challenge {description: challenge})
        MERGE (o)-[:FACED]->(c)

        WITH o
        UNWIND CASE WHEN size($observations.successes) > 0 THEN $observations.successes ELSE [null] END AS success
        WITH o, success WHERE success IS NOT NULL
        MERGE (s:Success {description: success})
        MERGE (o)-[:ACHIEVED]->(s)

        WITH o
        UNWIND CASE WHEN size($externalSupport.agencies) > 0 THEN $externalSupport.agencies ELSE [null] END AS agency
        WITH o, agency WHERE agency IS NOT NULL
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