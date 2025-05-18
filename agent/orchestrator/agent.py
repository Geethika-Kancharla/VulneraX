from google.adk.agents import Agent,SequentialAgent
from typing import Dict
from zap import SecurityScanner
# from simple_scanner import SimpleScanner 
from enhanced_scanner import EnhancedSecurityScanner   
from google.adk.agents import Agent
from typing import Dict
import json
import subprocess
import shlex
from pydantic import BaseModel
import time
from google.genai.errors import ClientError

class ScanInput(BaseModel):
    target_url: str
    report_content: str
    filename: str
from typing import List, Dict

def save_report_to_file(content: str, filename: str):
    """
    Save a report to a file.
    
    Args:
        content (str): The content of the report
        filename (str): The filename to save the report to
    """
    try:
        with open(f'/Users/yuktha/Documents/VulneraX/agent/reports/{filename}', 'w') as file:
            file.write(content)
        print(f"Report saved successfully to {filename}")
        return {"success": True, "message": f"Report saved to {filename}"}
    except Exception as e:
        print(f"Error saving report: {str(e)}")
        return {"success": False, "error": str(e)}

def execute(curl: List[str]) -> List[Dict]:
    """
    Execute a list of curl commands and return the results.

    Args:
        curl (List[str]): List of curl commands to execute.

    Returns:
        List[Dict]: List of results per curl command. Each result contains:
            - success (bool)
            - output (str, if success)
            - error (str, if failed)
            - status_code (int)
    """
    results = []

    for curl_command in curl:
        print(f"Executing command: {curl_command}")

        if not curl_command or not curl_command.strip().startswith("curl"):
            results.append({
                "success": False,
                "error": "Invalid curl command. Command must start with 'curl'.",
                "status_code": -1
            })
            continue

        try:
            args = shlex.split(curl_command)
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                results.append({
                    "success": True,
                    "output": result.stdout.strip(),
                    "status_code": 0
                })
            else:
                results.append({
                    "success": False,
                    "error": result.stderr.strip(),
                    "status_code": result.returncode
                })
        except subprocess.TimeoutExpired:
            results.append({
                "success": False,
                "error": "Command execution timed out after 30 seconds",
                "status_code": -1
            })

        except Exception as e:
            results.append({
                "success": False,
                "error": f"Error executing curl command: {str(e)}",
                "status_code": -1
            })

    return results

def run_security_scan(target_url: str) -> Dict:
    print(f"--- Tool: run_security_scan called with input: {target_url} ---")
    # Extract the URL safely
    if not target_url:
        return {"error": "No target_url provided."}
    print(f"--- Tool: run_security_scan called for target URL: {target_url} ---")
    scanner=SecurityScanner(target_url)
    # detailed_endpoints = scanner.run_scan()
    with open('/Users/yuktha/Documents/VulneraX/agent/scan_results/structure.json', 'r') as file:
        data = json.load(file)
    # input_path = "/Users/yuktha/Desktop/maheshbabu/example/agent/scan_results/endpoints.json"
    # output_path = "/Users/yuktha/Desktop/maheshbabu/example/agent/scan_results/output.json"
    # enhanced_scanner = EnhancedSecurityScanner(input_path, output_path)
    # formatted_endpoints=enhanced_scanner.scan()
    # Format endpoint data in the requested format
    
    print("AGENTTTTT_______________________________")
    print(data)
    return {
        "message": f"Scan completed for {target_url}",
        "endpoints": data
    }

recon_agent = Agent(
        name="recon_agent",
        model="gemini-2.0-flash-exp",
        description='''You are the Recon Agent. Your ONLY task is to perform reconnaissance on a given target URL.''',
        tools=[run_security_scan], 
        instruction='''Extract the URL from user input (such as "Scan http://example.com") and call the function 
`run_security_scan` with the URL as the value for `target_url`. '''
    )


payload_agent = Agent(
    name="payload_agent",
    model="gemini-2.0-flash-exp",
    description='''You are the Payload Agent. Your task is to generate potential penetration testing payloads 
    for given web application endpoints. These endpoints include path, methods (GET, POST), and form fields.

    For each unique path, you will return a dictionary with:
    - The endpoint path as a key
    - A nested dictionary as value containing:
      - Each form field name as key
      - A relevant attack payload as values
    
    For example:
    ```
    {
      "/login": {
        "email": ["test@example.com", "' OR 1=1--", "<script>alert(1)</script>"],
        "password": ["password123", "' OR '1'='1", "admin' --"]
      },
      "/register": {
        "name": ["test", "<script>alert(1)</script>", "'; DROP TABLE users;--"],
        "email": ["test@example.com", "admin@' OR 1=1--"]
        // other fields...
      }
    }
    ```

    For each field, generate 1 payload that are relevant based on the form field types:
    - For `email` fields: email format attacks and email-based injections
    - For `password` fields: SQLi or encoding-based attacks
    - For `text` fields: XSS, LFI, command injections, etc.
    - For `hidden` fields (like _token): CSRF attacks

    Include common attack types:
    - SQL Injection (`' OR 1=1--`, `admin' --`)
    - Cross-site Scripting (XSS) (`<script>alert(1)</script>`)
    - Server-Side Request Forgery (SSRF) (`http://127.0.0.1`, `file:///etc/passwd`)
    - Local File Inclusion (LFI) (`../../../../etc/passwd`)
    - Command Injection (`; ls -la`, `&& whoami`)
    '''
)

