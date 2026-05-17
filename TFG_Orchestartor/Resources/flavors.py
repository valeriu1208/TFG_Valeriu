
class FLavors:
    
    def __init__(self,id: str,name: str, cpu: int, ram: int, disk: int):
        self.id = id
        self.name = name
        self.cpu = cpu
        self.ram = ram
        self.disk = disk
flavor1 = FLavors(id="1", name="ds1G", cpu=1, ram=1024, disk=10)
flavor2 = FLavors(id="2", name="ds2G", cpu=2, ram=2048, disk=20)
    