from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
import math
#: queue depending on resources, mainly by qubits, but also by circuit depth and shots
app = FastAPI()
class LegacyService(BaseModel):
    service_name: str
    cpu: int
    memory: int
    storage: int
    execution_time: int
class LegacytoQuantumRequest(BaseModel):
    qbits: int
    shots: int
    circuit_depth: int
    qstorage: int
class QuantumServer:
    def __init__(self, host: str, qbits: int, shots: int, circuit_depth: int, qstorage: int):
        self.host = host
        self.qbits = qbits
        self.shots = shots
        self.circuit_depth = circuit_depth
        self.qstorage = qstorage
        self.available_resources = {
            "qbits": qbits,
            "shots": shots,
            "circuit_depth": circuit_depth,
            "qstorage": qstorage
        }
        self.requested_resources = {
            "qbits": 0,
            "shots": 0,
            "circuit_depth": 0,
            "qstorage": 0
        }
    def get_host_ip(self) -> str:
        return self.host
    def set_host_ip(self, host: str):
        self.host = host
    def get_qbits(self) -> int:
        return self.qbits
    def set_qbits(self, qbits: int):
        self.qbits = qbits
    def get_shots(self) -> int:
        return self.shots
    def set_shots(self, shots: int):
        self.shots = shots
    def get_circuit_depth(self) -> int:
        return self.circuit_depth
    def set_circuit_depth(self, circuit_depth: int):
        self.circuit_depth = circuit_depth
    def get_qstorage(self) -> int:
        return self.qstorage
    def set_qstorage(self, qstorage: int):
        self.qstorage = qstorage
    def get_available_resources(self) -> dict:
        return self.available_resources
    def set_available_resources(self, available_resources: dict):
        self.available_resources = available_resources
    def get_requested_resources(self) -> dict:
        return self.requested_resources
    def set_requested_resources(self, requested_resources: dict):
        self.requested_resources = requested_resources
   
server = QuantumServer(
    host="192.168.1.200", 
    qbits=127, 
    shots=10000, 
    circuit_depth=5000, 
    qstorage= (127 * 10000 // 8)
)
server1 = QuantumServer(
    host="192.168.1.201",
    qbits=127,
    shots=10000,
    circuit_depth=5000,
    qstorage=(127 * 10000 // 8)
)

@app.get("/status")
def get_status():
    return {"available_resources": server.available_resources}
def get_status1():
    return {"available_resources": server1.available_resources}

@app.post("/legacy-to-quantum")
def legacy_to_quantum(petition: LegacyService):
    ram_bytes = petition.memory * 1024 * 1024 * 1024
    bytes_per_amplitude = 16
    if ram_bytes == 0:
        raise HTTPException(status_code=400, detail="Memory must be greater than 0")
    else:
        qbits = math.floor(math.log2(ram_bytes / bytes_per_amplitude))
    if qbits <= 0:
        raise HTTPException(status_code=400, detail="Calculated qbits must be greater than 0")
    else:
        shots = max(1024, petition.cpu * 100)
        circuit_depth = petition.cpu * 10
        qstorage = (qbits * shots) // 8
    requested_resources = LegacytoQuantumRequest(
            qbits=qbits,
            shots=shots,
            circuit_depth=circuit_depth,
            qstorage=qstorage
        )
    return create_quantum_server(requested_resources)

@app.post("/quantum_server")
def create_quantum_server(request: LegacytoQuantumRequest):

    available_resources = server.get_available_resources()
    if (request.qbits > available_resources["qbits"] or
        request.shots > available_resources["shots"] or
        request.circuit_depth > available_resources["circuit_depth"] or
        request.qstorage > available_resources["qstorage"]):
        raise HTTPException(status_code=400, detail="Requested resources exceed available resources")
    else:
        available_resources["qbits"] -= request.qbits
        available_resources["circuit_depth"] -= request.circuit_depth
        available_resources["qstorage"] -= request.qstorage
        return {"message": "Quantum server created successfully", "remaining_resources": available_resources}
@app.post("/release_resources")
def release_resources(request: LegacytoQuantumRequest):
    available_resources = server.get_available_resources()
    available_resources["qbits"] += request.qbits
    available_resources["circuit_depth"] += request.circuit_depth
    available_resources["qstorage"] += request.qstorage
    return {"message": "Resources released successfully", "available_resources": available_resources}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

