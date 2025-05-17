from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
from typing import Dict

# Import the security scan function
from ...agent.orchestrator.agent import run_security_scan

# Define the recon agent
recon_agent = Agent(
    name="recon_agent",
    model="gemini-2.0-flash-exp",
    description='''You are the Recon Agent. Your ONLY task is to perform reconnaissance on a given target URL.
Extract the URL from user input (such as "Scan http://example.com") and call the function 
`run_security_scan` with the URL as the value for `target_url`. 
If parsing fails, ask the user for a valid URL.''',
    tools=[run_security_scan],  # Register the security scan tool
    instruction="You are the Recon Agent. Your ONLY task is to perform reconnaissance on a given target URL."
)

# Set up session service and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=recon_agent,
    app_name="recon_app",
    session_service=session_service
)
USER_ID = "user_recon"
SESSION_ID = "session_recon"

async def execute(request):
    # Create or get session
    session_service.create_session(
        app_name="recon_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Extract target URL from the request if available
    target_url = request.get('target_url', '')
    
    # Create a prompt based on the input
    if target_url:
        prompt = f"Scan {target_url}"
    else:
        prompt = "I need to scan a website. Please extract the URL from my request."
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    # Execute the agent and handle the response
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            # The response might contain natural language, so we look for scan results
            # in tool outputs rather than parsing the response text
            
            # Check if the scan was successfully executed (via tool outputs)
            tool_outputs = event.get_tool_results()
            if tool_outputs:
                for output in tool_outputs:
                    if output.get('tool_name') == 'run_security_scan':
                        # Return the scan results
                        return {
                            "status": "success",
                            "message": f"Reconnaissance completed for {target_url}",
                            "scan_results": output.get('output', {})
                        }
            
            # If no tool was executed, return the agent's response
            return {
                "status": "info", 
                "message": response_text
            }
    
    # If we get here, no final response was received
    return {
        "status": "error",
        "message": "Failed to get response from recon agent"
    }
