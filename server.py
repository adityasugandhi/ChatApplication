# Aditya Sugandhi (AS22CQ) Author Name

import socket
import select
import random
import threading
import time
import sys
import os


try:
    HOST = socket.gethostname()
    socket.gethostbyname(HOST)  # check if HOST is resolvable
except (socket.error, socket.gaierror):
    HOST = 'localhost'

PORT = random.randint(0, 65535)

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(10)
        self.clients = {}
        self.should_stop = False
        self.client_sockets = []
        self.server_messages = []
        self.running = True  # Flag to track server status
        print("Chat server is listening on port and Host ...", PORT, HOST)

    def broadcast_message(self, message):
        for client_sock in self.client_sockets:
            try:
                client_sock.send(message.encode("utf-8"))
            except Exception as e:
                print(e)
                client_sock.close()
                self.client_sockets.remove(client_sock)

    def send_server_messages(self):
        while self.running:  # Run as long as the server is active
            if self.server_messages:
                message = self.server_messages.pop(0)
                self.broadcast_message(message)

    def handle_client(self, client_socket, username):
        while True:
            try:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    username = self.clients[client_socket]
                    print("{} has disconnected.".format(username))
                    self.client_sockets.remove(client_socket)
                    del self.clients[client_socket]
                    break

                self.broadcast_message("{}: {}".format(self.clients[client_socket], data))
                print("{} : {}".format(self.clients[client_socket], data))
            except Exception as e:
                print(e)
                client_socket.close()
                self.client_sockets.remove(client_socket)
                del self.clients[client_socket]
                break

    def client_handler(self, client_socket, username):
        self.clients[client_socket] = username  # Store the username with client socket
        self.client_sockets.append(client_socket)
        print("New connection from {} as {}".format(client_socket.getpeername(), username))
        self.handle_client(client_socket, username)

    def run(self):
        server_message_thread = threading.Thread(target=self.send_server_messages)
        server_message_thread.daemon = True
        server_message_thread.start()

        while self.running:
            if self.should_stop:
                break
            readable, _, _ = select.select([self.server_socket], [], [])
            for sock in readable:
                if sock is self.server_socket:
                    client_socket, _ = self.server_socket.accept()
                    username = client_socket.recv(1024).decode("utf-8")
                    client_thread = threading.Thread(target=self.client_handler, args=(client_socket, username))
                    client_thread.start()
        self.stop_server()

    def send_message_to_all_clients(self, message):
        self.server_messages.append(message)

    def server_input_thread(self):
        while self.running:
            message = input("Enter a message to broadcast to all clients (Type '/exit' to stop the server): ")
            if message == '/exit':
                self.should_stop= True
                self.stop_server()
                break
            else:
                self.send_message_to_all_clients("Server: {}".format(message))

    def stop_server(self):
        self.running = False
        self.server_socket.close()
        # Disconnect all clients
        for client_sock in self.client_sockets:
            try:
                client_sock.send("Server is shutting down. Goodbye!".encode("utf-8"))
                client_sock.close()

            except:
                pass
                print("Error Occured the socket is still open")
        self.client_sockets.clear()
        print("Server has been stopped.")
        time.sleep(2)
        os._exit(0)
        

if __name__ == "__main__":
    S = Server()

    #  Thread to monitor server status
    def check_server_status():
        while True:
            time.sleep(1)
            if not S.running:
                break

    status_thread = threading.Thread(target=check_server_status)
    status_thread.daemon = True
    status_thread.start()

    input_thread = threading.Thread(target=S.server_input_thread)
    input_thread.daemon = True
    input_thread.start()

    try:
        S.run()
    except KeyboardInterrupt:
        S.stop_server()

