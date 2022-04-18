import io
import logging
import pytesseract as ocr
import numpy as np
import cv2
import fitz
import os
import pathlib
from werkzeug.utils import secure_filename

from PIL import Image


TEMP_FOLDER = os.path.join(pathlib.Path().resolve(), "temp")
log = logging.getLogger('fileReader')


def read_image(filename, treatImage):

    file_path = get_temp_file_path(filename)[0]

    # tipando a leitura para os canais de ordem RGB
    image = Image.open(file_path).convert('RGB')

    # convertendo em um array editável de numpy[x, y, CANALS]
    img = np.asarray(image).astype(np.uint8)

    if not treatImage:
        return ocr.image_to_string(img)

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(
        gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

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


def read_pdf_file(filename):
    file_path = get_temp_file_path(filename)[0]
    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    return text


def pdf_to_temp_image(file):
    file_path, filename = get_temp_file_path(file.filename)

    image_format = 'tiff'
    image_filename = filename.split('.')[0] + '.' + image_format

    zoom = 2  # to increase the resolution
    mat = fitz.Matrix(zoom, zoom)
    image_list = []
    with fitz.open(file_path) as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=mat)

            image = Image.open(io.BytesIO(pix.pil_tobytes(image_format)))

            image_list.append(image)

        image_file_path = os.path.join(TEMP_FOLDER, image_filename)
        if image_list:
            image_list[0].save(
                image_file_path,
                save_all=True,
                append_images=image_list[1:],
                dpi=(300, 300),
            )

        return image_filename


def save_temp_file(file):
    file_path, filename = get_temp_file_path(file.filename)

    if not os.path.exists(file_path):
        file.save(file_path)

    return filename


def remove_temp_file(filename):
    file_path = get_temp_file_path(filename)[0]
    try:
        os.remove(file_path)
    except Exception as error:
        log.error("Error removing boleto temp file: %s", error)


def get_temp_file_path(filename):
    secure = secure_filename(filename)
    return [os.path.join(TEMP_FOLDER, secure), secure]
