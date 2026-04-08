import socket
import threading
import sys
import getpass

HOST = "127.0.0.1"
PORT = 9999

# Colors for Server Console
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

clients = {}  
running = True
SERVER_PASSWORD = None

def broadcast(msg, sender=None):
    for client in list(clients.keys()):
        if client != sender:
            try:
                client.sendall(msg)
            except:
                remove_client(client)

def remove_client(client):
    username = clients.get(client, "Unknown")
    print(f"{C_RED}[-] {username} disconnected{C_RESET}")
    clients.pop(client, None)
    try:
        client.close()
    except:
        pass

def send_private(target_user, msg):
    for client, username in clients.items():
        if username == target_user:
            try:
                client.sendall(msg)
                return True
            except:
                return False
    return False

def handle_client(client):
    try:
        auth = client.recv(1024).decode()
        if not auth.startswith("AUTH::"):
            client.close()
            return

        _, username, password = auth.split("::", 2)

        if username in clients.values():
            client.sendall(b"[!] ERROR: Username already taken in this session.")
            client.close()
            return

        if password != SERVER_PASSWORD:
            client.sendall(b"[!] Authentication failed")
            client.close()
            return

        clients[client] = username
        print(f"{C_GREEN}[+] {username} connected{C_RESET}")
        client.sendall(b"[+] Auth successful")
        broadcast(f"[+] {username} joined the server".encode(), client)

        is_receiving_file = False
        file_target = "all"
        
        # 🛡️ THE FIX: A rolling window that saves the last 20 bytes of every packet
        # so if the network slices our "::NOVA_FILE_END::" in half, we still catch it!
        tail = b"" 

        while running:
            data = client.recv(65536) 
            if not data:
                break

            if not is_receiving_file:
                if data.startswith(b"FILE_DATA::"):
                    is_receiving_file = True
                    tail = data[-20:] 
                    
                    try:
                        header_part = data[len(b"FILE_DATA::"):data.find(b"|")]
                        header_str = header_part.decode('utf-8', errors='ignore')
                        parts = header_str.split("::")
                        if len(parts) >= 3:      
                            file_target = parts[1]
                        elif len(parts) == 2:    
                            file_target = parts[0]
                        else:
                            file_target = "all"
                    except:
                        file_target = "all"
                    
                    if file_target == "all":
                        broadcast(data, client)
                    else:
                        success = send_private(file_target, data)
                        if not success:
                            client.sendall(f"[!] User '{file_target}' not found or offline.".encode())
                    
                    if b"::NOVA_FILE_END::" in data:
                        is_receiving_file = False
                        tail = b""
                else:
                    try:
                        decoded = data.decode(errors="ignore")
                    except:
                        decoded = ""

                    if decoded.startswith("DEL_FILE::"):
                        broadcast(data, client)
                        continue

                    if decoded.startswith("CMD::USERS"):
                        user_list = ",".join(clients.values())
                        client.sendall(f"USERS::{user_list}".encode())
                        continue

                    if decoded.startswith("PM::"):
                        try:
                            _, target, payload = decoded.split("::", 2)
                            send_private(target, payload.encode())
                        except:
                            client.sendall(b"[!] Invalid PM format")
                        continue

                    broadcast(data, client)
            else:
                if file_target == "all":
                    broadcast(data, client)
                else:
                    send_private(file_target, data)
                
                # 🛡️ THE FIX: Combine the end of the last packet with the new packet
                check_buffer = tail + data
                if b"::NOVA_FILE_END::" in check_buffer:
                    is_receiving_file = False
                    tail = b""
                else:
                    tail = data[-20:]

    except Exception as e:
        pass
    remove_client(client)

def start_server():
    global SERVER_PASSWORD
    print(f"{C_YELLOW}--- NovaChat Secure Server ---{C_RESET}")
    SERVER_PASSWORD = getpass.getpass("Set server password: ")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind((HOST, PORT))
    s.listen()
    print(f"{C_GREEN}[+] Server Running on {HOST}:{PORT}{C_RESET}")
    
    try:
        while running:
            client, _ = s.accept()
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
    except KeyboardInterrupt:
        print(f"\n{C_RED}[!] Server stopping...{C_RESET}")
        sys.exit(0)

if __name__ == "__main__":
    start_server()