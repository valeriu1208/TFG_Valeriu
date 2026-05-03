from fastapi import HTTPException
from pydantic import BaseModel
import math
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
        self.servers = [serverQuantum, serverQuantum1]
        

    def FirstFit(self, app):
        server_list = list_servers()
        self.server_DevStack = server_list[0]  # list of server objects
        self.data_DevStack = {s["id"]: s for s in server_list[1]}  # dict keyed by server id
        self.number_of_servers = server_list[2]

        if self.number_of_servers == 0:# if server is empty, allocate directly
            flavor = flavors.flavor2 if (app.cpu > 1 or app.memory > 1024) else flavors.flavor1
            result = create_server(
                name=app.service_name,
                image_name=Images.image1.name,
                flavor_name=flavor.name,
                network_name="TFG"
            )
            if result is not None:
                return {
                    "status": "allocated",
                    "type": "classical",
                    "server_id": result
                }
            
        for server in self.server_DevStack:#check first the status of the Desvtack provisiong server, and then go for legacy and then quantum
            server_data = self.data_DevStack.get(server.id)
            if server_data is None:
                continue
            has_cpu = server_data["cpu"] >= app.cpu # change with gnocchi metrics / this makes no sense
            has_memory = server_data["memory"] >= app.memory # change with gnocchi metrics / this makes no sense

            if has_cpu and has_memory:
                
                if app.cpu > 1 or app.memory > 1024:
                    flavor = flavors.flavor2
                else:
                    flavor = flavors.flavor1

                result = create_server(
                    name=app.service_name,
                    image_name=Images.image1.name,
                    flavor_name=flavor.name,
                    network_name="TFG"
                )
                if result is not None:
                    return {
                        "status": "allocated",
                        "type": "classical",
                        "server_id": result
                    }
        raise HTTPException(status_code=400, detail="FNo suitable allocation found for the service.")
class DeleteAlgorithm:
    @staticmethod
    def GetServerIdFromName(server_name: str):
        servers_deployed = list_servers()
        data_list = servers_deployed[1]  # [name, id, cpu, memory]
        for server in data_list:
            if server["name"] == server_name:
                print(f"Server found: {server['name']}, ID: {server['id']}")
                return server["id"]
        
        print(f"Server with name '{server_name}' not found.")
        raise HTTPException(status_code=404, detail=f"Server with name '{server_name}' not found.")
        
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








   