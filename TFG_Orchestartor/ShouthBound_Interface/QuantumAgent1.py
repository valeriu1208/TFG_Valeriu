from fastapi import FastAPI
import uvicorn
from TFG_QSERVER.QuantumServer import TypeQ

app = FastAPI()

AGENT_SERVERS = {
    2: {"Quantum_Computer4": TypeQ.server3, "Quantum_Computer5": TypeQ.server4, "Quantum_Computer6": TypeQ.server5, "Quantum_Computer7" : TypeQ.server6}
}

@app.get("/status")
def get_status():
    result = {
        name: s.available_resources
        for name, s in AGENT_SERVERS[2].items()
    }
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)