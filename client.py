import socks
import socket
import threading
import protocol
import getpass
import os
import sys
import shutil
from datetime import datetime

# TOR configuration
TOR_PROXY = ("127.0.0.1", 9050)
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- UI COLORS ---
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"
C_DIM = "\033[2m"

USER_COLORS = [C_RED, C_GREEN, C_YELLOW, C_BLUE, C_MAGENTA, C_CYAN]

BANNER = f"""{C_CYAN}{C_BOLD}
 ███╗   ██╗██████╗ ██╗   ██╗███████╗ ██████╗██╗  ██╗███████╗████████╗
 ████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔════╝██║  ██║██╔══██╗╚══██╔══╝
 ██╔██╗ ██║██║   ██║██║   ██║███████║██║     ███████║███████║   ██║   
 ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║     ██╔══██║██╔══██║   ██║   
 ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╗██║  ██║██║  ██║   ██║   
 ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
     {C_YELLOW}Secure Onion Chat Protocol{C_RESET}
"""

def get_time():
    return datetime.now().strftime("%H:%M")

def get_user_color(username):
    idx = sum(ord(char) for char in username) % len(USER_COLORS)
    return USER_COLORS[idx]

def print_prompt(username, chat_mode):
    width = shutil.get_terminal_size().columns
    if chat_mode == "broadcast":
        raw_line1 = f"╭─[{username} @ Public]"
        color = C_MAGENTA
    else:
        raw_line1 = f"╭─[{username} @ PM:{chat_mode}]"
        color = C_GREEN
        
    raw_line2 = "╰─> "
    pad_len = (width - len(raw_line1)) // 2
    padding = " " * max(0, pad_len)
    
    print(f"{C_BOLD}{color}{padding}{raw_line1}{C_RESET}")
    print(f"{C_BOLD}{color}{padding}{raw_line2}{C_RESET}", end="", flush=True)

def clear_current_prompt():
    print("\r\033[2K\033[1A\033[2K", end="")

def erase_last_input():
    print("\033[F\033[2K\033[F\033[2K", end="")

def print_left(sender, text, is_pm=False):
    u_color = get_user_color(sender)
    if is_pm:
        print(f"{u_color}╭── [{C_BOLD}🔒 PM from {sender}{C_RESET}{u_color}] ─ {C_DIM}{get_time()}{C_RESET} 📥")
        print(f"{C_MAGENTA}╰─> {text}{C_RESET}")
    else:
        print(f"{u_color}╭── [{C_BOLD}{sender}{C_RESET}{u_color}] ─ {C_DIM}{get_time()}{C_RESET} 📥")
        print(f"{C_CYAN}╰─> {text}{C_RESET}")

def print_right(target, text):
    width = shutil.get_terminal_size().columns
    erase_last_input()
    
    header_clean = f"{get_time()} ─ [{target}] ──╮"
    body_clean = f"{text} ──╯"
    
    pad_header = " " * max(0, width - len(header_clean))
    pad_body = " " * max(0, width - len(body_clean))
    
    print(f"{pad_header}{C_DIM}{C_GREEN}{header_clean}{C_RESET}")
    print(f"{pad_body}{C_BOLD}{C_GREEN}{body_clean}{C_RESET}")

