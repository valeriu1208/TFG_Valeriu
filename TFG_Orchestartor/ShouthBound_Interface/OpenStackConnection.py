import openstack
openstack.enable_logging(debug = True)

conn = openstack.connect(cloud='devstack') #: Via clouds.yaml file connection parameters
print("Connected to OpenStack successfully.")
def create_server(name: str, image_name: str, flavor_name: str, network_name: str):
    image = conn.compute.find_image(image_name)
    flavor = conn.compute.find_flavor(flavor_name)
    network = conn.network.find_network(network_name)

    if not image:
        print(f"Image '{image_name}' not found.")
        return
    if not flavor:
        print(f"Flavor '{flavor_name}' not found.")
        return
    if not network:
        print(f"Network '{network_name}' not found.")
        return

    server = conn.compute.create_server(
        name=name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}]
    )
    server = conn.compute.wait_for_server(server)
    print(f"Server '{name}' created successfully with ID: {server.id}")
    server_id = server.id
    return server_id
def delete_server(server_id: str):
    server = conn.compute.find_server(server_id)
    if not server:
        print(f"Server with ID '{server_id}' not found.")
        return

    conn.compute.delete_server(server)
    print(f"Server with ID '{server_id}' deleted successfully.")

def list_servers():
    serversInDevStack = list(conn.compute.servers())
    data_servers = []
    for server in serversInDevStack:
      
        flavor_info = server.flavor
        if "vcpus" in flavor_info:
            vcpus = flavor_info["vcpus"]
            ram = flavor_info["ram"]
        else:
            flavot = conn.compute.get_flavor(server.flavor["id"])
            vcpus = flavot.vcpus
            ram = flavot.ram
        data_servers.append({
            "name": server.name,
            "id": server.id,
            "cpu": vcpus,
            "memory": ram  
        })
    
    print(f"Number of servers in DevStack: {len(serversInDevStack)}")
    return serversInDevStack, data_servers, len(serversInDevStack)  # return server objects + data