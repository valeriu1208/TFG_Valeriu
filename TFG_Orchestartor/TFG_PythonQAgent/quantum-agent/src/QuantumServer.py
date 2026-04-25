class QuantumServer:
    def __init__(self, host: str, service_name: str, cpu: int, memory: int, storage: int):
        self.host = host
        self.service_name = service_name
        self.cpu = cpu
        self.memory = memory
        self.storage = storage
    
    def get_host(self) -> str:
        return self.host
    def set_host(self, host: str):
        self.host = host
    def get_service_name(self) -> str:
        return self.service_name
    def set_service_name(self, service_name: str):
        self.service_name = service_name
