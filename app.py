import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import base64

# Folder paths
CHAT_DIR = Path("chat")
MEDIA_DIR = CHAT_DIR / "media"
CHAT_FILE = CHAT_DIR / "chat_log.txt"

# Create folders if not exist
CHAT_DIR.mkdir(exist_ok=True)
MEDIA_DIR.mkdir(exist_ok=True)
CHAT_FILE.touch(exist_ok=True)

# Page config
st.set_page_config(page_title="EchoChomms", layout="centered")

# Custom Background Styling (Preserve user-defined aesthetic)
st.markdown("""
    <style>
    body {
        background-color: #1f1f2e;
        color: #ffffff;
    }

    .stApp {
        background: linear-gradient(to bottom right, #1e1e2f, #3a3a6a);
        color: #f0f0f0;
        font-family: 'Courier New', monospace;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #00ffcc;
        text-shadow: 0 0 5px #00ffcc;
    }

    .stTextInput>div>div>input {
        background-color: #2a2a40;
        color: #00ffcc;
        border: 1px solid #00ffcc;
    }

    .stButton>button {
        background-color: #00cc88;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0 0 10px #00ffcc;
    }

    .stMarkdown {
        color: #ffffff;
    }

    ::placeholder {
        color: #cccccc;
    }

    img {
        border: 2px solid #00ffcc;
        border-radius: 10px;
    }

    .title {
        color: #00ffcc;
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        text-shadow: 0px 0px 5px #00ffcc;
    }
    .footer {
        color: #cccccc;
        text-align: center;
        font-size: 0.8em;
        margin-top: 2em;
    }
    .chat-box {
        background-color: rgba(0,0,0,0.6);
        padding: 1em;
        border-radius: 12px;
        max-height: 500px;
        overflow-y: scroll;
        color: white;
    }
    .chat-bubble {
        margin: 0.5em 0;
        padding: 0.5em;
        border-radius: 10px;
    }
    .chat-bubble.me {
        background-color: #005555;
        text-align: right;
    }
    .chat-bubble.you {
        background-color: #220022;
    }
    .chat-image {
        max-width: 80%;
        border-radius: 10px;
        margin-top: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">EchoComms</div>', unsafe_allow_html=True)

# Password gate
SECRET_CODE = "bestie254"
if "access_granted" not in st.session_state:
    access_code = st.text_input("Enter Secret Access Code:", type="password")
    code_button = st.button("Submit Access Code")

    if code_button:
        if access_code != SECRET_CODE:
            st.warning("Wrong code, try again.")
            st.stop()
        else:
            st.session_state["access_granted"] = True
    else:
        st.stop()

# Gender & Username setup
if "gender" not in st.session_state or "username" not in st.session_state:
    gender = st.radio("Select your gender:", ["Male", "Female"], horizontal=True)

    male_codenames = ["ShadowFox", "NightOwl", "SilentNova", "CrimsonWolf", "EchoBlade", "Null Agent"]
    female_codenames = ["LunaSkye", "VelvetWhisper", "PinkSpectre", "StarlightMuse", "CrimsonRose", "MoonDancer"]
    codenames = male_codenames if gender == "Male" else female_codenames

    username = st.selectbox("Choose your secret codename to join chat:", codenames)
    if st.button("Enter Chat"):
        st.session_state["gender"] = gender
        st.session_state["username"] = username
        st.rerun()
    else:
        st.stop()

# Use stored session values
gender = st.session_state["gender"]
username = st.session_state["username"]

# Clear Chat Button
if st.button("Clear Chat for Everyone"):
    CHAT_FILE.unlink(missing_ok=True)
    CHAT_FILE.touch()
    for file in MEDIA_DIR.glob("*"):
        file.unlink()
    st.success("Chat cleared for everyone. Reload to see.")

# Message
message = st.text_input("Type your message:", key="msg")
media_file = st.file_uploader("Send image or video (optional):", type=["png", "jpg", "jpeg", "gif", "mp4"])

if st.button("Send"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {username}: {message}\n"

    if media_file is not None:
        media_path = MEDIA_DIR / media_file.name
        with open(media_path, "wb") as f:
            f.write(media_file.getbuffer())
        entry = entry.strip() + f"|{media_file.name}\n"

    with open(CHAT_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    
    # Force real-time update
    st.session_state["last_update"] = datetime.now()
    st.rerun()

# Auto-refresh every 2 seconds
if "last_update" not in st.session_state:
    st.session_state["last_update"] = datetime.now()

if (datetime.now() - st.session_state["last_update"]).seconds > 2:
    st.session_state["last_update"] = datetime.now()
    st.rerun()

# Read and show chat
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
with open(CHAT_FILE, "r", encoding="utf-8") as f:
    for line in f.readlines():
        if not line.strip():
            continue  # Skip empty lines

        parts = line.strip().split("|")
        text_part = parts[0]

        # Skip lines that don't match the expected format
        if ": " not in text_part:
            continue

        try:
            name = text_part.split("] ")[1].split(":")[0]
            content = text_part.split(": ", 1)[1]
        except IndexError:
            continue  # Skip corrupted lines

        bubble_class = "me" if name == username else "you"

        st.markdown(
            f"<div class='chat-bubble {bubble_class}'><b>{name}:</b> {content}",
            unsafe_allow_html=True
        )

        if len(parts) > 1:
            media_part = parts[1]
            media_path = MEDIA_DIR / media_part
            ext = media_part.split(".")[-1].lower()
            if media_path.exists():
                if ext in ["png", "jpg", "jpeg", "gif"]:
                    with open(media_path, "rb") as file:
                        encoded = base64.b64encode(file.read()).decode()
                        data_url = f"data:image/{ext};base64,{encoded}"
                    st.markdown(
                        f"<a href='{data_url}' target='_blank'>"
                        f"<img src='{data_url}' class='chat-image'/></a></div>",
                        unsafe_allow_html=True
                    )
                elif ext == "mp4":
                    st.video(media_path.as_posix())
                else:
                    st.markdown(f"<div class='chat-bubble {bubble_class}'>Media not supported</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble {bubble_class}'>Media file not found</div>", unsafe_allow_html=True)
        else:
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>Made by Francis Kamande • 2025</div>", unsafe_allow_html=True)
