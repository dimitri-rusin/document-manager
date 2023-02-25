import cv2
from info import info
import pytesseract
import os

# Set the path to the Tesseract executable (optional)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Set the input file path
input_file = "IKK Gesundheitskarte1024_1.jpg"

# Load the input image
img = cv2.imread(input_file)

# Rotate the image in all four directions and save each rotation to a file
for angle in [0, 90, 180, 270]:
  # Rotate the image
  img = cv2.imread(input_file)
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

# Combine the output text from all rotations into a single file
combined_text = f"{input_file}\n"
combined_text += "========================================================\n"
for angle in [0, 90, 180, 270]:
  output_file = f"output_{angle}.txt"
  with open(output_file, "r") as f:
    text = f.read()
    combined_text += text

# Generate the output file name for the combined text
output_file = "combined_output.txt"

# Write the combined output text to a file
with open(output_file, "w") as f:
  f.write(combined_text)

# Clean up the temporary output files
for angle in [0, 90, 180, 270]:
  output_file = f"output_{angle}.txt"
  os.remove(output_file)
