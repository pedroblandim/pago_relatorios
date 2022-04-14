import logging
import pytesseract as ocr
import numpy as np
import cv2
import fitz
import os
import pathlib
from werkzeug.utils import secure_filename
# from pdf2image import  

from PIL import Image


TEMP_FOLDER = os.path.join(pathlib.Path().resolve(), "temp")
log = logging.getLogger('fileReader')

def read_image(file, treatImage):

    # tipando a leitura para os canais de ordem RGB
    image = Image.open(file).convert('RGB')

    # convertendo em um array editável de numpy[x, y, CANALS]
    img = np.asarray(image).astype(np.uint8)  

    if not treatImage:
        return ocr.image_to_string(img)

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)

    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_NONE)

    # Creating a copy of image
    im2 = img.copy()

    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file

    # cv2.imshow("teste", thresh1)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    text = ""
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]
        
        # Apply OCR on the cropped image
        text += ocr.image_to_string(cropped, lang='por')
        
    return text

def read_pdf_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(TEMP_FOLDER, filename)
    
    file.save(file_path)

    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    try:
        os.remove(file_path)
    except Exception as error:
        log.error("Error removing boleto temp file", error)

    return text

def pdf_to_image(file):
    pass