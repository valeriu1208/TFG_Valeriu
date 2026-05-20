
class FLavors:
    
    def __init__(self,id: str,name: str, cpu: int, ram: int, disk: int):
        self.id = id
        self.name = name
        self.cpu = cpu
        self.ram = ram
        self.disk = disk
flavor1 = FLavors(id="1", name="ds1G", cpu=1, ram=1024, disk=10)
flavor2 = FLavors(id="2", name="ds2G", cpu=2, ram=2048, disk=20)
flavor3 = FLavors(id = "3", name = "ds4G", cpu = 4, ram = 4096, disk = 20)
flavor4 = FLavors(id = "4", name = "m1.medium", cpu = 4, ram = 4096, disk = 40)
flavor5 = FLavors(id = "5", name = "m1.large", cpu = 8, ram = 8192, disk = 80)
    