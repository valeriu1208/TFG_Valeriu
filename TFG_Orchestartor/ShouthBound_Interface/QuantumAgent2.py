from fastapi import FastAPI, HTTPException
from TFG_QSERVER.QuantumServer import TypeQ
app = FastAPI

server8 = TypeQ.server7
server9 = TypeQ.server8
server10 = TypeQ.server9


@app.get("/status")
def get_status():
    save_status = server8.available_resources
    save1_status = server9.available_resources
    save2_status = server10.available_resources
    total_qubits = save_status["qbits"] + save1_status["qbits"] + save2_status["qbits"]
    result = {
        "available_resources": total_qubits
        }
    return result