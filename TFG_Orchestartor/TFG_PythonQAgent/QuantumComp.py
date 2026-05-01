from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
import math
from QuantumServer import QuantumServer2, TypeQ
from Decision_Algorithm.allocation import LegacyService, LegacytoQuantumRequest
#: queue depending on resources, mainly by qubits, but also by circuit depth and shots
app = FastAPI()

server = TypeQ.server
server1 = TypeQ.server1



@app.get("/status")
def get_status():
    return {"available_resources": server.available_resources}
def get_status1():
    return {"available_resources": server1.available_resources}

@app.post("/release_resources")
def release_resources(request: LegacytoQuantumRequest):
    available_resources = server.get_available_resources()
    available_resources["qbits"] += request.qbits
    available_resources["circuit_depth"] += request.circuit_depth
    available_resources["qstorage"] += request.qstorage
    return {"message": "Resources released successfully", "available_resources": available_resources}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

