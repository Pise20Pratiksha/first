#Code for the raspberrypi to add on raspberrypi editor (Server code)
import socket

def start_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to an IP and port
    host = "0.0.0.0"  # Listen on all available interfaces
    port = 12345      # Port number
    server_socket.bind((host, port))

    # Start listening for connections
    server_socket.listen(1)
    print(f"Server started on {host}:{port}. Waiting for a connection...")

    # Accept a connection
    conn, addr = server_socket.accept()
    print(f"Connected by: {addr}")

    try:
        while True:
            # Receive data from the client
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Received from client: {data}")

            # Process the data and send a response
            response = f"Server received: {data}"
            conn.send(response.encode())
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    start_server()
