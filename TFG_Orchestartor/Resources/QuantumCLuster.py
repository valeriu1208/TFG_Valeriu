import requests

class QuantumServer:
    def __init__(self, name: str):
        self.name = name

class QuantumAgent:
    def __init__(self, name: str, url:str, quantum_rack: list):
        self.name = name
        self.url
        self.resources = {}
        self.rack = quantum_rack
    def refresh(self):
        try:
            r = requests.get(f"{self.url}/status", timeout= 3) #dependig on the url it will be Agnet 1, 2, 3, hitting all qcluster resources at the moment
            r.raise_for_status()
            self.resources = r.json().get("available_resources", {})
        except requests.exceptions.RequestException:
            self.resources = {}
            self.resources = {}
    @property
    def available_qubits(self):
        return self.resources.get("qbits",0)
    @property
    def availabñe_circuit_depth(self):
        return self.resources.get("circuit_depth",0)
    @property
    def available_shots(self):
        return self.resources.get("shots",0)
    @property
    def available_qstorage(self):
        return self.resources.get("qstorage",0)
    @property
    def total_qbits(self):
        return self.resources.get("total_qbits",127)

class QCluster:
    def __init__(self, name: str, agent: list):
        self.name = name
        self.agent = agent
    def refresh(self):
        for agent in self.agents:
            agent.refresh()
        

Quantum_Cluster1 = QCluster(
    name = "Quantum_Cluster",
    agent= [
        QuantumAgent(
            name= "Quantum_Agent1",
            quantum_rack=[
            QuantumServer( name =  "Quantum_Computer1"),
            QuantumServer( name =  "Quantum_Computer2"),
            QuantumServer( name =  "Quantum_Computer3")
            ],
        ),
        QuantumAgent(
            name= "Quantum_Agent2",
            quantum_rack=[
            QuantumServer( name =  "Quantum_Computer4"),
            QuantumServer( name =  "Quantum_Computer5"),
            QuantumServer( name =  "Quantum_Computer6"),
            QuantumServer( name =  "Quantum_Computer7")
            ],
        ),
        QuantumAgent(
            name= "Quantum_Agent3",
            quantum_rack=[
            QuantumServer( name =  "Quantum_Computer8"),
            QuantumServer( name =  "Quantum_Computer9"),
            QuantumServer( name =  "Quantum_Computer10")
            ],
        )
    ]
)