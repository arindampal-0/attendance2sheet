"""main file"""
from PIL import Image, ImageDraw, ImageFont
import json

import streamlit
from google import genai
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

@streamlit.cache_resource
def get_gemini_client():
    """create gemini client"""
    return genai.Client()

client = get_gemini_client()

class RollNoDetection(BaseModel):
    """Roll Number Detection data"""
    rollno_text: str = Field(description="roll number text.")
    bounding_box: list[int] = Field(
        min_length=4, max_length=4,
        description="bounding box in the image from where roll number was " \
        "extracted (x_min, y_min, x_max, y_max) all integers " \
        "normalized coordinates between 0 and 1000."
        )
    confidence_score: int = Field(
        ge=0, le=10,
        description="how confident the model is on the predicted result, " \
        "0 is not confident, 10 is very confident.")
    any_comments: str = Field(
        description="comments about the image to text conversion if any, " \
        "empty string if no comments.")

detection_list_adapter = TypeAdapter(list[RollNoDetection])

available_models = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.8-flash"]

@streamlit.cache_data(scope="session", show_spinner=False)
def extract_rollno(image_name: str, _image_bytes: bytes, mimetype: str,
                    model: str) -> list[RollNoDetection]:
    """extract roll numbers from the image of attendance sheet"""
    response = client.models.generate_content(
        model=model,
        contents=[
            genai.types.Part.from_bytes(
                data=_image_bytes,
                mime_type=mimetype
            ),
            f"The image {image_name} is of attendance sheet containing handwritten roll " \
            "numbers. The roll numbers are of the form 22CS02xxx, 23CS01xxx, " \
            "23EC01xxx, 23EC01xxx, 25CL05xxx, 26AI06xxx, 26CL06xxx, 26CS06xxx, " \
            "26RA06xxx, A26CS08xxx, S26CS08xxx, A26CS09xxx, S26CS09xxx, " \
            "A26EC08xxx, A26EC09xxx, S26EC09xxx, A26EE09xxx, A26MA09xxx, " \
            "something like these. Extract all the roll numbers from the image " \
            "of the attendance sheet as a list of roll numbers (string) along " \
            "with bounding box (x_min, y_min, width, height) all integers " \
            "and are normalized coordinates between 0 and 1000, comments " \
            "regarding conversion (if any), and confidence score between " \
            "0 and 10, 0 is not confident and 10 is very confident. Extract " \
            "the roll numbers in the same sequence as written in the image."
        ],
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[RollNoDetection]
        )
    )

    if response.parsed:
        try:
            detection_list = detection_list_adapter.validate_python(response.parsed)
            return detection_list
        except ValidationError:
            streamlit.error("Error during validating the model response.")

    return []

@streamlit.cache_data(scope="session")
def visualize_detection(image: streamlit.typing.UploadedFile, detection: RollNoDetection):
    """visualize detection"""
    pass


streamlit.title("Attendance2Sheet")
streamlit.header("Upload the attendance sheet photo")
image = streamlit.file_uploader(
    "Upload the attendance sheet image", 
    key="uploaded_image",
    type="image/*",
    max_upload_size=10,
    accept_multiple_files=False,
)

if "uploaded_image" not in streamlit.session_state:
    streamlit.error("uploaded_image not in session_state")
    streamlit.session_state["uploaded_image"] = None

# print(image_data)
# if len(image_data) > 0:
#     for image in image_data:
#         print(image)
#         print(image.type)
#         streamlit.image(image)

image = streamlit.session_state["uploaded_image"]
streamlit.write(image)
if image and isinstance(image, streamlit.typing.UploadedFile):
    streamlit.image(image)

# if image:
#     streamlit.write(image)
#     streamlit.image(image)

selected_model = streamlit.selectbox("Select model", available_models, index=0)
if not isinstance(selected_model, str) or selected_model not in available_models:
    streamlit.error(f"Incorrect model selected: {selected_model}")
# streamlit.write(selected_model)

extract_button = streamlit.button("Extract")
# streamlit.write(extract_button)

if "detections" not in streamlit.session_state:
    streamlit.session_state["detections"] = []

