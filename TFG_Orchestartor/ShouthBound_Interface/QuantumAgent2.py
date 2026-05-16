from fastapi import FastAPI
import uvicorn
from TFG_QSERVER.QuantumServer import TypeQ


app = FastAPI()

AGENT_servers = {
    3: {"Quantum_Computer8": TypeQ.server7, "Quantum_Computer9": TypeQ.server8, "Quantum_Computer10": TypeQ.server9}
}

@app.get("/status")
def get_status():
    return {
        name: s.available_resources
        for name, s in AGENT_servers[3].items()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)