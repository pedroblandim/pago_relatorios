import locale
import mimetypes
import re
from tika import parser
from werkzeug.utils import secure_filename

from ocr import read_image

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class BoletoFile():
    """Reads boleto from a PDF or image and then extract its number"""
    
    #                   xxxxx . xxxxx           xxxxx  . xxxxxx           xxxxx . xxxxx        xxxxxxxxx xxxxxxxxxxxxxx
    NUMBER_PATTERN = '[0-9]{5}.[0-9]{5}[ ]{1,6}[0-9]{5}.[0-9]{6}[ ]{1,6}[0-9]{5}.[0-9]{6}[ ]{1,6}[0-9][ ]{1,6}[0-9]{14}'
    SIMPLIFIED_NUMBER_PATTERN = '[0-9]{47}'

    ALLOWED_EXTENSIONS = { 'pdf', 'jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff' }

    def __init__(self, file):
        self.filename = secure_filename(file.filename)

        if mimetypes.types_map['.pdf'] == file.mimetype:
            text = BoletoFile.__read_pdf_file(file)
        else:
            text = BoletoFile.__read_image_file(file)

        self.number = BoletoFile.__extract_boleto_number(text)

    @staticmethod
    def __read_pdf_file(file):
        raw = parser.from_buffer(file)
        return raw['content']

    @staticmethod
    def __read_image_file(file):
        return read_image(file)

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
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in BoletoFile.ALLOWED_EXTENSIONS

    def getFormattedNumber(self):
        if not self.number:
            return ""
            
        formattedNumber = self.number 
        formattedNumber= '{}.{} {}.{} {}.{} {} {}'.format(
            formattedNumber[:5], formattedNumber[5:10], formattedNumber[10:15], formattedNumber[15:21], 
            formattedNumber[21:26], formattedNumber[26:32], formattedNumber[32:33], formattedNumber[33:47])
        
        return formattedNumber

    def getFilename(self):
        return self.filename

    def getAmount(self):
        if not self.number:
            return ''

        return locale.currency(int(self.number[-10:]) / 100)
        