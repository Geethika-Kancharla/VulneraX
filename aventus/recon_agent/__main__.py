import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from common.a2a_server import create_app
from aventus.recon_agent.recon_agent import execute
import uvicorn

def main():
    # Create a simple class to match the expected API
    Agent = type("Agent", (), {"execute": execute})
    
    # Create the FastAPI app
    app = create_app(agent=Agent())
    
    # Run the app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)  # Using port 8004 for recon agent

if __name__ == "__main__":
    main()
