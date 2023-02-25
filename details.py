import cv2
from info import info
import pytesseract
import os

# Set the path to the Tesseract executable (optional)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

from wand.image import Image

pdf_path = 'resources/Reisepass.pdf'
# https://duckduckgo.com/?q=PolicyError%3A+attempt+to+perform+an+operation+not+allowed+by+the+security+policy+%60PDF%27+%40+error%2Fconstitute.c%2FIsCoderAuthorized%2F408&t=brave&atb=v340-1&ia=web
# https://stackoverflow.com/questions/52998331/imagemagick-security-policy-pdf-blocking-conversion#53180170
with Image(filename=pdf_path, resolution=300) as pdf:

  combined_text = f"{pdf_path}\n"
  combined_text += "========================================================\n"
  info(combined_text)

  for i, page in enumerate(pdf.sequence):
    with Image(page) as img:
      img.compression_quality = 100
      img.format = 'jpg'
      jpg_name = f'output_{i+1}.jpg'
      img.save(filename=jpg_name)

      # Load the input image
      img = cv2.imread(jpg_name)

      # Rotate the image in all four directions and save each rotation to a file
      for angle in [0, 90, 180, 270]:
        # Rotate the image
        img = cv2.imread(jpg_name)
        # Calculate the rotation matrix
        center = (img.shape[1] / 2, img.shape[0] / 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Apply the rotation matrix to the image
        rotated = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

        # Generate the output file name
        output_file = f"output_{angle}.txt"

        # Apply Tesseract to the rotated image and save the output to a file
        text = pytesseract.image_to_string(rotated, lang='deu')
        with open(output_file, "w") as f:
          f.write(text)

      for angle in [0, 90, 180, 270]:
        output_file = f"output_{angle}.txt"
        with open(output_file, "r") as f:
          text = f.read()
          combined_text += text
          info(text)

      # Generate the output file name for the combined text

      # Clean up the temporary output files
      for angle in [0, 90, 180, 270]:
        output_file = f"output_{angle}.txt"
        os.remove(output_file)

  info(combined_text)
  combined_filename = f"{pdf_path}.txt"
  # Write the combined output text to a file
  with open(combined_filename, "w") as f:
    f.write(combined_text)
