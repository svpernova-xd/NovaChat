import socks
import socket
import threading
import protocol
import crypto
import stego
import payload as nova_payload
import file_format
import os
import sys
import re
from datetime import datetime
from flask import Flask, render_template_string, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nova-secret!'
socketio = SocketIO(app, async_mode='threading', max_http_buffer_size=1e8)

TOR_PROXY = ("127.0.0.1", 9050)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

active_sessions = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NovaChat Web</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #fff; margin: 0; display: flex; height: 100vh; overflow: hidden; }
        #login-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; }
        .box { background: #1e1e1e; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); text-align: center; width: 350px; }
        .box h1 { color: #00e5ff; margin-bottom: 20px; font-size: 32px; letter-spacing: 2px; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #2d2d2d; border: 1px solid #444; color: white; border-radius: 6px; outline: none; }
        button { width: 100%; padding: 12px; background: #00e5ff; color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; transition: 0.3s; }
        button:hover { background: #00b3cc; }
        button:disabled { background: #555; cursor: not-allowed; }
        
        #chat-screen { display: none; width: 100%; flex-direction: column; }
        #header { background: #1e1e1e; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; }
        #messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; background: #0a0a0a; }
        
        .msg { max-width: 65%; padding: 10px 15px; border-radius: 12px; line-height: 1.4; word-wrap: break-word; position: relative; }
        .msg-left { background: #2d2d2d; align-self: flex-start; border-bottom-left-radius: 2px; }
        .msg-right { background: #0078FF; align-self: flex-end; border-bottom-right-radius: 2px; }
        .msg-sys { background: #333; color: #aaa; font-size: 0.85em; align-self: center; border-radius: 20px; padding: 8px 15px; text-align: center;}
        
        .sender-name { font-weight: bold; font-size: 0.85em; margin-bottom: 4px; }
        .timestamp { font-size: 0.7em; opacity: 0.6; display: block; margin-top: 5px; text-align: right;}
        
        #input-area { padding: 15px; background: #1e1e1e; display: flex; gap: 10px; align-items: center; }
        #chat-input { flex: 1; margin: 0; border-radius: 4px; padding: 12px; background: #2d2d2d; border: 1px solid #444; color: white; outline: none;}
        #send-btn { width: 100px; margin: 0; }
        
        #file-btn { font-size: 24px; cursor: pointer; padding: 0 10px; transition: 0.2s; }
        #file-btn:hover { color: #00e5ff; }

        .user-dropdown { background: #2d2d2d; color: #00e5ff; border: 1px solid #00e5ff; border-radius: 6px; padding: 5px 10px; font-weight: bold; font-size: 13px; outline: none; cursor: pointer; }
        .user-dropdown:focus { border-color: #00b3cc; }
        
        .media-preview { max-width: 100%; max-height: 280px; border-radius: 8px; margin-top: 8px; display: block; object-fit: contain; background: #000; }
        .dl-btn { background: #333; border: 1px solid #555; color: #00e5ff; margin-top: 8px; padding: 6px 12px; font-size: 13px; text-decoration: none; display: inline-block; border-radius: 4px; cursor: pointer; }
        .dl-btn:hover { background: #444; }
        .del-btn { background: #4a0000; border: 1px solid #800; color: #ffaaaa; margin-left: 5px; }
        .del-btn:hover { background: #600000; }

        .modal { display: none; position: fixed; z-index: 100; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); }
        .modal-content { background-color: #1e1e1e; margin: 5% auto; padding: 25px; border: 1px solid #333; width: 90%; max-width: 600px; border-radius: 12px; color: white;}
        .tab-menu { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 10px;}
        .tab-menu button { flex: 1; background: #2d2d2d; color: #fff; font-size: 14px; margin: 0; }
        .tab-menu button.active { background: #00e5ff; color: #000; }
        .tool-section { display: none; flex-direction: column; gap: 15px; }
        .tool-section.active { display: flex; }
        
        textarea { background: #121212; color: #00e5ff; border: 1px solid #444; border-radius: 6px; padding: 12px; width: 100%; resize: vertical; min-height: 80px; font-family: monospace; word-break: break-all; white-space: pre-wrap;}
        .file-picker-card { background: #2d2d2d; padding: 15px; border-radius: 6px; border: 1px dashed #555; }
        .file-picker-input { width: 100%; padding: 10px; background: #121212; border: 1px solid #444; border-radius: 4px; color: white; margin-top: 10px;}
        .tools-btn { width: auto; padding: 8px 15px; font-size: 13px; background: #2d2d2d; color: #00e5ff; border: 1px solid #00e5ff; margin: 0;}
        .tools-btn:hover { background: #00e5ff; color: #000; }

        .progress-ring { width: 40px; height: 40px; }
        .progress-ring__circle { transition: stroke-dashoffset 0.1s linear; transform: rotate(-90deg); transform-origin: 50% 50%; }
        .upload-overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7); border-radius: 8px;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            color: #00e5ff; font-size: 12px; font-weight: bold; z-index: 10;
        }
        .media-container { position: relative; display: inline-block; margin-top: 8px; max-width: 100%; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>

    <div id="login-screen">
        <div class="box">
            <h1>NOVA WEB</h1>
            <input type="text" id="onion" placeholder="Tor Onion Address" value="127.0.0.1">
            <input type="text" id="username" placeholder="Username">
            <input type="password" id="password" placeholder="Password">
            <button onclick="connect()" id="connect-btn">Connect Securely</button>
            <p id="status" style="color: #ff4444; font-size: 14px;"></p>
        </div>
    </div>

    <div id="tools-modal" class="modal">
        <div class="modal-content">
            <span onclick="document.getElementById('tools-modal').style.display='none'" style="float:right; cursor:pointer; font-size: 24px; color: #ff5252;">✖</span>
            <h2 style="margin-top:0; color:#00e5ff;">🛠️ Nova Engine</h2>
            
            <div class="tab-menu">
                <button id="tab-btn-stego" class="active" onclick="switchToolTab('stego')">Camouflage (ZWC)</button>
                <button id="tab-btn-payload" onclick="switchToolTab('payload')">Payload Base64</button>
            </div>
            
            <div id="tool-stego" class="tool-section active">
                <textarea id="stego-cover" placeholder="Cover Text (or infected text to reveal)"></textarea>
                <textarea id="stego-secret" placeholder="Secret Message (Leave blank if revealing)"></textarea>
                <input type="password" id="stego-pass" placeholder="Encryption Password" style="margin: 0;">
                <div style="display:flex; gap:10px;">
                    <button onclick="stegoAction('hide')">🔒 Hide Secret</button>
                    <button onclick="stegoAction('reveal')" style="background: #333; color:#fff;">🔓 Reveal Secret</button>
                </div>
                <textarea id="stego-output" placeholder="Result will appear here..." readonly style="min-height: 120px;"></textarea>
            </div>

            <div id="tool-payload" class="tool-section">
                <div class="file-picker-card">
                    <label style="font-weight: bold; color: #00e5ff;">1. Select File to Pack (Max 8MB):</label>
                    <input type="file" id="payload-file" class="file-picker-input">
                </div>
                <textarea id="payload-text" placeholder="Or paste -----BEGIN NOVA PAYLOAD----- block here to unpack..."></textarea>
                <input type="password" id="payload-pass" placeholder="Encryption Password" style="margin: 0;">
                <div style="display:flex; gap:10px;">
                    <button onclick="payloadAction('create')">📦 Pack to Base64</button>
                    <button onclick="payloadAction('restore')" style="background: #333; color:#fff;">📄 Unpack to File</button>
                </div>
                <textarea id="payload-output" placeholder="Base64 Payload will appear here..." readonly style="min-height: 120px;"></textarea>
                <div id="payload-download-area"></div>
            </div>
        </div>
    </div>

    <div id="chat-screen">
        <div id="header">
            <div style="display: flex; gap: 15px; align-items: center;">
                <h2 style="margin:0; color:#00e5ff;">NovaChat</h2>
                <button class="tools-btn" onclick="document.getElementById('tools-modal').style.display='block'">🛠️ Tools</button>
            </div>
            <div style="display: flex; gap: 15px; align-items: center;">
                <select id="user-select" class="user-dropdown" onchange="changeChatMode(this.value)">
                    <option value="all">🌐 Public Chat</option>
                </select>
                <span id="online-users" style="font-size: 14px; color: #aaa;">Connected</span>
            </div>
        </div>
        <div id="messages"></div>
        <div id="input-area">
            <label for="file-upload" id="file-btn" title="Send a File">📎</label>
            <input type="file" id="file-upload" style="display: none;" onchange="uploadChatFile(this)">
            <input type="text" id="chat-input" placeholder="Type a message..." autocomplete="off" onkeypress="if(event.key === 'Enter') sendMessage()">
            <button id="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const socket = io();
        let myName = "";
        let chatMode = "all"; 
        
        const MAX_FILE_SIZE = 8 * 1024 * 1024; 

        function escapeHTML(str) {
            if (!str) return "";
            return str.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function getColor(username) {
            const colors = ['#ff5252', '#69f0ae', '#ffd740', '#448aff', '#e040fb', '#18ffff'];
            let hash = 0;
            for (let i = 0; i < username.length; i++) { hash += username.charCodeAt(i); }
            return colors[hash % colors.length];
        }

        function scrollToBottom() {
            const msgs = document.getElementById('messages');
            msgs.scrollTop = msgs.scrollHeight;
        }

        function switchToolTab(tab) {
            document.querySelectorAll('.tool-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-menu button').forEach(el => el.classList.remove('active'));
            document.getElementById('tool-' + tab).classList.add('active');
            document.getElementById('tab-btn-' + tab).classList.add('active');
        }

        function stegoAction(action) {
            const cover = document.getElementById('stego-cover').value;
            const secret = document.getElementById('stego-secret').value;
            const pass = document.getElementById('stego-pass').value;
            if (!pass) return alert("Password required!");
            
            document.getElementById('stego-output').value = "Processing...";
            if (action === 'hide') {
                if (!cover || !secret) return alert("Cover and Secret required to hide.");
                socket.emit('stego_hide', {cover: cover, secret: secret, password: pass});
            } else {
                if (!cover) return alert("Paste infected text into Cover input to reveal.");
                socket.emit('stego_reveal', {infected: cover, password: pass});
            }
        }

        socket.on('stego_result', function(data) {
            if (data.status === 'success') {
                document.getElementById('stego-output').value = data.result;
            } else {
                document.getElementById('stego-output').value = "Error: " + data.msg;
            }
        });

        function payloadAction(action) {
            const pass = document.getElementById('payload-pass').value;
            if (!pass) return alert("Password required!");
            
            document.getElementById('payload-output').value = "Processing...";
            document.getElementById('payload-download-area').innerHTML = "";

            if (action === 'create') {
                const fileInput = document.getElementById('payload-file');
                if (fileInput.files.length === 0) return alert("Select a file first to pack.");
                
                const file = fileInput.files[0];
                if (file.size > MAX_FILE_SIZE) {
                    return alert("File is too large! Maximum allowed size is 8MB.");
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    socket.emit('payload_create', {filename: file.name, data: e.target.result, password: pass});
                };
                reader.readAsArrayBuffer(file);
            } else {
                const payloadText = document.getElementById('payload-text').value;
                if (!payloadText.includes("BEGIN NOVA PAYLOAD")) return alert("Paste valid Nova Payload text to unpack.");
                socket.emit('payload_restore', {payload: payloadText, password: pass});
            }
        }

        socket.on('payload_result', function(data) {
            if (data.status === 'success') {
                if (data.action === 'create') {
                    document.getElementById('payload-output').value = data.result;
                } else if (data.action === 'restore') {
                    document.getElementById('payload-output').value = "File successfully unpacked and decrypted!";
                    const url = '/downloads/' + encodeURIComponent(data.filename);
                    document.getElementById('payload-download-area').innerHTML = `
                        <a href="${url}" download class="dl-btn" style="display:block; text-align:center; padding: 12px; font-size: 16px;">
                            💾 Download Restored File (${escapeHTML(data.filename)})
                        </a>`;
                }
            } else {
                document.getElementById('payload-output').value = "Error: " + data.msg;
            }
        });

        function connect() {
            const btn = document.getElementById('connect-btn');
            btn.disabled = true;
            btn.innerText = "Negotiating Tor Circuit...";
            document.getElementById('status').innerText = "";
            
            myName = document.getElementById('username').value;
            socket.emit('login', {
                onion: document.getElementById('onion').value,
                user: myName,
                pass: document.getElementById('password').value
            });
        }

        socket.on('login_response', function(data) {
            const btn = document.getElementById('connect-btn');
            btn.disabled = false;
            btn.innerText = "Connect Securely";
            
            if (data.status === 'success') {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('chat-screen').style.display = 'flex';
                addSystemMessage("Connected to Tor Network Securely.");
                socket.emit('send_msg', { text: '/users', target: 'all' });
            } else {
                document.getElementById('status').innerText = escapeHTML(data.msg);
            }
        });

        socket.on('update_users', function(data) {
            const select = document.getElementById('user-select');
            select.innerHTML = '<option value="all">🌐 Public Chat</option>';
            
            data.users.forEach(u => {
                if(u && u.trim() !== myName) {
                    const opt = document.createElement('option');
                    opt.value = escapeHTML(u.trim());
                    opt.innerText = '🔒 PM: ' + escapeHTML(u.trim());
                    select.appendChild(opt);
                }
            });

            if (data.users.includes(chatMode)) {
                select.value = chatMode;
            } else if (chatMode !== 'all') {
                chatMode = 'all';
                select.value = 'all';
                addSystemMessage("User went offline. Returned to Public Chat.");
            }
        });

        socket.on('trigger_user_refresh', function() {
            socket.emit('send_msg', { text: '/users', target: 'all' });
        });

        function changeChatMode(newMode) {
            chatMode = newMode;
            if (chatMode === 'all') {
                addSystemMessage("Switched to Public Chat.");
            } else {
                addSystemMessage(`Entered Private Mode. Messages are now securely locked to ${escapeHTML(chatMode)}.`);
            }
        }

        function addSystemMessage(text) {
            const div = document.createElement('div');
            div.className = 'msg msg-sys';
            div.innerText = text;
            document.getElementById('messages').appendChild(div);
            scrollToBottom();
        }

        function deleteChatFile(btnElem, filename) {
            socket.emit('delete_file', { filename: filename });
            const div = btnElem.closest('.msg');
            if (div) {
                div.innerHTML = `<div style="color: #ff5252; font-style: italic; padding: 10px;">🚫 You deleted this file for everyone.</div>`;
            }
        }

        socket.on('file_deleted', function(data) {
            const div = document.getElementById('alert-' + data.safeName);
            if (div) {
                div.innerHTML = `<div style="color: #ff5252; font-style: italic; padding: 10px;">🚫 This file was deleted by the sender.</div>`;
            }
        });

        socket.on('file_ready', function(data) {
            const div = document.createElement('div');
            div.id = 'alert-' + escapeHTML(data.safeName);
            div.className = 'msg msg-left';
            
            if (data.target !== "all") {
                div.style.borderLeft = '4px solid #e040fb';
            }

            let senderSafe = escapeHTML(data.sender);
            let filenameSafe = escapeHTML(data.filename);
            let senderColor = getColor(senderSafe);
            let time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const url = `/downloads/${encodeURIComponent(data.filename)}`;
            
            let mediaHtml = '';
            if (data.file_type === 'image') {
                mediaHtml = `<img src="${url}" class="media-preview">`;
            } else if (data.file_type === 'video') {
                mediaHtml = `<video controls class="media-preview"><source src="${url}"></video>`;
            } else if (data.file_type === 'audio') {
                mediaHtml = `<audio controls class="media-preview" style="height: 40px; margin-top: 10px;"><source src="${url}"></audio>`;
            } else if (data.file_type === 'document') {
                mediaHtml = `<div style="padding: 10px 0; background: #222; border-radius: 6px; padding: 10px; margin-top: 5px;">📄 <b>${filenameSafe}</b></div>`;
            } else {
                mediaHtml = `<div style="background: #3a2a00; border-left: 4px solid #ffaa00; padding: 8px; margin: 8px 0; font-size: 12px; color: #ffdd99; border-radius: 4px;">⚠️ <b>Unknown file type.</b> Open at your own risk.</div>`;
            }
            
            let pmHeader = data.target !== "all" ? `🔒 PM from ` : ``;
            
            div.innerHTML = `
                <div class="sender-name" style="color: ${senderColor}">${pmHeader}${senderSafe}</div>
                ${mediaHtml}
                <div style="margin-top: 6px;"><a href="${url}" download class="dl-btn">💾 Save File</a></div>
                <span class="timestamp">${time}</span>
            `;
            
            document.getElementById('messages').appendChild(div);
            scrollToBottom();
        });

        socket.on('chat_message', function(data) {
            const div = document.createElement('div');
            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            let safeText = escapeHTML(data.text);
            let safeSender = escapeHTML(data.sender);

            if (data.type === 'system') {
                div.className = 'msg msg-sys';
                div.innerText = data.text; 
                if (data.text.includes("❌")) {
                    div.style.color = "#ff4444";
                }
            } else if (data.sender === myName) {
                div.className = 'msg msg-right';
                div.innerHTML = `<div>${safeText}</div><span class="timestamp">${time}</span>`;
            } else if (data.type === 'pm') {
                div.className = 'msg msg-left';
                div.style.borderLeft = '4px solid #e040fb'; 
                const color = getColor(safeSender);
                div.innerHTML = `<div class="sender-name" style="color: ${color}">🔒 PM from ${safeSender}</div><div>${safeText}</div><span class="timestamp">${time}</span>`;
            } else {
                div.className = 'msg msg-left';
                const color = getColor(safeSender);
                div.innerHTML = `<div class="sender-name" style="color: ${color}">${safeSender}</div><div>${safeText}</div><span class="timestamp">${time}</span>`;
            }
            
            document.getElementById('messages').appendChild(div);
            scrollToBottom();
        });

        function uploadChatFile(inputElem) {
            if (inputElem.files.length === 0) return;
            const file = inputElem.files[0];
            
            if (file.size > MAX_FILE_SIZE) {
                alert("File is too large! Maximum allowed size is 8MB.");
                inputElem.value = "";
                return;
            }
            
            const objectUrl = URL.createObjectURL(file);
            let safeFilename = escapeHTML(file.name);
            const uniqueId = safeFilename.replace(/[^a-zA-Z0-9]/g, '') + Date.now();
            
            const targetText = chatMode === "all" ? "everyone" : `PM: ${escapeHTML(chatMode)}`;
            const div = document.createElement('div');
            div.className = 'msg msg-right';
            
            let innerMediaHtml = '';
            if (file.type.startsWith('image/')) {
                innerMediaHtml = `<img src="${objectUrl}" class="media-preview">`;
            } else if (file.type.startsWith('video/')) {
                innerMediaHtml = `<video class="media-preview" src="${objectUrl}"></video>`;
            } else if (file.type.startsWith('audio/')) {
                innerMediaHtml = `<audio class="media-preview" src="${objectUrl}" style="height: 40px; margin-top:10px;"></audio>`;
            } else {
                innerMediaHtml = `<div style="padding: 10px 0; background: #222; border-radius: 6px; padding: 10px;">📄 <b>${safeFilename}</b></div>`;
            }

            const mediaHtml = `
                <div class="media-container">
                    ${innerMediaHtml}
                    <div id="upload-progress-${uniqueId}" class="upload-overlay">
                        <svg class="progress-ring" width="40" height="40">
                            <circle stroke="rgba(255,255,255,0.2)" stroke-width="4" fill="transparent" r="16" cx="20" cy="20"/>
                            <circle id="progress-circle-${uniqueId}" class="progress-ring__circle" stroke="#00e5ff" stroke-width="4" fill="transparent" r="16" cx="20" cy="20" stroke-dasharray="100.53" stroke-dashoffset="100.53"/>
                        </svg>
                        <div id="progress-text-${uniqueId}" style="margin-top: 5px;">0%</div>
                    </div>
                </div>
            `;

            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            div.innerHTML = `
                <div style="font-size: 0.8em; opacity: 0.7; margin-bottom: 4px;">Sending to ${targetText}...</div>
                ${mediaHtml}
                <div style="margin-top: 6px;">
                    <button onclick="deleteChatFile(this, '${file.name}')" class="dl-btn del-btn">🗑️ Delete</button>
                </div>
                <span class="timestamp">${time}</span>
            `;
            document.getElementById('messages').appendChild(div);
            scrollToBottom();

            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/api/upload_chat_file", true);
            
            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    let percentComplete = Math.floor((e.loaded / e.total) * 100);
                    let circle = document.getElementById('progress-circle-' + uniqueId);
                    let text = document.getElementById('progress-text-' + uniqueId);
                    
                    if (circle) {
                        const offset = 100.53 - (percentComplete / 100) * 100.53;
                        circle.style.strokeDashoffset = offset;
                    }
                    if (text) {
                        if (percentComplete >= 100) {
                            text.innerText = "Routing...";
                        } else {
                            text.innerText = percentComplete + "%";
                        }
                    }
                }
            };
            
            xhr.onload = function() {
                let overlay = document.getElementById('upload-progress-' + uniqueId);
                if (xhr.status === 200) {
                    if (overlay) overlay.style.display = 'none';
                } else {
                    if (overlay) overlay.innerHTML = "<span style='color:#ff5252;'>Upload Failed</span>";
                }
            };

            const formData = new FormData();
            formData.append("file", file);
            formData.append("target", chatMode);
            formData.append("sid", socket.id);
            
            xhr.send(formData);
            inputElem.value = ""; 
        }

        function sendMessage() {
            const input = document.getElementById('chat-input');
            const text = input.value.trim();
            if (!text) return;

            if (text.startsWith("/pm ")) {
                const target = text.split(" ")[1].trim();
                const select = document.getElementById("user-select");
                
                if (target.toLowerCase() === "exit") {
                    changeChatMode('all');
                    select.value = 'all';
                } else {
                    changeChatMode(target);
                    if (![...select.options].some(o => o.value === target)) {
                        const opt = document.createElement('option');
                        opt.value = escapeHTML(target);
                        opt.innerText = '🔒 PM: ' + escapeHTML(target);
                        select.appendChild(opt);
                    }
                    select.value = target;
                }
                input.value = '';
                return;
            }

            socket.emit('send_msg', { text: text, target: chatMode });
            input.value = '';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)

def stream_to_tor(sock, packet):
    """Feeds the socket in 64KB chunks to avoid OS/Tor buffer overflow."""
    chunk_size = 65536
    for i in range(0, len(packet), chunk_size):
        sock.sendall(packet[i:i+chunk_size])

@app.route('/api/upload_chat_file', methods=['POST'])
def api_upload_chat_file():
    sid = request.form.get('sid')
    target = request.form.get('target')
    file = request.files.get('file')
    
    if not file or not sid:
        return jsonify({'status': 'error', 'msg': 'Missing data'}), 400
        
    client = active_sessions.get(sid)
    if not client:
        return jsonify({'status': 'error', 'msg': 'Not authenticated'}), 401
        
    file_bytes = file.read()
    filename = file.filename
    
    try:
        encrypted_data, salt, nonce = crypto.encrypt_data(file_bytes, client["password"])
        header = f"{client['username']}::{target}::{filename}|".encode()
        packet = b"FILE_DATA::" + header + salt + nonce + encrypted_data + b"::NOVA_FILE_END::"
        
        # Stream it chunk-by-chunk to keep Tor happy
        stream_to_tor(client["socket"], packet)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@socketio.on('stego_hide')
def handle_stego_hide(data):
    try:
        infected = stego.hide_text(data['cover'], data['secret'], data['password'])
        emit('stego_result', {'status': 'success', 'result': infected})
    except Exception as e:
        emit('stego_result', {'status': 'error', 'msg': str(e)})

@socketio.on('stego_reveal')
def handle_stego_reveal(data):
    try:
        secret = stego.reveal_text(data['infected'], data['password'])
        emit('stego_result', {'status': 'success', 'result': secret})
    except Exception as e:
        emit('stego_result', {'status': 'error', 'msg': str(e)})

@socketio.on('payload_create')
def handle_payload_create(data):
    try:
        file_bytes = data['data']
        filename = data['filename']
        password = data['password']
        
        encrypted_data, salt, nonce = crypto.encrypt_data(file_bytes, password)
        final_binary = file_format.pack_nv_file(filename, salt, nonce, encrypted_data)
        payload_str = nova_payload.create_payload(final_binary)
        
        emit('payload_result', {'status': 'success', 'action': 'create', 'result': payload_str})
    except Exception as e:
        emit('payload_result', {'status': 'error', 'msg': str(e)})

@socketio.on('payload_restore')
def handle_payload_restore(data):
    try:
        payload_str = data['payload']
        password = data['password']
        
        nv_data = nova_payload.extract_payload(payload_str)
        original_filename, salt, nonce, encrypted_data = file_format.unpack_nv_file(nv_data)
        decrypted_data = crypto.decrypt_data(encrypted_data, password, salt, nonce)
        
        safe_name = re.sub(r'[^a-zA-Z0-9\.\-_]', '_', original_filename)
        filepath = os.path.join(DOWNLOAD_DIR, safe_name)
        with open(filepath, "wb") as f:
            f.write(decrypted_data)
        
        emit('payload_result', {'status': 'success', 'action': 'restore', 'filename': safe_name})
    except Exception as e:
        emit('payload_result', {'status': 'error', 'msg': str(e)})

def process_file_data(packet, client, sid):
    try:
        raw = packet[len(b"FILE_DATA::"):]
        header, blob = raw.split(b"|", 1)
        header_str = header.decode(errors='ignore')
        
        target = "all"
        if "::" in header_str:
            sender, target, fname = header_str.split("::", 2)
        else:
            return
            
        if target != "all" and target != client["username"]:
            return 
        
        if sender == client["username"]:
            return
        
        salt = blob[:16]
        nonce = blob[16:28]
        enc = blob[28:]
        
        decrypted_bytes = crypto.decrypt_data(enc, client["password"], salt, nonce)
        filepath = os.path.join(DOWNLOAD_DIR, fname)
        with open(filepath, "wb") as f:
            f.write(decrypted_bytes)
        
        ext = fname.split('.')[-1].lower() if '.' in fname else ''
        file_type = 'unknown'
        if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp']: file_type = 'image'
        elif ext in ['mp4', 'webm', 'ogg', 'mov']: file_type = 'video'
        elif ext in ['mp3', 'wav', 'ogg', 'm4a']: file_type = 'audio'
        elif ext in ['txt', 'pdf', 'doc', 'docx', 'csv', 'py', 'json', 'html']: file_type = 'document'
        
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', fname)
        socketio.emit('file_ready', {
            'filename': fname, 
            'file_type': file_type, 
            'sender': sender,
            'target': target,
            'safeName': safe_name
        }, to=sid)
    except Exception as e:
        socketio.emit('chat_message', {'type': 'system', 'text': f"❌ Error: File stream dropped bytes."}, to=sid)

def process_msg_data(packet, client, sid):
    try:
        msg = protocol.decode_message(packet, client["password"])
        if "]: " in msg:
            sender_part, text = msg.split("]: ", 1)
            if "[PM from " in sender_part:
                sender = sender_part.replace("[PM from ", "")
                socketio.emit('chat_message', {'type': 'pm', 'sender': sender, 'text': text}, to=sid)
            else:
                sender = sender_part.replace("[", "")
                socketio.emit('chat_message', {'type': 'msg', 'sender': sender, 'text': text}, to=sid)
        else:
            socketio.emit('chat_message', {'type': 'system', 'text': msg}, to=sid)
    except Exception as e:
        pass

def receive_loop(sid):
    client = active_sessions.get(sid)
    if not client: return

    while client["running"]:
        try:
            data = client["socket"].recv(65536)
            if not data: break
            
            # 🛡️ THE MEMORY FIX: bytearray.extend() completely eliminates O(N^2) memory reallocation
            client["buffer"].extend(data)
            
            while True:
                idx_file = client["buffer"].find(b"::NOVA_FILE_END::")
                idx_msg = client["buffer"].find(b"::NOVA::")
                
                if idx_file == -1 and idx_msg == -1:
                    if client["buffer"].startswith(b"[+]") or client["buffer"].startswith(b"[-]") or client["buffer"].startswith(b"USERS::") or client["buffer"].startswith(b"[SERVER]") or client["buffer"].startswith(b"DEL_FILE::"):
                        buf_str = client["buffer"].decode(errors='ignore')
                        
                        if buf_str.startswith("DEL_FILE::"):
                            _, fname = buf_str.split("::", 1)
                            filepath = os.path.join(DOWNLOAD_DIR, fname)
                            if os.path.exists(filepath):
                                try: os.remove(filepath)
                                except: pass
                            
                            safe_name = re.sub(r'[^a-zA-Z0-9]', '', fname)
                            socketio.emit('file_deleted', {'safeName': safe_name}, to=sid)
                        
                        elif buf_str.startswith("USERS::"):
                            users_str = buf_str.split("::", 1)[1]
                            socketio.emit('update_users', {'users': users_str.split(',')}, to=sid)
                            
                        else:
                            socketio.emit('chat_message', {'type': 'system', 'text': buf_str}, to=sid)
                            if "[+]" in buf_str or "[-]" in buf_str:
                                socketio.emit('trigger_user_refresh', {}, to=sid)
                        
                        client["buffer"].clear()
                    break
                
                # We found a packet, slice it out efficiently
                if idx_file != -1 and (idx_msg == -1 or idx_file < idx_msg):
                    packet = bytes(client["buffer"][:idx_file])
                    del client["buffer"][:idx_file + len(b"::NOVA_FILE_END::")]
                    process_file_data(packet, client, sid)
                elif idx_msg != -1:
                    packet = bytes(client["buffer"][:idx_msg])
                    del client["buffer"][:idx_msg + len(b"::NOVA::")]
                    if packet:
                        process_msg_data(packet, client, sid)
                
        except Exception as e:
            break
            
    if sid in active_sessions:
        try:
            active_sessions[sid]["socket"].close()
        except:
            pass

def background_connect(sid, data):
    onion = data['onion']
    user = data['user']
    pwd = data['pass']
    
    port = 9999
    if ":" in onion:
        onion, port = onion.split(":")
        port = int(port)

    s = socks.socksocket()
    
    if onion != "127.0.0.1" and onion != "localhost":
        s.set_proxy(socks.SOCKS5, TOR_PROXY[0], TOR_PROXY[1])
        
    try:
        s.settimeout(45.0)
        s.connect((onion, port))
        s.settimeout(None) 
        
        auth_packet = f"AUTH::{user}::{pwd}"
        s.send(auth_packet.encode())
        
        response = s.recv(1024).decode()
        if "[!]" in response:
            socketio.emit('login_response', {'status': 'error', 'msg': response}, to=sid)
            s.close()
            return
            
        active_sessions[sid] = {
            "socket": s,
            "username": user,
            "password": pwd,
            "running": True,
            "buffer": bytearray() # 🛡️ High Performance bytearray stream initialized here
        }
        
        socketio.emit('login_response', {'status': 'success'}, to=sid)
        receive_loop(sid)
        
    except Exception as e:
        socketio.emit('login_response', {'status': 'error', 'msg': f"Tor Connection failed/timed out: {e}"}, to=sid)

@socketio.on('login')
def handle_login(data):
    socketio.start_background_task(background_connect, request.sid, data)

@socketio.on('delete_file')
def handle_delete_file(data):
    sid = request.sid
    client = active_sessions.get(sid)
    if not client: return
    fname = data['filename']
    client["socket"].sendall(f"DEL_FILE::{fname}".encode())
    
    filepath = os.path.join(DOWNLOAD_DIR, fname)
    try: os.remove(filepath)
    except: pass

@socketio.on('send_msg')
def handle_send(data):
    sid = request.sid
    client = active_sessions.get(sid)
    if not client: return
    
    msg = data['text']
    target = data.get('target', 'all')
    s = client["socket"]
    username = client["username"]
    password = client["password"]
    
    if msg == "/users":
        s.sendall(b"CMD::USERS")
    elif msg.startswith("/msg "):
        try:
            _, target_user, text = msg.split(" ", 2)
            payload = protocol.encode_message(f"[PM from {username}]: {text}", password)
            s.sendall(f"PM::{target_user}::".encode() + payload)
            emit('chat_message', {'type': 'msg', 'sender': username, 'text': f"[PM to {target_user}]: {text}"})
        except:
            emit('chat_message', {'type': 'system', 'text': "Usage: /msg <user> <message>"})
    else:
        if target == 'all':
            payload = protocol.encode_message(f"[{username}]: {msg}", password)
            s.sendall(payload)
            emit('chat_message', {'type': 'msg', 'sender': username, 'text': msg})
        else:
            payload = protocol.encode_message(f"[PM from {username}]: {msg}", password)
            s.sendall(f"PM::{target}::".encode() + payload)
            emit('chat_message', {'type': 'msg', 'sender': username, 'text': f"[PM to {target}]: {msg}"})

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in active_sessions:
        active_sessions[sid]["running"] = False
        try:
            active_sessions[sid]["socket"].close()
        except:
            pass
        del active_sessions[sid]

if __name__ == "__main__":
    print(f"[*] Starting NovaChat Web UI on http://127.0.0.1:5000")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False, allow_unsafe_werkzeug=True)