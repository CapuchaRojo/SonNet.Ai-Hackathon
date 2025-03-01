import random
import base64
import hashlib
from cryptography.fernet import Fernet

# Generate encryption key using Fernet
def generate_key():
    return Fernet.generate_key()

# Encrypt data
def encrypt_data(data, key):
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

# Simulate data packet in a sonar wave
def simulate_sonar_wave(terrain, data_packet):
    print("Simulating sonar wave propagation...")
    # Simulate how the sonar wave travels
    distance = random.uniform(10, 100)  # meters
    time_taken = distance / 340  # Speed of sound in air (340 m/s)
    print(f"Sonar wave traveling {distance:.2f} meters, will take {time_taken:.2f} seconds to reach terrain.")
    
    # Propagate wave towards target (Lesotho High School in this case)
    print(f"Packet sent to terrain: {terrain}")
    return data_packet

# Main function to simulate data transmission
def main():
    terrain = "Lesotho High School"
    data = "This is confidential data from SonNet.AI"
    key = generate_key()
    encrypted_data = encrypt_data(data, key)

    # Simulate sonar wave transmission
    packet = simulate_sonar_wave(terrain, encrypted_data)
    print(f"Encrypted packet: {base64.b64encode(packet).decode()}")

main()
