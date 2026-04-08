# NovaChat 🌌
**Secure, Anonymous, End-to-End Encrypted Tor Chat Engine**

NovaChat is a decentralized, high-performance chat platform designed for absolute privacy. It routes all traffic through the Tor network via Hidden Services, meaning it requires no port forwarding, completely bypasses NAT/Firewalls, and hides the IP addresses of both the server and all connected clients.

## 🧠 Basis of Technology
NovaChat operates on a custom-built, highly secure architecture:

* **The Network Layer (Tor & PySocks):** Uses SOCKS5 to route TCP socket connections directly through the Tor network to a `.onion` Hidden Service.
* **End-to-End Encryption (AES-GCM):** Every message and file is encrypted client-side using AES-GCM (256-bit keys derived via PBKDF2HMAC-SHA256). The Server acts purely as a blind router and *never* sees the plaintext content of chats or files.
* **TCP Stream Optimization:** Utilizes custom chunked `bytearray` streaming to flawlessly push large media (up to 8MB) through Tor's strict packet fragmentation limits without overflowing memory.
* **Nova Engine (Steganography & Payloads):**
  * **ZWC Camouflage:** Hides encrypted text invisibly inside normal text using Base16 Unicode Variation Selectors (`U+FE00` to `U+FE0F`), ensuring zero visual spacing or layout corruption.
  * **Payload Packer:** Converts encrypted binary files into highly efficient Base85 strings for easy copy-pasting across text-only platforms.

---

## ⚙️ Prerequisites
Before running NovaChat, you must have the Tor service installed and running on your machine's background (Port `9050`).
* **Linux:** `sudo apt install tor` then `sudo systemctl start tor`
* **Windows/Mac:** Download and run the Tor Expert Bundle, or simply keep the Tor Browser open in the background.
* **Python:** Python 3.8 or higher.

---

## 🛠️ Installation
1. Clone or download this repository.
2. Open your terminal/command prompt in the NovaChat folder.
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
