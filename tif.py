import streamlit as st
from PIL import Image
import os
import zipfile
import tempfile

# Define the function to convert TIF to JPG
def convert_tif_to_jpg(input_path, output_path, new_size=(800, 600), max_size_mb=3):
    """
    Convert a TIF image to JPG, resize it, and reduce size to a maximum of 3 MB.
    
    :param input_path: Path to the input TIF file
    :param output_path: Path to save the output JPG file
    :param new_size: Tuple (width, height) for resizing
    :param max_size_mb: Maximum allowed file size in MB
    """
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGB")  # Convert to RGB (JPG doesn't support transparency)
            img = img.resize(new_size, Image.LANCZOS)  # Resize image
            quality = 95
            img.save(output_path, "JPEG", quality=quality)  # Initial save
            
            # Reduce file size if necessary
            while os.path.getsize(output_path) > max_size_mb * 1024 * 1024 and quality > 10:
                quality -= 5
                img.save(output_path, "JPEG", quality=quality)
            
            return output_path
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Title for the app
st.title("TIF to JPG Converter")

# Upload multiple TIF files
uploaded_files = st.file_uploader("Upload TIF images", type=["tif", "tiff"], accept_multiple_files=True, help="Upload up to 2GB of TIF images")

# Resize parameters
resize_width = st.number_input("Width", min_value=1, value=1024)
resize_height = st.number_input("Height", min_value=1, value=768)

# Process the uploaded files
if uploaded_files:
    output_files = []
    
    # Create a temporary directory to store the files
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            input_tif = os.path.join(temp_dir, f"temp_{uploaded_file.name}")
            output_jpg = os.path.splitext(input_tif)[0] + ".jpg"
            
            # Save the uploaded file temporarily
            with open(input_tif, "wb") as f:
                f.write(uploaded_file.read())
            
            # Convert the TIF to JPG
            converted_path = convert_tif_to_jpg(input_tif, output_jpg, (resize_width, resize_height))
            
            # If conversion was successful, add to the list
            if converted_path:
                output_files.append(converted_path)
        
        # Create a ZIP file for all converted images
        if output_files:
            zip_filename = "converted_images.zip"
            with zipfile.ZipFile(zip_filename, "w") as zipf:
                for file in output_files:
                    zipf.write(file, os.path.basename(file))
            
            # Provide a download button for the ZIP file
            with open(zip_filename, "rb") as zipf:
                st.download_button("Download All Images", zipf, file_name=zip_filename, mime="application/zip")
