
class Application:
    def __init__(self, app_name: str, cpu: int, ram: int, storage: int, execution_time: int):
        self.name = app_name
        self.cpu = cpu
        self.memory = ram
        self.storage = storage
        self.execution_time = execution_time
