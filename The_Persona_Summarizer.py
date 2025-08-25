import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import warnings
import time # We need this to create the typing effect

# This loads your secret key from the .env file
load_dotenv()

# This will hide the security warning that appears after our fix
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# This sets up the connection to the Google Gemini API
try:
    genai.configure(api_key=os.getenv("AIzaSyDBCpo8ozHlGTqWzRS3QaP7Omk2TN_PqKM"))
except AttributeError:
    st.error("Oops! The GOOGLE_API_KEY is missing. Please make sure it's in your .env file.")
    st.stop()

# --- UI Setup ---
st.set_page_config(page_title="The Persona Chat", page_icon="💬", layout="centered")
st.title("The Persona Chat 💬")
st.subheader("Choose a personality, and have a 'live' chat about your text.")

# --- Prompts and Persona Emojis ---
persona_prompts = {
    "Sarcastic Teenager 😒": {
        "prompt": "You are a cynical, unimpressed teenager...",
        "avatar": "😒"
    },
    "Excited Influencer ✨": {
        "prompt": "You are an overly-enthusiastic social media influencer...",
        "avatar": "✨"
    },
    "Grumpy Pirate 🏴‍☠️": {
        "prompt": "You are a grumpy, old pirate...",
        "avatar": "🏴‍☠️"
    },
    "Shakespearean Actor 🎭": {
        "prompt": "You are a dramatic Shakespearean actor...",
        "avatar": "🎭"
    }
}
# Remember to paste your full persona prompts back into the dictionary above

# --- Main App Layout ---
selected_persona_name = st.selectbox(
    "Choose a Persona:",
    options=list(persona_prompts.keys())
)

text_to_summarize = st.text_area("Enter the text you want to talk about...", height=150, placeholder="Paste that boring article link or corporate email here...")

model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- NEW: A function to handle the streaming response for the typing effect ---
def stream_response(response):
    for chunk in response:
        yield chunk.text
        time.sleep(0.05) # This small delay makes the typing look more natural

if st.button("Start Live Chat!", type="primary", use_container_width=True):
    if text_to_summarize:
        persona_info = persona_prompts[selected_persona_name]
        system_prompt = persona_info["prompt"]
        persona_avatar = persona_info["avatar"]
        
        full_prompt = system_prompt + "\n\nSummarize this text:\n" + text_to_summarize

        # Display the user's message immediately
        st.subheader("Your Conversation:")
        with st.chat_message("user"):
            st.write(text_to_summarize)

        # Now, get and display the AI's streaming reply
        with st.chat_message("assistant", avatar=persona_avatar):
            # The placeholder will show the "typing..." indicator
            with st.spinner("Typing..."):
                try:
                    generation_config = genai.types.GenerationConfig(temperature=0.75)
                    # --- NEW: We set stream=True to get the response piece by piece ---
                    response = model.generate_content(
                        full_prompt,
                        generation_config=generation_config,
                        stream=True
                    )
                    
                    # --- NEW: We use st.write_stream to display the typing effect ---
                    st.write_stream(stream_response(response))

                except Exception as e:
                    st.error(f"An error occurred: {e}")
    else:
        st.warning("You have to give me some text to talk about first.")

st.markdown("---")
st.info("Built with ❤️ (and a lot of personality) by a human.")

