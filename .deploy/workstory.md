


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
