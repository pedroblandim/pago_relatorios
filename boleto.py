import logging
import mimetypes
import re
from functools import reduce

from werkzeug.datastructures import FileStorage

from PyPDF2 import PdfFileWriter, PdfFileReader

from fileReader import get_temp_file_path, read_pdf_file, read_image, pdf_to_temp_image, save_temp_file, remove_temp_file

log = logging.getLogger('boleto')


def read_boletos(files):

    files_split = [__split_pdf_file(file) for file in files]

    # reduce list of lists to a list (same as flatmap)
    files = reduce(list.__add__, files_split)

    boletos = []

    for file in files:
        if not BoletoFile.allowed_file(file.filename):
            log.warning(
                'File with mimetype not allowed: ' + file.filename)
            continue

        boleto = BoletoFile(file)

        if not boleto.number:
            log.warning(
                'Could not read number from boleto: ' + file.filename)

        boletos.append(boleto)

    return boletos


def __split_pdf_file(file):
    # create one PDF per page

    if not mimetypes.types_map['.pdf'] == file.mimetype:
        return [file]

    inputpdf = PdfFileReader(file.stream)

    files = []

    for i in range(inputpdf.numPages):
        page_file_output = PdfFileWriter()
        page_file_output.insertPage(inputpdf.getPage(i))

        temp_file_path, temp_filename = get_temp_file_path(
            str(i) + file.filename)

        # write current page to temp file
        with open(temp_file_path, "wb") as output_stream:
            page_file_output.write(output_stream)

        # instantiate FileStorage with current page temp file
        with open(temp_file_path, "rb") as current_page_temp_output:
            new_filename = file.filename.split(
                '.', 1)[0] + ' Page ' + str(i + 1) + '.' + file.filename.split('.', 1)[1]
            new_file_path, new_filename = get_temp_file_path(new_filename)

            new_file = FileStorage(
                current_page_temp_output, new_filename, None, file.content_type, file.content_length, file.headers)

            new_file.save(new_file_path)
            files.append(new_file)

        # remove current page temp file
        remove_temp_file(temp_filename)

    return files


class BoletoFile():
    """Reads boleto from a PDF or image and then extract its number"""

    #                   xxxxx . xxxxx           xxxxx  . xxxxxx           xxxxx . xxxxx        xxxxxxxxx xxxxxxxxxxxxxx
    NUMBER_PATTERN = '[0-9]{5}.[0-9]{5}[ .]{1,6}[0-9]{5}.[0-9]{6}[ .]{1,6}[0-9]{5}.[0-9]{6}[ .]{1,6}[0-9][ .]{1,6}[0-9]{14}'
    SIMPLIFIED_NUMBER_PATTERN = '[0-9]{47}'

    ALLOWED_EXTENSIONS = {'pdf', 'jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff'}

    def __init__(self, file):
        self.filename = file.filename

        number = BoletoFile.__read_boleto_file_number(file)

        if BoletoFile.__validate_number(number):
            self.number = number
        else:
            self.number = ""

    @staticmethod
    def __read_boleto_file_number(file):
        number = ""

        filename = ""
        try:
            filename = save_temp_file(file)

            if mimetypes.types_map['.pdf'] == file.mimetype:
                # try to read PDF file
                text = read_pdf_file(filename)
                number = BoletoFile.__extract_boleto_number(text)

                if number:
                    return number
                else:
                    # transform PDF in image and replace current filename
                    image_filename = pdf_to_temp_image(file)

                    remove_temp_file(filename)

                    filename = image_filename

                if not image_filename:
                    return ""

            # read image with current filename
            text = read_image(filename, False)

            number = BoletoFile.__extract_boleto_number(text)

            if not number:
                text = read_image(filename, True)
                number = BoletoFile.__extract_boleto_number(text)

            return number
        finally:
            if filename:
                remove_temp_file(filename)

    @staticmethod
    def __extract_boleto_number(text):
        numbers = re.search(BoletoFile.NUMBER_PATTERN, text)
        if not numbers:
            numbers = re.search(BoletoFile.SIMPLIFIED_NUMBER_PATTERN, text)

        if numbers:
            number = numbers[0]
            return re.sub('[^\d]', '', number)

        else:
            return ""

    @staticmethod
    def __validate_number(number):
        if len(number) != 47:
            return False

        # TODO validate with modulo11
        return True

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in BoletoFile.ALLOWED_EXTENSIONS

    def getFormattedNumber(self):
        if not self.number:
            return ""

        formattedNumber = self.number
        formattedNumber = '{}.{} {}.{} {}.{} {} {}'.format(
            formattedNumber[:5], formattedNumber[5:
                                                 10], formattedNumber[10:15], formattedNumber[15:21],
            formattedNumber[21:26], formattedNumber[26:32], formattedNumber[32:33], formattedNumber[33:47])

        return formattedNumber

    def getFilename(self):
        return self.filename

    def getAmount(self):
        if not self.number:
            return ''

        return BoletoFile.__toCurrency(int(self.number[-10:]) / 100)

    @staticmethod
    def __toCurrency(number):
        a = '{:,.2f}'.format(float(number))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        return "R$ " + c.replace('v', '.')
