# NovaChat 🌌

**Secure, Anonymous, End-to-End Encrypted Tor Chat Engine**

NovaChat is a decentralized, high-performance chat platform designed for absolute privacy. It routes all traffic through the Tor network via Hidden Services, meaning it requires no port forwarding, completely bypasses NAT/Firewalls, and hides the IP addresses of both the server and all connected clients.

---

## 📸 Screenshots

### Web UI
<img width="1920" height="1009" alt="image" src="https://github.com/user-attachments/assets/86e9308d-bd64-410c-926e-caaa099f074e" />

##

<img width="1920" height="1009" alt="image" src="https://github.com/user-attachments/assets/fb9ffdf8-53c4-40f4-8d34-8c40d28150a2" />

##

<img width="1920" height="1009" alt="image" src="https://github.com/user-attachments/assets/cf5d1a81-2772-4866-a107-c268a99c6b3a" />

### CLI Client

<img width="1919" height="961" alt="Screenshot From 2026-04-09 01-47-37" src="https://github.com/user-attachments/assets/255ea4b2-35ca-4f67-b200-1a11bbc9f52d" />


---

## ⚠️ Disclaimer

> This project is intended for **educational and research purposes only**.

* The author is **not responsible for misuse** of this software.
* Do **not** use NovaChat for illegal activities, unauthorized access, or privacy violations.
* While strong encryption is implemented, this project is **experimental** and has not undergone formal security audits.

---

## 🧅 How to Get Your `.onion` Hostname

To allow others to connect to your NovaChat server over Tor, you need to create a Tor Hidden Service.

### Step 1 — Edit Tor Configuration

* Linux:

```bash
sudo nano /etc/tor/torrc
```

* Windows/macOS (Tor Browser):
  Locate `torrc` inside the Tor installation directory.

Add:

```
HiddenServiceDir /var/lib/tor/novachat_service/
HiddenServicePort 9999 127.0.0.1:9999
```

---

### Step 2 — Restart Tor

```bash
sudo systemctl restart tor
```

---

### Step 3 — Get Onion Address

```bash
sudo cat /var/lib/tor/novachat_service/hostname
```

---

### Step 4 — Run Server

```bash
python server.py
```

---

## ⚙️ Prerequisites

### 🐧 Linux

```bash
sudo apt install tor
sudo systemctl start tor
```

---

### 🪟 Windows 10 / 11 (IMPORTANT)

#### 1. Install Tor Browser

* Download and install **Tor Browser**
* Open it once and keep it running

👉 Windows uses **SOCKS5 port `9150` (NOT 9050)**

---

#### 2. Install Python (3.8+)

Download from: https://www.python.org/

✔ Make sure:

* "Add Python to PATH" is checked

---

#### 3. Install Required Modules

Run in Command Prompt / PowerShell:

```bash
py -m pip install flask==3.0.3 flask-socketio==5.3.6 pysocks==1.7.1 cryptography==42.0.5
```

---

#### 4. Important Fix (Tor Port)

Edit these files:

* `client.py`
* `web_client.py`

Change:

```python
("127.0.0.1", 9050)
```

👉 TO:

```python
("127.0.0.1", 9150)
```

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/novachat.git
cd novachat
pip install -r requirements.txt
```

---

## 🚀 How to Use NovaChat

### 🔹 Step 1 — Start Server

```bash
python server.py
```

---

### 🔹 Step 2 — Start CLI Client

```bash
python client.py
```

---

### 🔹 Step 3 — Start Web Client (Optional)

```bash
python web_client.py
```

Open:

```
http://127.0.0.1:5000
```

---

## 💬 Basic Usage

### Public Chat

```
Hello everyone
```

### Private Messaging

```
/pm username
```

or

```
/msg username Hello
```

### Users List

```
/users
```

### Send File

```
/sendfile username path/to/file
```

### Download File

```
/get filename
```

### Exit

```
/exit
```

---

## 🔥 Features

### 🔐 End-to-End Encryption

* AES-GCM encryption
* PBKDF2 key derivation
* Server cannot read messages

### 🧅 Tor-Based Anonymity

* Hidden services
* No IP exposure

### 📁 Secure File Transfer

* Encrypted before sending
* Decrypted only by receiver

### 🕵️ Steganography

* Invisible message hiding

### 📦 Payload System

* Base64 encrypted file transport

### 🌐 Web Interface

* File preview
* Upload progress
* Media playback

### ⚡ Optimized Streaming

* Handles large files efficiently
* Prevents memory overflow

---

## 🧪 Security Notes

* Custom crypto implementation
* No formal audit
* Use cautiously

---

## 🛣️ Future Improvements

* Key-based file access
* Self-destruct messages
* JWT authentication
* Mobile support

---

## 🤝 Contributing

Contributions are welcome.

---

## 📜 License

MIT License

---

## 🌌 Final Note

NovaChat is not just a chat app —
it’s a **secure communication engine built for privacy-first interaction**.

---
