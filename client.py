import socket
import argparse
import threading

parser = argparse.ArgumentParser(description='Description of your script.')
parser.add_argument('host', type=str, help='Hostname or IP address')
parser.add_argument('port', type=int, help='Port number')
args = parser.parse_args()
HOST = args.host  # The server's hostname or IP address
PORT = args.port  # The port used by the server

def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024).decode("utf-8")
        print(data)

def main():
    # Create a socket object for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((HOST, PORT))
        print("Connected to the chat server.")

        # Prompt the user to enter a username
        username = input("Enter your username: ")
        client_socket.send(username.encode("utf-8"))

        # Start a separate thread to continuously receive messages
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True  # Daemonize the thread to exit when the main program exits
        receive_thread.start()

        # Start sending messages
        while True:
            message = input("Enter your message:")
            client_socket.send(message.encode("utf-8"))

            if message.lower() == "/exit":
                print("Disconnected from the chat server.")
                break

    except Exception as e:
        print("An error occurred: {0}".format(e))
    finally:
        # Close the socket when done
        client_socket.close()

if __name__ == "__main__":
    main()
