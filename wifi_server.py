import socket
from picarx import Picarx
import threading
import time

# Initialize PicarX
px = Picarx()

HOST = "192.168.1.209"  # IP address of your Raspberry PI
PORT = 65432             # Port to listen on (non-privileged ports are > 1023)

# Initialize variables to store the car's state
current_speed = 0
last_direction = "STOP"
is_moving = False  # Track if the car is currently moving

# Function to get Raspberry Pi temperature
def get_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        temp = float(f.read()) / 1000  # Convert to Celsius
    return temp

# Function to send data to the client
def send_data(client):
    global current_speed, last_direction
    while True:
        # Send data only when speed or direction changes
        if current_speed or last_direction != "STOP":
            distance = px.get_distance()
            temperature = get_temperature()
            data_str = f"Speed: {current_speed}, Distance: {distance}, Direction: {last_direction}, Temperature: {temperature:.2f}"
            try:
                client.sendall(data_str.encode())
            except (BrokenPipeError, ConnectionResetError):
                print("Client disconnected, stopping data send.")
                break
        
        time.sleep(1)  # Check every second

def handle_client(client):
    global current_speed, last_direction, is_moving
    try:
        while True:
            data = client.recv(1024)  # Receive 1024 bytes of message in binary format
            
            if not data:
                print("Client disconnected.")
                break  # Exit the loop if the client disconnects

            command = data.decode().strip()  # Decode the received bytes
            print("Received command:", command)
            
            # Control the car based on the command
            if command == "87":  # W key
                if last_direction != "FORWARD":
                    last_direction = "FORWARD"
                    current_speed = 50
                    px.set_dir_servo_angle(0)
                    is_moving = True
                if is_moving:
                    px.forward(current_speed)  # Keep moving forward
                print("Moving Forward")
            elif command == "83":  # S key
                if last_direction != "BACKWARD":
                    last_direction = "BACKWARD"
                    current_speed = 50
                    is_moving = True
                if is_moving:
                    px.backward(current_speed)  # Keep moving backward
                print("Moving Backward")
            elif command == "65":  # A key
                if last_direction != "LEFT":
                    last_direction = "LEFT"
                    current_speed = 50
                    is_moving = True
                if is_moving:
                    px.set_dir_servo_angle(-30)  # Turn left
                    px.forward(current_speed)  # Keep moving left
                print("Turning Left")
            elif command == "68":  # D key
                if last_direction != "RIGHT":
                    last_direction = "RIGHT"
                    current_speed = 50
                    is_moving = True
                if is_moving:
                    px.set_dir_servo_angle(30)  # Turn right
                    px.forward(current_speed)  # Keep moving right
                print("Turning Right")
            elif command == "STOP":  # Custom stop command
                if last_direction != "STOP":
                    last_direction = "STOP"
                    current_speed = 0
                    is_moving = False
                    px.stop()  # Stop the car
                print("Stopping Car")
            else:
                print("Invalid command")
            
    finally:
        # Stop the car when the client disconnects
        px.stop()
        print("Client disconnected, stopping car.")
        client.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print("Server listening on {}:{}".format(HOST, PORT))

    try:
        while True:
            client, clientInfo = s.accept()
            print("Connected by:", clientInfo)
            
            # Start a thread for sending data
            threading.Thread(target=send_data, args=(client,), daemon=True).start()
            # Handle the client connection in the main thread
            handle_client(client)

    except Exception as e:
        print("Error:", e)
    finally:
        print("Closing socket")
        s.close()