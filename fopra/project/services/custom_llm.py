import requests
import logging
from typing import Dict
from datetime import datetime
from config.llm_config import LLM_SERVER
import paramiko
import time
from ollama import Client

class CustomLLMService:
    """Service for interacting with custom LLM server"""

    def __init__(self):
        self.hostname = LLM_SERVER['hostname']
        self.username = LLM_SERVER['username']
        self.password = LLM_SERVER['password']
        self.logger = logging.getLogger(__name__)
        self.ssh = None
        self.client = None
        self.logger.info("Connecting to LLM server...")
        self.connect_to_server()

    def connect_to_server(self):
        """Connect to the LLM server and initialize Ollama"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.hostname, username=self.username, password=self.password)
            self.logger.info("Connected to LLM server")

            # Start Ollama service
            ollama_command = "OLLAMA_HOST=0.0.0.0:7000 nohup /run/system-manager/sw/bin/ollama serve > /dev/null 2>&1 & echo $!"
            stdin, stdout, stderr = self.ssh.exec_command(ollama_command)

            # Wait for server to be ready
            if self.wait_for_server():
                self.client = Client(
                    host=f'http://{self.hostname}:7000',
                    headers={'x-some-header': 'some-value'}
                )
                self.logger.info("Ollama client initialized")
            else:
                raise Exception("Failed to start Ollama server")

        except Exception as e:
            self.logger.error(f"Failed to connect to LLM server: {str(e)}")
            raise

    def wait_for_server(self, timeout=300):
        """Wait for Ollama server to be ready"""
        check_command = "curl 0.0.0.0:7000"
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                stdin, stdout, stderr = self.ssh.exec_command(check_command)
                status = stdout.read().decode().strip()
                self.logger.info(f"Server Status: {status}")
                if status == "Ollama is running":
                    return True
                time.sleep(5)
            except Exception:
                time.sleep(5)
        return False

    def pull_model(self, model):
        """Pull an Ollama model"""
        try:
            pull_command = f"OLLAMA_HOST=0.0.0.0:7000 /run/system-manager/sw/bin/ollama pull {model}"
            self.ssh.exec_command(pull_command)
            self.logger.info(f"Pulled model: {model}")
        except Exception as e:
            self.logger.error(f"Failed to pull model {model}: {str(e)}")
            raise

    def get_response(self, text: str, model: str) -> Dict:
        """get response from  Ollama"""
        try:
            self.pull_model(model)

            response = self.client.chat(model=model, messages=[{
                'role': 'user',
                'content': text
            }])

            return response['message']['content']

        except Exception as e:
            self.logger.error(f"LLM analysis failed: {str(e)}")
            raise

    def remove_model(self, model):
        remove_command = f"OLLAMA_HOST=0.0.0.0:7000 /run/system-manager/sw/bin//ollama rm {model}"
        try:
            print(f"Removing Ollama model: {model}...")
            stdin, stdout, stderr = self.ssh.exec_command(remove_command)

            # Capture the output for debugging or status updates
            for line in stdout:
                print(line.strip())
            for line in stderr:
                print(f"Error: {line.strip()}")

            print(f"Model '{model}' removed successfully.")
        except Exception as e:
            print(f"Failed to remove model '{model}': {e}")

    def close(self):
        """Close connections"""
        if self.ssh:
            self.ssh.close()
            self.logger.info("Closed SSH connection")