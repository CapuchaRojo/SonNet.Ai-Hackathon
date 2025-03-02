import numpy as np
import time
import threading
import random
import networkx as nx
import blender_python_api as blender
import speedtest
import requests
import google.auth
from google.auth.transport.requests import Request
import ee  # Google Earth Engine API
from esp32_lora import ESP32_LoRa

# Initialize Google Earth Engine
ee.Initialize()

# Swarm Configuration
SWARM_SIZE = 5
SWARM_RANGE_KM = 2  # LoRa transmission range

# Setup Ookla Speed Test
def check_network_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
    ping = st.results.ping
    return download_speed, upload_speed, ping

# Define AI Agent Class
class AI_Agent:
    def __init__(self, id, role, location):
        self.id = id
        self.role = role
        self.status = "inactive"
        self.location = location
        self.last_heartbeat = time.time()
        self.lora = ESP32_LoRa(node_id=id, frequency=915e6)

    def heartbeat(self):
        self.last_heartbeat = time.time()
        print(f"Agent {self.id} - Heartbeat sent")

    def pulse_sync(self, leader):
        if time.time() - self.last_heartbeat > 5:
            self.heartbeat()
        if leader:
            print(f"Agent {self.id} - Syncing with leader {leader.id}")

    def send_lora_message(self, target_agent):
        """ Send message via LoRa """
        signal_strength = self.lora.transmit(target_agent.id)
        print(f"Agent {self.id} -> {target_agent.id} | Signal Strength: {signal_strength} dBm")

# Define Leader Agent
class LeaderAgent(AI_Agent):
    def __init__(self, id, location):
        super().__init__(id, role="leader", location=location)
        self.agents = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def manage_swarm(self):
        print(f"Leader {self.id} - Managing swarm")
        for agent in self.agents:
            agent.pulse_sync(self)
            agent.send_lora_message(self)

    def run(self):
        while True:
            self.manage_swarm()
            time.sleep(5)

# Create Swarm with ESP32 LoRa
leader = LeaderAgent(id=1, location=[45.5231, -122.6765])  # Portland as test location
swarm_agents = [AI_Agent(id=i, role="worker", location=[45.5231 + (i * 0.001), -122.6765 + (i * 0.001)]) for i in range(2, SWARM_SIZE+2)]
for agent in swarm_agents:
    leader.add_agent(agent)

# Run Leader in Background Thread
leader_thread = threading.Thread(target=leader.run)
leader_thread.start()

# Google Earth Engine Visualization
def visualize_connectivity():
    """ Overlay agent locations on a satellite map """
    points = [ee.Geometry.Point(agent.location) for agent in swarm_agents]
    feature_collection = ee.FeatureCollection(points)
    map_layer = ee.Image().paint(feature_collection, 2, 3)
    print("Swarm visualization updated in Google Earth Engine.")

# Blender Wave Propagation Simulation
def generate_wave_animation():
    """ Use Blender to simulate LoRa wave propagation """
    blender.initialize()
    blender.create_wave_animation(frequency=915e6, range_km=SWARM_RANGE_KM)
    print("Blender wave animation generated.")

# Network Speed Monitoring & n8n Automation
def monitor_network():
    while True:
        download_speed, upload_speed, ping = check_network_speed()
        print(f"Network Speed | Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps | Ping: {ping} ms")
        
        # Send data to n8n for automation
        requests.post("http://localhost:5678/webhook/network_status", json={
            "download_speed": download_speed,
            "upload_speed": upload_speed,
            "ping": ping
        })
        time.sleep(10)

network_thread = threading.Thread(target=monitor_network)
network_thread.start()

# Run Visualizations
visualize_connectivity()
generate_wave_animation()
