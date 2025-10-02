import streamlit as st
from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash"
GEMINI_API_KEY = "AIzaSyDCpcuyqpw10Lke4w5g8R04vNXdnGuccqM"
# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="Automotive Safety Standards Chatbot", page_icon="🤖")
st.title("🚗 Automotive Safety Standards Chatbot")
st.write("Choose a standard and ask your question!")

# Sidebar standard selection
standard = st.sidebar.radio(
    "Select a standard:",
    ("ISO 26262", "ISO 21434 & GB 44495")
)

# System instruction depending on standard
if standard == "ISO 26262":
    system_instruction = (
        "You are an expert in ISO 26262, specializing in functional safety for automotive systems. "
        "Provide clear, precise, and technically correct answers."
    )
else:
    system_instruction = (
        "You are an automotive cybersecurity expert. "
        "Provide accurate and detailed guidance according to ISO 21434. "
        "If the user asks in Chinese or refers to GB 44495, respond in Chinese and explain based on GB 44495 (Chinese version of ISO 21434)."
    )

# ------------------------------
# Session state for history
# ------------------------------
if "messages" not in st.session_state or st.session_state.get("active_standard") != standard:
    st.session_state["messages"] = []
    st.session_state["active_standard"] = standard

# Display previous chat
for msg in st.session_state["messages"]:
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        st.markdown(msg["content"])

# ------------------------------
# Chat input
# ------------------------------
if user_input := st.chat_input(f"Ask your question about {standard}..."):
    # Save user input
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare Gemini content
    contents = [types.Content(role="user", parts=[types.Part.from_text(user_input)])]

    # Config with system instruction
    config = types.GenerateContentConfig(system_instruction=system_instruction)

    # Stream Gemini response
    with st.chat_message("assistant"):
        response_text = ""
        placeholder = st.empty()

        for chunk in client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
            config=config
        ):
            if hasattr(chunk, "text") and chunk.text:
                response_text += chunk.text
                placeholder.markdown(response_text + "▌")

        placeholder.markdown(response_text)

    # Save assistant message
    st.session_state["messages"].append({"role": "assistant", "content": response_text})
