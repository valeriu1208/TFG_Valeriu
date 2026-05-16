import requests

class QuantumServer:
    def __init__(self, name: str):
        self.name = name
        self.resources = {}
    @property
    def available_qbits(self):
        return self.resources.get("qbits",0)
    @property
    def available_circuit_depth(self):
        return self.resources.get("circuit_depth",0)
    @property
    def available_shots(self):
        return self.resources.get("shots",0)
    @property
    def available_qstorage(self):
        return self.resources.get("qstorage",0)
class QuantumAgent:
    def __init__(self, name: str, url:str, quantum_rack: list):
        self.name = name
        self.url = url
        self.rack = quantum_rack
    def refresh(self):
        try:
            r = requests.get(f"{self.url}/status", timeout= 3) #dependig on the url it will be Agnet 1, 2, 3, hitting all qcluster resources at the moment
            r.raise_for_status()
            data = r.json()
            for servers in self.rack:
                servers.resources = data.get(servers.name,{})
            
        except requests.exceptions.RequestException:
            for servers in self.rack:
                servers.resources = {}
    @property
    def available_qbits(self):
        return sum(s.available_qbits for s in self.rack)
    @property
    def available_circuit_depth(self):
        return sum(s.available_circuit_depth for s in self.rack)
    @property
    def available_shots(self):
        return sum(s.available_shots for s in self.rack)
    @property
    def available_qstorage(self):
        return sum(s.available_qstorage for s in self.rack)

class QCluster:
    def __init__(self, name: str, agent: list):
        self.name = name
        self.agent = agent
    def refresh(self):
        for agent in self.agent:
            agent.refresh()
        

Quantum_Cluster1 = QCluster(
    name = "Quantum_Cluster",
    agent= [
        QuantumAgent(
            name= "Quantum_Agent1",
            url = "http://0.0.0.0:8001",
            quantum_rack=[
            QuantumServer( name =  "Quantum_Computer1"),
            QuantumServer( name =  "Quantum_Computer2"),
            QuantumServer( name =  "Quantum_Computer3")
            ],
        ),
        QuantumAgent(
            name= "Quantum_Agent2",
            url = "http://0.0.0.0:8002",
            quantum_rack=[
            QuantumServer( name =  "Quantum_Computer4"),
            QuantumServer( name =  "Quantum_Computer5"),
            QuantumServer( name =  "Quantum_Computer6"),
            QuantumServer( name =  "Quantum_Computer7")
            ],
        ),
        QuantumAgent(
            name= "Quantum_Agent3",
            url = "http://0.0.0.0:8003",
            quantum_rack=[
            QuantumServer( name =  "Quantum_Computer8"),
            QuantumServer( name =  "Quantum_Computer9"),
            QuantumServer( name =  "Quantum_Computer10")
            ],
        )
    ]
)