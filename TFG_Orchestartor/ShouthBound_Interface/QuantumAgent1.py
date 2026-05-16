from fastapi import FastAPI, HTTPException
from TFG_QSERVER.QuantumServer import TypeQ
app = FastAPI

server4 = TypeQ.server3
server5 = TypeQ.server4
server6 = TypeQ.server5
server7 = TypeQ.server6


@app.get("/status")
def get_status():
    save_status = server4.available_resources
    save1_status = server5.available_resources
    save2_status = server6.available_resources
    save3_status = server7.available_resources
    total_qubits = save_status["qbits"] + save1_status["qbits"] + save2_status["qbits"] + save3_status["qbits"]
    result = {
        "available_resources": total_qubits
        }
    return result