attack_agent = Agent(
    name="attack_agent",
    model="gemini-2.0-flash-exp",
    description='''You are the Attack Agent. Your ONLY task is to perform penetration testing attacks on web application endpoints.
    You will receive a list of endpoints with their respective methods and form fields. 
    For each endpoint, you will execute the attack using the payloads generated by the Payload Agent.''',
    tools=[execute],
    instruction="generate a list of curl commands for each endpoint using the payloads provided by the Payload Agent, and send to `execute()`function ")

# root_agent = Agent(
#         name="orchestrator_agent", 
#         model="gemini-2.0-flash-exp",
#         description="You are the Orchestrator Agent. Your task is to manage and coordinate the execution of other agents. "
#                     "You will delegate tasks to the Recon Agent as needed."
#                     "If the user provides a target URL, you will use the Recon Agent to perform reconnaissance on that URL. "
#                     "If the user provides a list of endpoints, you will use the Payload Agent to generate potential payloads for each endpoint."
#                     "If the user provides a list of payloads, you will use the Attack Agent to perform penetration testing attacks on the endpoints using the payloads.",
#         sub_agents=[recon_agent,payload_agent,attack_agent],
#         instruction="You are the Orchestrator Agent. Your task is to manage and coordinate the execution of other agents. "
# )

report_agent1 = Agent(
    name="report_agent1",
    model="gemini-2.0-flash-exp",
    description='''You are the Report Agent. Your ONLY task is to generate a report based on the results recon_agent.
    ''',
    tools=[save_report_to_file],
    instruction="""
    1. Generate a comprehensive security report based on the recon_agent results
    2. After creating your report, you MUST save it by calling save_report_to_file with these parameters:
       - report_content: Your complete report text
       - filename: "attack_report.txt"
    Example function call: save_report_to_file(report_content="Your report text here", filename="attack_report.txt")
    """

)
report_agent2=Agent(
    name="report_agent2",
    model="gemini-2.0-flash-exp",
    description='''You are the Report Agent. Your ONLY task is to generate a report based on the results payload_agent.
    ''',
)
report_agent3=Agent(
    name="report_agent3",
    model="gemini-2.0-flash-exp",
    description='''You are the Report Agent. Your ONLY task is to generate a report based on the results attack_agent.
    ''',
    tools=[save_report_to_file],
    instruction="""
    1. Generate a comprehensive security report based on the attack results
    2. Give all the attacks that were successful and give the payload that caused the attack. Give quick remediation fixes to prevent this agent
    3. After creating your report, you MUST save it by calling save_report_to_file with these parameters:
       - report_content: Your complete report text
       - filename: "attack_report2.txt"
    Example function call: save_report_to_file(report_content="Your report text here", filename="attack_report2.txt")
    """

)
# root_agent=SequentialAgent(

#     name="sequential_agent",
#     description="You are the Sequential Agent. Your task is to manage and coordinate the execution of other agents in a sequential manner. "
#                 "You will delegate tasks to the Recon Agent as needed."
#                 "If the user provides a target URL, you will use the Recon Agent to perform reconnaissance on that URL. "
#                 "If the user provides a list of endpoints, you will use the Payload Agent to generate potential payloads for each endpoint."
#                 "If the user provides a list of payloads, you will use the Attack Agent to perform penetration testing attacks on the endpoints using the payloads.",
#     sub_agents=[recon_agent,report_agent1,payload_agent,attack_agent,report_agent3]
# )

def handle_api_execution(func, *args, **kwargs):
    """
    Wrapper function to handle API rate limit errors with retry logic.
    
    Args:
        func: The function to execute
        *args, **kwargs: Arguments to pass to the function
    
    Returns:
        The result of the function call
    """
    try:
        return func(*args, **kwargs)
    except ClientError as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print(f"API quota exceeded: {str(e)}")
            print("Waiting for 30 seconds to reset quota...")
            time.sleep(30)  # Sleep for 30 seconds
            print("Retrying operation...")
            return func(*args, **kwargs)  # Retry once after waiting
        else:
            # If it's another type of error, re-raise it
            raise

# Modify your SequentialAgent to use this wrapper
class RateLimitAwareSequentialAgent(SequentialAgent):
    def process(self, *args, **kwargs):
        return handle_api_execution(super().process, *args, **kwargs)

# Replace your root_agent with the rate-limit aware version
root_agent = RateLimitAwareSequentialAgent(
    name="sequential_agent",
    description="You are the Sequential Agent. Your task is to manage and coordinate the execution of other agents in a sequential manner. "
                "You will delegate tasks to the Recon Agent as needed."
                "If the user provides a target URL, you will use the Recon Agent to perform reconnaissance on that URL. "
                "If the user provides a list of endpoints, you will use the Payload Agent to generate potential payloads for each endpoint."
                "If the user provides a list of payloads, you will use the Attack Agent to perform penetration testing attacks on the endpoints using the payloads.",
    sub_agents=[recon_agent, report_agent1, payload_agent, attack_agent, report_agent3]
)
