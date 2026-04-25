from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
import math
import App
from Resources import flavors,Images
from pathlib import Path
from ShouthBound_Interface.OpenStackConnection import create_server, delete_server
from NorthBound_Interface.process import process_request, process_status, process_token

class AllocationAlgorithm:
    App = App.App()
    flavors = flavors.flavors()
    Images = Images.Images()
    app_counter: int = 0
    openstack_enabled: bool = False
    server: list = []
    rack: list = []
    qComputer: list = []
    qNodes: list = []
    queue: list = []
    def __init__(self, App: App.App, flavors: flavors.flavors, Images: Images.Images, openstack_enabled: bool):
        self.App = App
        self.flavors = flavors
        self.Images = Images
        self.openstack_enabled = openstack_enabled




