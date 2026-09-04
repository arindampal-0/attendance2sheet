"""main file"""
import sys

import streamlit

def main() -> int:
    """main function"""
    print("Attendance2Sheet")

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
            streamlit.image(image)

    return 0

if __name__ == "__main__":
    sys.exit(main())