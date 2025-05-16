import socket
import pickle
import threading

class NetworkManager:
    def __init__(self, is_server=False, server_ip='127.0.0.1', port=5555):
        self.is_server = is_server
        self.server_ip = server_ip
        self.port = port
        self.socket = None
        self.client_sockets = []
        self.running = False
    
    def start(self):
        """Start the network manager as either server or client"""
        self.running = True
        if self.is_server:
            self._start_server()
        else:
            self._connect_to_server()
    
    def _start_server(self):
        """Initialize and run the server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(2)  # Listen for 2 players
        
        # Start a thread to accept connections
        threading.Thread(target=self._accept_connections, daemon=True).start()
    
    def _accept_connections(self):
        """Accept client connections (runs in a separate thread)"""
        print(f"Server started, waiting for connections on port {self.port}...")
        while self.running and len(self.client_sockets) < 2:
            try:
                client_socket, addr = self.socket.accept()
                self.client_sockets.append(client_socket)
                print(f"Connection from {addr}")
                
                # Start a thread to handle this client
                threading.Thread(target=self._handle_client, 
                                args=(client_socket,), daemon=True).start()
            except:
                break
    
    def _handle_client(self, client_socket):
        """Handle communication with a client"""
        while self.running:
            try:
                # Receive data from client
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Process the received data
                message = pickle.loads(data)
                self._process_message(message, client_socket)
            except:
                break
        
        # Clean up when client disconnects
        if client_socket in self.client_sockets:
            self.client_sockets.remove(client_socket)
        client_socket.close()
    
    def _connect_to_server(self):
        """Connect to the server as a client"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_ip, self.port))
            print(f"Connected to server at {self.server_ip}:{self.port}")
            
            # Start a thread to receive messages
            threading.Thread(target=self._receive_messages, daemon=True).start()
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.running = False
    
    def _receive_messages(self):
        """Receive messages from the server (client mode)"""
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = pickle.loads(data)
                self._process_message(message)
            except:
                break
        self.running = False
    
    def send_message(self, message, client_socket=None):
        """Send a message to the server or to a specific client"""
        try:
            data = pickle.dumps(message)
            if self.is_server and client_socket:
                # Server sending to a specific client
                client_socket.send(data)
            elif self.is_server:
                # Server broadcasting to all clients
                for client in self.client_sockets:
                    client.send(data)
            else:
                # Client sending to server
                self.socket.send(data)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def _process_message(self, message, sender=None):
        """Process received messages - override this in subclasses"""
        print(f"Received message: {message}")
        # This should be overridden to handle game-specific messages
    
    def stop(self):
        """Stop the network manager and close all connections"""
        self.running = False
        if self.is_server:
            for client in self.client_sockets:
                try:
                    client.close()
                except:
                    pass
        if self.socket:
            self.socket.close()