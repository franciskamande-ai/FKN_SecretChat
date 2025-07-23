# FKN SecretChat by Kamande (MVP v1)
import streamlit as st
import os
from datetime import datetime

# === CONFIG ===
CHAT_FILE = "chat_log.txt"
MEDIA_FOLDER = "media"
SECRET_CODE = "fknbestie42"

# === SETUP ===
os.makedirs(MEDIA_FOLDER, exist_ok=True)
st.set_page_config(page_title="FKN SecretChat 💌", layout="centered")

# === STYLE ===
st.markdown("""
<style>
body {
  background-image: url('https://i.pinimg.com/originals/b4/10/1e/b4101e5f4127508288b6971fa64c305e.gif');
  background-size: cover;
  color: #00FFAD !important;
  font-family: 'Courier New', monospace;
}
p, label, .stTextInput>div>div>input {
  color: #00FFAD !important;
}
.chat-bubble {
  background: rgba(0,0,0,0.6);
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 10px;
}
img, video {
  max-width: 300px;
  border: 2px solid #00FFAD;
  border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# === AUTH ===
st.title("💌 FKN SecretChat")

secret = st.text_input("Enter access code:", type="password")
if secret != SECRET_CODE:
    st.warning("🔐 Secret code required.")
    st.stop()

st.success("🎉 Welcome to your haven.")

# === CHAT HISTORY DISPLAY ===
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        history = f.read()
        st.markdown(history, unsafe_allow_html=True)

# === SEND MESSAGE ===
msg = st.text_input("Type your message:")
if st.button("Send Message"):
    timestamp = datetime.now().strftime("%H:%M")
    new_line = f"<div class='chat-bubble'><b>You ({timestamp}):</b> {msg}</div>\n"
    with open(CHAT_FILE, "a", encoding="utf-8") as f:
        f.write(new_line)
    st.rerun()

# === MEDIA UPLOAD ===
uploaded = st.file_uploader("📎 Send a photo/video", type=["jpg", "png", "mp4", "mov"])
if uploaded:
    media_path = os.path.join(MEDIA_FOLDER, uploaded.name)
    with open(media_path, "wb") as f:
        f.write(uploaded.read())

    timestamp = datetime.now().strftime("%H:%M")

    if uploaded.type.startswith("image"):
        tag = f"<div class='chat-bubble'><b>You ({timestamp}):</b><br><img src='{media_path}'></div>\n"
    elif uploaded.type.startswith("video"):
        tag = f"<div class='chat-bubble'><b>You ({timestamp}):</b><br><video controls src='{media_path}'></video></div>\n"
    else:
        tag = f"<div class='chat-bubble'><b>You ({timestamp}):</b> File sent: {uploaded.name}</div>\n"

    with open(CHAT_FILE, "a", encoding="utf-8") as f:
        f.write(tag)
    st.success("Media sent.")
    st.rerun()