while extract_button:
    # streamlit.write("button pressed")

    if image is None:
        streamlit.error("Upload image of attendance sheet.")
        break

    if not isinstance(selected_model, str):
        streamlit.error("selected model is not str")
        break

    image_data = image.getvalue()
    image_mimetype = image.type
    with streamlit.spinner("Model is processing..."):
        detections = extract_rollno(image.name, image_data, image_mimetype, selected_model)
        streamlit.session_state["detections"] = detections

    break

detections = streamlit.session_state["detections"]
streamlit.write(streamlit.session_state["detections"])
streamlit.code(body=json.dumps([
    {
        "roll_text": d.rollno_text,
        "bounding_box": d.bounding_box
    } for d in streamlit.session_state["detections"]]))

image_font = ImageFont.load_default(size=20)

if "current_index" not in streamlit.session_state:
    streamlit.session_state["current_index"] = 0

def increment_index():
    """increment index"""
    if len(detections) > 0:
        streamlit.session_state["current_index"] += 1
        if streamlit.session_state["current_index"] >= len(detections):
            streamlit.session_state["current_index"] = 0

def decrement_index():
    """decrement_index"""
    if len(detections) > 0:
        streamlit.session_state["current_index"] -= 1
        if streamlit.session_state["current_index"] < 0:
            streamlit.session_state["current_index"] = len(detections) - 1

with streamlit.container(
    width="content", height="content",
    horizontal=True, horizontal_alignment="left",
    vertical_alignment="center", gap=5):
    streamlit.write("Change index:")
    if streamlit.button("Prev", icon="⬅️"):
        decrement_index()
    if streamlit.button("Next", icon="➡️"):
        increment_index()

index = streamlit.session_state["current_index"]

with streamlit.container(
    width="content", height="content",
    horizontal=True, horizontal_alignment="left",
    vertical_alignment="center", gap=5):
    streamlit.write("Index: ")
    streamlit.write(index)

if index >= 0 and index < len(detections):
    streamlit.write(detections[index])

if image:
    viz_image = Image.open(image)
    with streamlit.container(width="content", height="content",
                             horizontal=True, horizontal_alignment="left",
                             vertical_alignment="center", gap=5):
        streamlit.write("image_size:")
        streamlit.write(viz_image.size)
    draw = ImageDraw.Draw(viz_image)
    draw.rectangle(
        [4, 4, viz_image.size[0] - 4, viz_image.size[1] - 4],
        outline="blue", width=2
    )

    DISPLAY_W = 720
    scale = DISPLAY_W / viz_image.size[0]

    if index >= 0 and index < len(detections):
        detection = detections[index]
        x1 = (detection.bounding_box[0] * viz_image.size[0] // 1000) - 2
        y1 = (detection.bounding_box[1] * viz_image.size[1] // 1000) - 2
        x2 = (detection.bounding_box[2] * viz_image.size[0] // 1000) + 2
        y2 = (detection.bounding_box[3] * viz_image.size[1] // 1000) + 2
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        # draw.rectangle((x2 + 4, y1 - 1, x2 + 130, y1 + 24), fill="white")
        # draw.text((x2 + 5, y1), detection.rollno_text, fill="red", font=image_font)

        with streamlit.container(key="stage"):
            streamlit.image(viz_image, width=DISPLAY_W)
            with streamlit.container(key="controls", width="content",
                                     height="content", horizontal=True,
                                     horizontal_alignment="center",
                                     vertical_alignment="center", gap=5):
                val = streamlit.text_input("Roll", detection.rollno_text, key=f"v{index}", label_visibility="collapsed", width=150)
                accept = streamlit.button("✅", key=f"a{index}")
                reject = streamlit.button("❌", key=f"r{index}")

        if accept:
            # detection.rollno_text = val
            streamlit.toast("Accept button pressed.", icon="✅")

        x1, y1, x2, y2 = [int(c * scale) for c in [x1, y1, x2, y2]]
        streamlit.html(f"""
        <style>
            .st-key-stage {{ 
                position: relative;
                # width: {DISPLAY_W}px;
            }}
            
            .st-key-controls {{
                position: absolute;
                left: {x1}px;
                top: {y2 + 2}px;
                z-index: 10;
                background: rgba(255, 255, 255, .60);
                border-radius: 5px;
                padding: 6px 8px;
                width: auto;
            }}

            .st-key-controls input {{
                font-size: 20px;
                font-weight: 600;
                text-align: center;
            }}
        </style>
        """)

    # streamlit.image(viz_image)
