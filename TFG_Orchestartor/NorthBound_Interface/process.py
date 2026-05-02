# connected to dashboard
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
import requests
from Decision_Algorithm.allocation import AllocationAlgorithm
QUANTUM_AGENT_URL = "http://127.0.0.1:8001/legacy-to-quantum"  # URL of the quantum agent server legacy-to-quantum endpoint
SERVER_URL = "http://127.0.0.1:8001/status"  # URL of the quantum agent server
DEVSTACK_URL = "http://192.168.1.157/metric" # URL of the Gnocchi API for metrics
KEYSTONE_URL = "http://192.168.1.157/identity/v3/auth/tokens" # URL of the Keystone API for authentication
DELETE_URL = "http://192.168.1.157/"

app = FastAPI()

class LegacyService(BaseModel):
    service_name: str
    cpu: int
    memory: int
    storage: int
    execution_time: int

class processRequest(BaseModel):
    legacy_service: LegacyService
    
@app.post("/process")
def process_request(request: LegacyService):
    #TODO: send request to fitting algorithm and process decision
    #TODO: inform dashboard about decision and status
    allocation = AllocationAlgorithm()
    allocation_algorithm = allocation.FirstFit(app=request)
    if allocation_algorithm is not None:
        return allocation_algorithm
    else:
        print("No suitable allocation found for the service.")
        raise HTTPException(status_code=400, detail="No suitable allocation found for the service.")

@app.get("/process/quantum_status")
def process_status():
    #TODO: send request to quantum agent and get status
    #TODO: send requesto to DeVstack and get status
    #: store status for fitting algorithm
    #TODO: display status on dashboard
    print("Getting status from our Hybrid Datacenter...")
    try:

        agent_response = requests.get(SERVER_URL)
        agent_response.raise_for_status()  # Check if the request was successful
        quantum_status = agent_response.json()

        return {
            "message": "Status retrieved successfully", 
                "quantum": quantum_status,

        }
    except requests.exceptions.RequestException as e:
        print("Error retrieving status from quantum agent:", e)
        raise HTTPException(status_code=500, detail=f"Error retrieving status {e}")
     # it needs to be added postman token to header
@app.post("/process/devstack_status")
def process_devstack_status():
    #TODO: send request to quantum agent and get status
    #TODO: send requesto to DeVstack and get status
    #: store status for fitting algorithm
    #TODO: display status on dashboard
    print("Getting status from our Hybrid Datacenter...")
    try:
        devstack_response = requests.get(DEVSTACK_URL)
        devstack_response.raise_for_status()  # Check if the request was successful
        devstack_status = devstack_response.json()
        return {
            "message": "Status retrieved successfully", 
                "devstack": devstack_status
        }
    except requests.exceptions.RequestException as e:
        print("Error retrieving status from quantum agent:", e)
        raise HTTPException(status_code=500, detail=f"Error retrieving status {e}")
     # it needs to be added postman token to header
# get token from postman and store it for future use
@app.post("/process/token")
def process_token():
    print("Getting token from Keystone...")

    payload = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "id": os.getenv("OPENSTACK_USER_ID"),
                            "password": os.getenv("OPENSTACK_PASSWORD"),
                                }
                                }
                            },
                "scope":{
                    "project": {
                        "id": os.getenv("OPENSTACK_PROJECT_ID")
                }           
                }
            }
        }
    try:
        response = requests.post(KEYSTONE_URL, json=payload)
        response.raise_for_status()  # Check if the request was successful
        token = response.headers.get("X-Auth-Token")
        print("Token from Keystone:", token)
        return {"message": "Token retrieved successfully", "token": token}
    except requests.exceptions.RequestException as e:
            print("Error retrieving token from Keystone:", e)
    raise HTTPException(status_code=500, detail="Error retrieving token from Keystone")



# send delete request to DeVstack to delete process
# send delete request to quantum agent to delete process
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)