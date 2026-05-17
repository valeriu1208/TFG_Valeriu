from fastapi import HTTPException
from pydantic import BaseModel
import math
from Resources import flavors,Images,LegacyCluster, QuantumCLuster
from ShouthBound_Interface.OpenStackConnection import create_server,list_servers

quantum_list: dict =  {}
total_deployed = 0
class LegacyService(BaseModel):
    service_name: str
    cpu: int
    memory: int
    storage: int
    force_quantum: bool = False
   # execution_time: int
class LegacytoQuantumRequest(BaseModel):
    service_name: str
    #id: int
    qbits: int
    shots: int
    circuit_depth: int
    qstorage: int
   # execution_time: int

class AllocationAlgorithm:

    def FirstFit(self, app):
        #server_list = list_servers()
        #self.server_DevStack = server_list[0]  # list of server objects
        #self.data_DevStack = {s["id"]: s for s in server_list[1]}  # :id, {name, id, cpu, memory}
        #self.number_of_servers = server_list[2]
        global total_deployed
        LegacyCluster.LegacyCluster1.refresh()
        QuantumCLuster.Quantum_Cluster1.refresh()

        if not app.force_quantum:
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
                    total_deployed+=1
                    return  {"status": "allocated", "type": "classical", "node": target_node["node"].hostname, "server_id": result, "number of deploymetns": total_deployed}
            # now, it shall be allocated to the node that has less resources, also check storage , as the second node is less powerful ;;; Add memory checking, if its close to 80% of it's total stop allocating etc
            suitable = [c for c in candidates
            if c["free_vcpus"] >= app.cpu and c["free_memory"] >= app.memory and c["free_disk"] >= app.storage ] #keep only the available node
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
                    total_deployed +=1
                    return  {"status": "allocated", "type": "classical", "node": best_node["node"].hostname, "server_id": result, "number of vm deployed" : total_deployed}

        requested_resources = legacy_to_quantum(app)
        QuantumCandidates = []
        for agent in QuantumCLuster.Quantum_Cluster1.agent:
            for server in agent.rack:
                QuantumCandidates.append({
                "agent" :agent,
                "server" :server,
                "available_circuit_depth" :server.available_circuit_depth,
                "available_qbits" :server.available_qbits,
                "available_shots" :server.available_shots,
                "available_qstorage":server.available_qstorage
                })
        suitable = [c for c in QuantumCandidates
                    if c["available_qbits"] >= requested_resources.qbits
                    and c["available_shots"] >= requested_resources.shots
                    and c ["available_circuit_depth"] >= requested_resources.circuit_depth
                    and c ["available_qstorage"] >= requested_resources.qstorage]
        if suitable:
            best_agent = sorted(suitable, key = lambda c: (c["available_qbits"], c["available_shots"], c["available_circuit_depth"]), reverse= True)[0]
            result = create_quantum_server(best_agent["agent"],best_agent["server"],requested_resources)
            total_deployed +=1
            return result
class DeleteAlgorithm:
    @staticmethod
    def GetServerIdFromName(server_name: str):
        global total_deployed
        servers_deployed = list_servers()
        data_list = servers_deployed[1]  # [name, id, cpu, memory]
        for server in data_list:
            if server["name"] == server_name:
                print(f"Server found: {server['name']}, ID: {server['id']}")
                total_deployed -= 1
                return server["id"]
        print(f"Server with name '{server_name}' not found.")
        raise HTTPException(status_code=404, detail=f"Server with name '{server_name}' not found.")
    def DeleteQuantum(service_name: str):
        global total_deployed
        if service_name not in quantum_list:
            raise HTTPException(status_code=404, detail=f"Not found in quantum'{service_name}'")
        record = quantum_list.pop(service_name)   
        server = record["server"]                 
        resources = record["resources"]
        
        server.resources["qbits"] += resources["qbits"]
        server.resources["shots"] += resources["shots"]
        server.resources["circuit_depth"] += resources["circuit_depth"]
        server.resources["qstorage"] += resources["qstorage"]
        total_deployed -= 1
        return {
            "status": "released",
            "type": "quantum",
            "service_name": service_name,
            "agent": record["agent"].name,
            "server": server.name
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
            service_name= petition.service_name,
            qbits=qbits,
            shots=shots,
            circuit_depth=circuit_depth,
            qstorage=qstorage
        )
    return requested_resources
def create_quantum_server(agent ,server, request: LegacytoQuantumRequest):
    if (request.qbits > server.available_qbits or
        request.shots > server.available_shots or
        request.circuit_depth > server.available_circuit_depth or
        request.qstorage > server.available_qstorage):
        raise HTTPException(status_code=400, detail="Requested resources exceed available resources")
    quantum_list[request.service_name]= { 
        "agent": agent,
        "app_service_name": request.service_name,
        "server": server,
        "resource":{
            "qbits": request.qbits,
            "circuit_depth": request.circuit_depth,
            "shots": request.shots,
            "quantum storage": request.qstorage
        }
       
    }
    server.resources["qbits"] -= request.qbits
    server.resources["circuit_depth"] -= request.circuit_depth
    server.resources["shots"] -= request.shots
    server.resources["qstorage"] -= request.qstorage
    
    return {
        "status": "allocated",
        "type": "quantum",
        "agent": agent.name,
        "server": server.name,
        "app_name": request.service_name,
        "available_resources" : {
            "qbits": server.available_qbits,
            "circuit_depth": server.available_circuit_depth,
            "shots": server.available_shots,
            "qstorage": server.available_qstorage
        },
        "requested_resources": {
            "qbits": request.qbits,
            "circuit_depth": request.circuit_depth,
            "shots": request.shots,
            "qstorage": request.qstorage
        },
        "total_deployed": total_deployed
    }




   