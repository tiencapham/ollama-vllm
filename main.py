import streamlit as st
import requests
import json
import base64
# --- Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/chat"
# IMPORTANT: Ensure you have pulled this model with 'ollama pull openbmb/minicpm-o2.6:8b'
DEFAULT_MODEL = "openbmb/minicpm-o2.6:8b" 

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Personal Ollama Multimodal Chat Agent", layout="centered")
st.title("💬 Personal Ollama Multimodal Chat Agent")
st.caption(f"Powered by Ollama (running {DEFAULT_MODEL} locally)")

# Initialize chat history and pending image in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
# Use a session state key to force uploader to reset by changing the key
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0
# Use a session state key to force uploader to reset by changing the key
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = 0

# --- Function to interact with Ollama ---
def get_ollama_response(current_user_message_parts , model=DEFAULT_MODEL):
    """
    Sends a chat request to the Ollama API and returns the model's response.
    Includes previous messages (text and images) for context.
    """
    headers = {"Content-Type": "application/json"}
    
    data = {
        "model": model,
        "messages": current_user_message_parts,
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data), stream=True, timeout=600)
        response.raise_for_status()
        
        full_response_content = ""
        message_placeholder = st.empty()

        for line in response.iter_lines():
            if line:
                try:
                    json_data = json.loads(line.decode('utf-8'))
                    
                    # Debugging: Uncomment to see each raw chunk
                    # st.write("Ollama API Raw Chunk (for debugging):", json_data)

                    if "message" in json_data and isinstance(json_data["message"], dict) and "content" in json_data["message"]:
                        content = json_data["message"]["content"]
                        full_response_content += content
                        message_placeholder.markdown(full_response_content + "▌") # Blinking cursor
                    elif "done" in json_data and json_data["done"]:
                        break
                except json.JSONDecodeError:
                    st.error(f"Failed to decode JSON chunk from Ollama. Raw chunk: {line.decode('utf-8')}")
                except Exception as e:
                    st.error(f"An unexpected error occurred while processing stream chunk: {e}")

        message_placeholder.markdown(full_response_content) # Final content without cursor
        return full_response_content

    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Could not connect to Ollama server at {OLLAMA_API_URL}. "
                 "Please ensure Ollama is running and the model is available.")
        return "Error: Ollama server is not reachable."
    except requests.exceptions.Timeout:
        st.error("Timeout Error: Ollama took too long to respond. "
                 "The model might be busy or the request is too complex.")
        return "Error: Ollama response timed out."
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while calling the Ollama API: {e}")
        return f"Error: {e}"
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return "Error: An unexpected error occurred."

# Display past conversation using chat bubbles
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- User input and chat logic ---

# File uploader for images
# This will update st.session_state.pending_image when a file is uploaded
uploaded_image = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"], key=f"uploader_{st.session_state.upload_key}")
if uploaded_image is not None:
    print(f"check debug upload file")
    st.session_state.uploaded_file = uploaded_image.read()
# Text input for prompt
# This will trigger the message sending logic
prompt = st.chat_input("Ask me anything...")

if prompt: # Only proceed if a text prompt is entered
    if st.session_state.uploaded_file is not None:
    # Read image as bytes and encode to base64
        image_base64 = base64.b64encode(st.session_state.uploaded_file).decode('utf-8')
        msg = {"role": "user", "content": prompt, "images": [image_base64]}
        # Clear the pending image after it's used
        # Clear the uploader widget visually
        print(f"check debug {uploaded_image}")
        st.session_state.uploaded_file = None # This might not immediately clear the widget in all Streamlit versions, but helps manage state.
        st.session_state.upload_key += 1
        uploaded_image = None
    else: 
        msg = {"role": "user", "content": prompt,  "images": None}

    # Display the combined user message (image + text) in the chat
    with st.chat_message("user"):
        st.markdown(msg["content"])
        if msg["images"] is not None:
            for image in msg["images"] :
                st.image(f"data:png;base64,{image}", use_column_width=True)

    # Add combined user message (text and/or image) to chat history
    st.session_state.messages.append(msg)

    # Get response from Ollama
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Pass only the current user message parts for the API call,
            full_response = get_ollama_response(st.session_state.messages)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response, "images": None})

