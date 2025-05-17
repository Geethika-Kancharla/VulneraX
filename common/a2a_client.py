import httpx
import logging

async def call_agent(url, payload):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)  # Reduced timeout for faster failure
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError as e:
        logging.error(f"Failed to connect to service at {url}: {str(e)}")
        return {"status": "error", "message": f"Service unavailable: {url}"}
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error from service at {url}: {str(e)}")
        return {"status": "error", "message": f"Service error: {e.response.status_code}"}
    except Exception as e:
        logging.error(f"Unexpected error calling service at {url}: {str(e)}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}