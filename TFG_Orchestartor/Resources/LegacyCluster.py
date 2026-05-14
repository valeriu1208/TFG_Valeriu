from ShouthBound_Interface.OpenStackConnection import get_available_resources_rack

class ServerNode:

    def __init__(self, name: str, hostname: str, rack_name: str, az_name: str):
        self.name = name
        self.hostname = hostname
        self.rack_name = rack_name
        self.az_name = az_name
        self.resources = {}

    def refresh(self):
        data = get_available_resources_rack(self.rack_name)
        self.resources = data.get(self.rack_name, {})
    
    @property
    def free_vcpus(self):
        return self.resources.get("VCPU_total", 0) - self.resources.get("VCPU_used", 0)

    @property
    def free_memory(self):
        return self.resources.get("RAM_total", 0) - self.resources.get("RAM_used", 0)

    @property
    def free_disk(self):
        return self.resources.get("DISK_total", 0) - self.resources.get("DISK_used", 0)
    @property
    def vcpus(self):
        return self.resources.get("VCPU_total", 0)

class Rack:
    def __init__(self, name: str, az_name: str, nodes: list):
        self.name = name
        self.az_name = az_name
        self.nodes = nodes

    def refresh(self):
        for node in self.nodes:
            node.refresh()

class Cluster:
    def __init__(self, name: str, racks: list):
        self.name = name
        self.racks = racks

    def refresh(self):
        for rack in self.racks:
            rack.refresh()

LegacyCluster1 = Cluster(
    name="LegacyCluster1",
    racks=[
        Rack(
            name="polaar",
            az_name="rack1",
            nodes=[
                ServerNode(name="controller", hostname="controller-node", az_name="polaar", rack_name="polaar"),
            ]
        ),
        Rack(
            name="m3node",
            az_name="rack2",
            nodes=[
                ServerNode(name="compute", hostname="compute-node", az_name="m3node", rack_name="m3node"),
            ]
        ),
    ]
)