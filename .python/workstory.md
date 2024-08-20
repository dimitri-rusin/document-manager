



Check which languages we have
```sh
tesseract --list-langs
```

Which codes stand for which languages:
```sh
https://github.com/tesseract-ocr/tessdoc/blob/main/Data-Files-in-different-versions.md
```

How to add another language:
```sh
wget https://github.com/tesseract-ocr/tessdata_best/raw/main/fra.traineddata
sudo mv fra.traineddata /usr/share/tesseract-ocr/5/tessdata/
```

Dangerous, tesseract is NOT packaged with Anaconda3:
```
> which tesseract
  /usr/bin/tesseract
```

Fixable (durch stumpfe Wiederholung) Fehler:
```
Done.
Making searchable: 2024-08-12 21-30 1.pdf
Traceback (most recent call last):
  File "/home/dimitri/code/DocumentManager/src/details.py", line 90, in <module>
    with wand.image.Image(filename=pdf_path, resolution=300) as pdf:
  File "/home/dimitri/code/DocumentManager/.deploy/conda_environment/lib/python3.9/site-packages/wand/image.py", line 9382, in __init__
    self.read(filename=filename)
  File "/home/dimitri/code/DocumentManager/.deploy/conda_environment/lib/python3.9/site-packages/wand/image.py", line 10142, in read
    raise WandRuntimeError(msg)
wand.exceptions.WandRuntimeError: MagickReadImage returns false, but did not raise ImageMagick  exception. This can occur when a delegate is missing, or returns EXIT_SUCCESS without generating a raster.
```