def connect(onion, port):
    print("\033[2J\033[H", end="") 
    print(BANNER)
    username = input(f"{C_BLUE}Username:{C_RESET} ")
    password = getpass.getpass(f"{C_BLUE}Password:{C_RESET} ")

    s = socks.socksocket()
    s.set_proxy(socks.SOCKS5, TOR_PROXY[0], TOR_PROXY[1])
    try:
        print(f"{C_YELLOW}[*] Connecting to Tor Network...{C_RESET}")
        s.connect((onion, port))
    except Exception as e:
        print(f"{C_RED}[!] Connection failed: {e}{C_RESET}")
        return

    auth_packet = f"AUTH::{username}::{password}"
    s.send(auth_packet.encode())
    
    response = s.recv(1024).decode()
    if "[!]" in response:
        print(f"\n{C_RED}{response}{C_RESET}")
        s.close()
        return

    print(f"\n{C_GREEN}{response}{C_RESET}")
    print(f"{C_CYAN}Type /help for commands.{C_RESET}\n")
    
    terminal_height = shutil.get_terminal_size().lines
    print("\n" * (terminal_height - 15)) 

    running = True
    chat_mode = "broadcast" 

    def receive():
        nonlocal running
        while running:
            try:
                data = s.recv(5 * 1024 * 1024)
                if not data: break

                try:
                    decoded_text = data.decode(errors="ignore")
                except:
                    decoded_text = ""

                if decoded_text.startswith("FILE_ALERT::"):
                    _, sender, fname, fsize = decoded_text.split("::")
                    size_mb = round(int(fsize) / (1024*1024), 2)
                    u_color = get_user_color(sender)
                    
                    clear_current_prompt()
                    print(f"{u_color}╭── [🔔 FILE ALERT: {C_BOLD}{sender}{C_RESET}{u_color}] ─ {C_DIM}{get_time()}{C_RESET} 📥")
                    print(f"{u_color}│    Name: {C_CYAN}{fname}{C_RESET} | Size: {size_mb} MB")
                    print(f"{u_color}╰─>  {C_BOLD}Type /get {fname} to download.{C_RESET}")
                    print_prompt(username, chat_mode)
                    continue

                if data.startswith(b"FILE_DATA::"):
                    raw = data[len(b"FILE_DATA::"):]
                    header, blob = raw.split(b"|", 1)
                    _, fname = header.decode().split("::", 1)
                    
                    clear_current_prompt()
                    try:
                        decrypted_bytes = protocol.decode_file_payload(blob, password)
                        filepath = os.path.join(DOWNLOAD_DIR, fname)
                        with open(filepath, "wb") as f:
                            f.write(decrypted_bytes)
                        print(f"{C_GREEN}[✅ {get_time()}] SECURE DOWNLOAD COMPLETE: {C_BOLD}{fname}{C_RESET} saved to {DOWNLOAD_DIR}/{C_RESET}")
                    except Exception as e:
                        print(f"{C_RED}[!] Decryption failed for {fname}. {C_RESET}")
                    
                    print_prompt(username, chat_mode)
                    continue

                if "USERS::" in decoded_text:
                    users = decoded_text.split('::')[1]
                    clear_current_prompt()
                    print(f"{C_CYAN}[{get_time()}] [Users Online]: {C_BOLD}{users}{C_RESET}")
                    print_prompt(username, chat_mode)
                    continue

                try:
                    msg = protocol.decode_message(data, password)
                    clear_current_prompt()
                    
                    if "]: " in msg:
                        sender_part, text = msg.split("]: ", 1)
                        # 🔒 PM DETECTION LOGIC
                        if "[PM from " in sender_part:
                            sender = sender_part.replace("[PM from ", "")
                            print_left(sender, text, is_pm=True)
                        else:
                            sender = sender_part.replace("[", "")
                            print_left(sender, text, is_pm=False)
                    else:
                        print(f"{C_BLUE} 💬 [{get_time()}] {msg}{C_RESET}")
                        
                    print_prompt(username, chat_mode)
                except:
                    clear_current_prompt()
                    print(f"{C_RED}[{get_time()}] {decoded_text}{C_RESET}")
                    print_prompt(username, chat_mode)
                    
            except Exception as e:
                break

    threading.Thread(target=receive, daemon=True).start()

    try:
        while running:
            print_prompt(username, chat_mode)
            msg = input()
            
            if not msg: 
                erase_last_input()
                continue

            if msg == "/help":
                erase_last_input()
                print(f"""{C_CYAN}
    --- Commands ---
    /users                     : List online users
    /pm <user>                 : Enter Private Mode
    /pm exit                   : Return to Public chat
    /msg <user> <text>         : Send quick private message
    /sendfile <user> <path>    : Send secure file ('all' for everyone)
    /get <filename>            : Download a file
    /exit                      : Quit
                {C_RESET}""")
            
            elif msg == "/exit":
                running = False
                break
            
            elif msg == "/users":
                erase_last_input()
                s.send(b"CMD::USERS")
            
            elif msg.startswith("/pm "):
                erase_last_input()
                target = msg.split(" ", 1)[1].strip()
                if target.lower() == "exit":
                    chat_mode = "broadcast"
                    print(f"{C_GREEN}[* {get_time()}] Exited private mode.{C_RESET}")
                else:
                    chat_mode = target
                    print(f"{C_YELLOW}[* {get_time()}] Entered private mode with {target}. Type '/pm exit' to leave.{C_RESET}")

            elif msg.startswith("/get "):
                erase_last_input()
                parts = msg.split(" ", 1)
                if len(parts) > 1:
                    fname = parts[1]
                    s.send(f"GET_FILE::{fname}".encode())
                    print(f"{C_YELLOW}[* {get_time()}] Requesting {fname}...{C_RESET}")
            
            elif msg.startswith("/sendfile "):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    print(f"{C_RED}[!] Usage: /sendfile <user_or_all> <path_to_file>{C_RESET}")
                    continue
                
                _, target, path = parts
                if os.path.exists(path):
                    fname = os.path.basename(path)
                    with open(path, "rb") as f:
                        file_bytes = f.read()
                    
                    print_right(target, f"[📁 Sent File: {fname}]")
                    packet = protocol.encode_file_payload(target, fname, file_bytes, password)
                    s.send(packet)
                else:
                    erase_last_input()
                    print(f"{C_RED}[!] File not found locally.{C_RESET}")
            
            elif msg.startswith("/msg "):
                try:
                    _, target_user, text = msg.split(" ", 2)
                    payload = protocol.encode_message(f"[PM from {username}]: {text}", password)
                    s.send(f"PM::{target_user}::".encode() + payload)
                    print_right(f"PM:{target_user}", text)
                except ValueError:
                    erase_last_input()
                    print(f"{C_RED}[!] Usage: /msg <user> <message>{C_RESET}")
            
            else:
                if chat_mode == "broadcast":
                    s.send(protocol.encode_message(f"[{username}]: {msg}", password))
                    print_right("Public", msg)
                else:
                    payload = protocol.encode_message(f"[PM from {username}]: {msg}", password)
                    s.send(f"PM::{chat_mode}::".encode() + payload)
                    print_right(f"PM:{chat_mode}", msg)
                
    finally:
        s.close()
        sys.exit(0)

if __name__ == "__main__":
    onion = input(f"{C_BLUE}Onion Address:{C_RESET} ")
    connect(onion, 9999)