"""main file"""
import sys

import streamlit
from google import genai
@streamlit.cache_resource
def get_gemini_client():
    """create gemini client"""
    return genai.Client()

client = get_gemini_client()
available_models = ["gemini-3.7-flash", "gemini-3.6-flash"]

@streamlit.cache_resource(scope="session")
def generate_response(prompt: str, model: str) -> genai.types.GenerateContentResponse:
    """generate response"""
    return client.models.generate_content(
        model=model,
        contents=[prompt]
    )

streamlit.title("Attendance2Sheet")
streamlit.header("Upload the attendance sheet photo")
image_data = streamlit.file_uploader(
    "Upload the attendance sheet image", 
    type="image/*",
    max_upload_size=10,
    accept_multiple_files=True,
)

# print(image_data)
if len(image_data) > 0:
    for image in image_data:
        print(image)
        print(image.type)
        streamlit.image(image)

selected_model = streamlit.selectbox("Select model", available_models, index=0)
streamlit.write(selected_model)

input_prompt = streamlit.text_area("Enter your prompt")
send_button = streamlit.button("Send")
streamlit.write(input_prompt)
streamlit.write(send_button)

if send_button and input_prompt and \
    isinstance(selected_model, str) and selected_model in available_models:
    streamlit.write("button pressed")
    response = generate_response(input_prompt, selected_model)
    streamlit.write(response)
    if response.text:
        streamlit.divider()
        streamlit.markdown(response.text)
