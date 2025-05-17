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

class ScanInput(BaseModel):
    target_url: str
from typing import List, Dict

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
    detailed_endpoints = scanner.run_scan()
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
        description='''You are the Recon Agent. Your ONLY task is to perform reconnaissance on a given target URL.
Extract the URL from user input (such as "Scan http://example.com") and call the function 
`run_security_scan` with the URL as the value for `target_url`. 
If parsing fails, ask the user for a valid URL.''',
        tools=[run_security_scan], 
        instruction="You are the Recon Agent. Your ONLY task is to perform reconnaissance on a given target URL. "
        # No sub-agents needed for this example
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
    give all the attacks that were successfull and give the payload that caused the attack. give quick remediation fixes to prevent this agent
    ''',
)
root_agent=SequentialAgent(

    name="sequential_agent",
    description="You are the Sequential Agent. Your task is to manage and coordinate the execution of other agents in a sequential manner. "
                "You will delegate tasks to the Recon Agent as needed."
                "If the user provides a target URL, you will use the Recon Agent to perform reconnaissance on that URL. "
                "If the user provides a list of endpoints, you will use the Payload Agent to generate potential payloads for each endpoint."
                "If the user provides a list of payloads, you will use the Attack Agent to perform penetration testing attacks on the endpoints using the payloads.",
    sub_agents=[recon_agent,report_agent1,payload_agent,attack_agent,report_agent3]
)

# def get_weather(city: str) -> Dict:

#     # Best Practice: Log tool execution for easier debugging
#     print(f"--- Tool: get_weather called for city: {city} ---")
#     city_normalized = city.lower().replace(" ", "") # Basic input normalization

#     # Mock weather data for simplicity (matching Step 1 structure)
#     mock_weather_db = {
#         "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
#         "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
#         "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
#         "chicago": {"status": "success", "report": "The weather in Chicago is sunny with a temperature of 25°C."},
#         "toronto": {"status": "success", "report": "It's partly cloudy in Toronto with a temperature of 30°C."},
#         "chennai": {"status": "success", "report": "It's rainy in Chennai with a temperature of 15°C."},
#  }

#     # Best Practice: Handle potential errors gracefully within the tool
#     if city_normalized in mock_weather_db:
#         return mock_weather_db[city_normalized]
#     else:
#         return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

# greeting_agent = Agent(
#         model="gemini-2.0-flash-exp",
#             name="greeting_agent",
#             instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. " "Do not engage in any other conversation or tasks.",
#             # Crucial for delegation: Clear description of capability
#             description="Handles simple greetings and hellos",
            
#  )

# farewell_agent = Agent(
#           model="gemini-2.0-flash-exp",
#             name="farewell_agent",
#             instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
#                         "Do not perform any other actions.",
#             # Crucial for delegation: Clear description of capability
#             description="Handles simple farewells and goodbyes",
            
#  )

