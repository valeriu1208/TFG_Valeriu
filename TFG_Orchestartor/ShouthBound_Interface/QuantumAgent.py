from fastapi import FastAPI
import uvicorn
from TFG_QSERVER.QuantumServer import TypeQ

app = FastAPI()

AGENT_Servers = {
    1: {"Quantum_Computer1": TypeQ.server, "Quantum_Computer2": TypeQ.server1, "Quantum_Computer3": TypeQ.server2}
}

@app.get("/status")
def get_status():
    result =  {
        name: s.available_resources
        for name, s in AGENT_Servers[1].items()
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

