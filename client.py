import socket

def connect_to_server():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Server IP and port
    server_ip = "192.168.0.129"  # Replace with the Raspberry Pi's IP address
    port = 12345

    # Connect to the server
    client_socket.connect((server_ip, port))
    print(f"Connected to server at {server_ip}:{port}")

    try:
        while True:
            # Get user input to send to the server
            message = input("Enter a message to send to the server (type 'exit' to quit): ")
            if message.lower() == "exit":
                break

            # Send the message to the server
            client_socket.send(message.encode())

            # Receive a response from the server
            response = client_socket.recv(1024).decode()
            print(f"Response from server: {response}")
    except KeyboardInterrupt:
        print("\nClient shutting down.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    connect_to_server()
