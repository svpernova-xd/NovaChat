# NovaChat 🌌

**Secure, Anonymous, End-to-End Encrypted Tor Chat Engine**

NovaChat is a decentralized, high-performance chat platform designed for absolute privacy. It routes all traffic through the Tor network via Hidden Services, meaning it requires no port forwarding, completely bypasses NAT/Firewalls, and hides the IP addresses of both the server and all connected clients.

---

## ⚠️ Disclaimer

> This project is intended for **educational and research purposes only**.

* The author is **not responsible for misuse** of this software.
* Do **not** use NovaChat for illegal activities, unauthorized access, or privacy violations.
* While strong encryption is implemented, this project is **experimental** and has not undergone formal security audits.

---

## 🧠 Basis of Technology

NovaChat operates on a custom-built, highly secure architecture:

* **The Network Layer (Tor & PySocks):**
  Uses SOCKS5 to route TCP socket connections directly through the Tor network to a `.onion` Hidden Service.

* **End-to-End Encryption (AES-GCM):**
  Every message and file is encrypted client-side using AES-GCM (256-bit keys derived via PBKDF2HMAC-SHA256).
  The server acts purely as a **blind router** and never sees plaintext data.

* **TCP Stream Optimization:**
  Uses chunked `bytearray` streaming to handle large media (up to 8MB) efficiently without memory overflow.

* **Nova Engine (Steganography & Payloads):**

  * **ZWC Camouflage:** Hide encrypted text invisibly inside normal text using zero-width Unicode characters.
  * **Payload Packer:** Convert encrypted binary files into Base64 blocks for easy sharing across platforms.

---

## ⚙️ Prerequisites

Before running NovaChat:

### 1. Install Tor

#### Linux

```bash
sudo apt install tor
sudo systemctl start tor
```

#### Windows / macOS

* Install **Tor Browser** OR **Tor Expert Bundle**
* Keep Tor running in the background

> Default Tor SOCKS port: `9050`

---

### 2. Install Python

* Python **3.8+ required**

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/novachat.git
cd novachat
pip install -r requirements.txt
```

---

## 🚀 How to Use NovaChat

### 🔹 Step 1 — Start the Server

```bash
python server.py
```

* Set a **server password** when prompted
* Server runs on:

```
127.0.0.1:9999
```

---

### 🔹 Step 2 — Connect Client (CLI)

```bash
python client.py
```

Enter:

* Onion address (or `127.0.0.1` for local testing)
* Username
* Password (same as server)

---

### 🔹 Step 3 — (Optional) Start Web Client

```bash
python web_client.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## 💬 Basic Usage

### Public Chat

Just type and send:

```
Hello everyone
```

---

### Private Messaging

```
/pm username
```

or

```
/msg username Hello
```

---

### View Online Users

```
/users
```

---

### Send File

```
/sendfile username path/to/file
```

or send to all:

```
/sendfile all file.jpg
```

---

### Download File

```
/get filename
```

---

### Exit

```
/exit
```

---

## 🔥 Features

### 🔐 End-to-End Encryption

* AES-GCM encryption
* Password-derived keys (PBKDF2)
* Server cannot read messages

---

### 🧅 Tor-Based Anonymity

* No IP exposure
* No port forwarding
* Hidden services supported

---

### 📁 Secure File Transfer

* Files encrypted before leaving sender
* Decrypted only on receiver side
* Supports images, audio, video, documents

---

### 🕵️ Steganography (ZWC Camouflage)

* Hide encrypted messages inside normal text
* Invisible to human eye
* Useful for covert communication

---

### 📦 Payload System

* Convert encrypted files into Base64 blocks
* Share across platforms (email, chat, etc.)
* Restore and decrypt anytime

---

### 🌐 Web Interface

* Modern chat UI
* File preview before sending
* Upload progress tracking
* Media playback inside chat

---

### ⚡ Optimized Streaming

* Handles large files via chunked transmission
* Prevents memory overflow
* Stable over Tor network

---

## 🧪 Security Notes

* Encryption is strong but implementation is **custom**
* No formal audit yet
* Use at your own risk for sensitive data

---

## 🛣️ Future Improvements

* Key-based access control for files
* Self-destruct messages
* Multi-device sync
* Improved authentication system (JWT / UUID)
* Mobile app support

---

## 🤝 Contributing

Contributions are welcome.
Feel free to fork, improve, and submit pull requests.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🌌 Final Note

NovaChat is not just a chat app —
it’s a **secure communication engine** built for privacy-first interaction.

---
