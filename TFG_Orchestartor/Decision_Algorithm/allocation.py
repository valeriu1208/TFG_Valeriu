from fastapi import HTTPException
from pydantic import BaseModel
import requests
import math
from Resources import flavors,Images,LegacyCluster, QuantumCLuster
from ShouthBound_Interface.OpenStackConnection import create_server,list_servers,get_available_resources_rack


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
    execution_time: int

class AllocationAlgorithm:

    def FirstFit(self, app):
        #server_list = list_servers()
        #self.server_DevStack = server_list[0]  # list of server objects
        #self.data_DevStack = {s["id"]: s for s in server_list[1]}  # :id, {name, id, cpu, memory}
        #self.number_of_servers = server_list[2]
        LegacyCluster.LegacyCluster1.refresh()
        QuantumCLuster.Quantum_Cluster1.refresh()
        vm_deployed: int = 0


        candidates = []
        for rack in LegacyCluster.LegacyCluster1.racks:
            for node in rack.nodes:
                candidates.append({
                "node": node,
                "rack": rack,
                "free_vcpus": node.free_vcpus,
                "free_memory": node.free_memory,
                "free_disk": node.free_disk,
                })
        all_empty = all(c["free_vcpus"] == c["node"].vcpus for c in candidates)
        if all_empty:
            target_node = candidates[0]
            result = create_server(
                name = app.service_name,
                image_name= Images.image1.name,
                flavor_name= flavors.flavor1.name,
                network_name= "TFG",
                az = target_node["rack"].az_name
            )
            if result:
                vm_deployed= vm_deployed + 1 
                return  {"status": "allocated", "type": "classical", "node": target_node["node"].hostname, "server_id": result}
        # now, it shall be allocated to the node that has less resources, also check storage , as the second node is less powerful ;;; Add memory checking, if its close to 80% of it's total stop allocating etc
        suitable = [c for c in candidates
        if c["free_vcpus"] >= app.cpu and c["free_memory"] >= app.memory ] #keep only the available node
        if suitable:
            best_node = sorted(suitable, key=lambda c: (c["free_vcpus"], c["free_memory"]), reverse=True)[0]
            result = create_server(
                name = app.service_name,
                image_name= Images.image1.name,
                flavor_name= flavors.flavor2.name,
                network_name= "TFG",
                az = best_node["rack"].az_name
            )
            if result:
                vm_deployed = vm_deployed + 1
                return  {"status": "allocated", "type": "classical", "node": best_node["node"].hostname, "server_id": result, "number of vm deployed" : vm_deployed}
        requested_resources = legacy_to_quantum(app)
        QuantumCandidates = []
        for agent in QuantumCLuster.Quantum_Cluster1.agent:
            QuantumCandidates.append({
            "agent" :agent,
            "available_circuit_depth": agent.available_circuit_depth,
            "available_qbits" :agent.available_qbits,
            "available_shots" :agent.available_shots,
            "available_qstorage": agent.available_qstorage
            })
        suitable = [c for c in QuantumCandidates
                    if c["available_qubits"] >= requested_resources["qbits"]
                    and c["available_shots"] >= requested_resources["shots"]
                    and c ["available_circuit_"] >= requested_resources["circuit_depth"]]
        if suitable:
            result = create_quantum_server(requested_resources)

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
def create_quantum_server(request: LegacytoQuantumRequest):# change

    available_resources = 1
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








   