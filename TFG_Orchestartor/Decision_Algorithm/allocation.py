from fastapi import HTTPException
from pydantic import BaseModel
import math
from Decision_Algorithm import App
from Resources import flavors,Images
from ShouthBound_Interface.OpenStackConnection import create_server,list_servers
from TFG_PythonQAgent import QuantumServer

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
serverQuantum = QuantumServer.TypeQ.server
serverQuantum1 = QuantumServer.TypeQ.server1

class AllocationAlgorithm:
    def __init__(self):
        server_list = list_servers()
        self.server_DevStack = server_list[0]  # list of server objects
        self.data_DevStack = {s["id"]: s for s in server_list[1]}  # dict keyed by server id
        self.servers = [serverQuantum, serverQuantum1]
        

    def FirstFit(self, app):
        
        for server in self.server_DevStack:#check first the status of the Desvtack provisiong server, and then see if do the fit in quantum or legacy
            server_data = self.data_DevStack.get(server.id)
            if server_data is None:
                continue
            has_cpu = server_data["cpu"] >= app.cpu
            has_memory = server_data["memory"] >= app.memory

            if has_cpu and has_memory:
                # Decide flavor based on resource requirements
                if app.cpu > 1 or app.memory > 1024:
                    flavor = flavors.flavor2
                else:
                    flavor = flavors.flavor1

                result = create_server(
                    name=app.service_name,
                    image_name=Images.image1,
                    flavor_name=flavor,
                    network_name="TFG"
                )
                if result is not None:
                    return {
                        "status": "allocated",
                        "type": "classical",
                        "server_id": result
                    }
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
    return requested_resources
def create_quantum_server(request: LegacytoQuantumRequest):

    available_resources = serverQuantum.get_available_resources()
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








   