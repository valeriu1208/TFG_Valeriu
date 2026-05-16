from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
from TFG_QSERVER.QuantumServer import TypeQ
from Decision_Algorithm.allocation import LegacyService, LegacytoQuantumRequest
app = FastAPI()

server = TypeQ.server
server1 = TypeQ.server1
server2 = TypeQ.server2


@app.get("/status")
def get_status():
    save_status = server.available_resources
    save1_status = server1.available_resources
    save2_status = server.available_resources
    total_qubits = save_status["qbits"] + save1_status["qbits"] + save2_status["qbits"]
    result =  {
            "available_resources": total_qubits
            }
    return result



####@app.post("/release_resources")
#def release_resources(request: LegacytoQuantumRequest):
#    available_resources = server.get_available_resources()
#    available_resources["qbits"] += request.qbits
#    available_resources["circuit_depth"] += request.circuit_depth
#    available_resources["qstorage"] += request.qstorage
#    return {"message": "Resources released successfully", "available_resources": available_resources}##

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

