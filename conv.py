from wand.image import Image

with Image(filename='resources/Steuernummer vom Finanzamt.pdf', resolution=300) as pdf:
  for i, page in enumerate(pdf.sequence):
    with Image(page) as img:
      img.compression_quality = 100
      img.format = 'jpg'
      img.save(filename=f'output_{i+1}.jpg')
