import cv2
import os
import pytesseract
import fitz  # PyMuPDF

import shutil
import tempfile
import wand.image

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

directory_path = './data'



# DIRECTLY READING SYMBOLIC INFO FROM PDF
# ================================================================================
def extract_text_from_pdf(pdf_path):
  text = ""
  pdf_document = fitz.open(pdf_path)
  for page_num in range(pdf_document.page_count):
    page = pdf_document.load_page(page_num)
    text += page.get_text()

  return text

def extract_pdf_metadata(pdf_path):
  pdf_document = fitz.open(pdf_path)
  metadata = pdf_document.metadata
  num_pages = pdf_document.page_count
  page_info = []

  for page_num in range(num_pages):
    page = pdf_document.load_page(page_num)
    size = page.rect
    rotation = page.rotation
    images = page.get_images(full=True)
    page_info.append({
      "page_num": page_num + 1,
      "size": size,
      "rotation": rotation,
      "num_images": len(images),
    })

  return metadata, num_pages, page_info

def extract_text_and_metadata_from_pdf(pdf_path):
  metadata, num_pages, page_info = extract_pdf_metadata(pdf_path)

  pdf_extracted_info = []
  pdf_extracted_info.append("PDF Metadata:")
  for key, value in metadata.items():
      pdf_extracted_info.append(f"{key}: {value}")

  pdf_extracted_info.append(f"\nNumber of Pages: {num_pages}", )

  pdf_extracted_info.append("\nPage Information:")
  for info in page_info:
      pdf_extracted_info.append(str(info))

  text_content = extract_text_from_pdf(pdf_path)
  pdf_extracted_info.append(text_content)

  pdf_extracted_info = '\n'.join(pdf_extracted_info)
  return pdf_extracted_info
# ================================================================================



# Iterate through the directory
for root, dirs, files in os.walk(directory_path):
  for filename in files:

    filename_without_suffix, _ = os.path.splitext(filename)
    folder_path = f'computed/{filename_without_suffix}'
    if os.path.exists(folder_path): continue

    print(f"Making searchable: {filename}")
    pdf_path = f'data/{filename}'

    metadata_and_text = extract_text_and_metadata_from_pdf(pdf_path)

    # Initialize the combined text
    combined_text = f"{pdf_path}\n"
    combined_text += "========================================================\n"
    combined_text += metadata_and_text
    combined_text += "========================================================\n"

    # Read the PDF and convert pages to images
    with wand.image.Image(filename=pdf_path, resolution=300) as pdf:
      for _, page in enumerate(pdf.sequence):
        with wand.image.Image(page) as image_from_single_page:
          image_from_single_page.compression_quality = 100
          image_from_single_page.format = 'jpg'

          # Create a temporary file for the image
          with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
            image_from_single_page.save(filename=temp_img.name)
            jpg_name = temp_img.name

          # Load the input image
          image_from_single_page = cv2.imread(jpg_name)

          # Rotate the image in all four directions and extract text
          for angle in [0, 90, 180, 270]:
            # Rotate the image
            center = (image_from_single_page.shape[1] / 2, image_from_single_page.shape[0] / 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
              image_from_single_page,
              M,
              (image_from_single_page.shape[1], image_from_single_page.shape[0]),
            )

            # Generate the output file name
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_txt:
              output_file = temp_txt.name

            # Apply Tesseract to the rotated image and save the output to a file
            text = pytesseract.image_to_string(rotated, lang='fra+deu')
            with open(output_file, "w") as f:
              f.write(text)

            # Read the output file and append the text to combined_text
            with open(output_file, "r") as f:
              text = f.read()
              combined_text += text

            # Clean up the temporary output file
            os.remove(output_file)

          # Clean up the temporary image file
          os.remove(jpg_name)


    # Create a searchable item (as a folder with two files).
    os.makedirs(folder_path, exist_ok = True)
    shutil.copy(pdf_path, folder_path)
    combined_filename = f"{folder_path}/{filename_without_suffix}.txt"
    with open(combined_filename, "w") as f:
      f.write(combined_text)
    print("Done.")
