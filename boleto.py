import mimetypes
import re
from werkzeug.utils import secure_filename

from fileReader import read_pdf_file, read_image, pdf_to_image


class BoletoFile():
    """Reads boleto from a PDF or image and then extract its number"""
    
    #                   xxxxx . xxxxx           xxxxx  . xxxxxx           xxxxx . xxxxx        xxxxxxxxx xxxxxxxxxxxxxx
    NUMBER_PATTERN = '[0-9]{5}.[0-9]{5}[ .]{1,6}[0-9]{5}.[0-9]{6}[ .]{1,6}[0-9]{5}.[0-9]{6}[ .]{1,6}[0-9][ .]{1,6}[0-9]{14}'
    SIMPLIFIED_NUMBER_PATTERN = '[0-9]{47}'

    ALLOWED_EXTENSIONS = { 'pdf', 'jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff' }

    def __init__(self, file):
        self.filename = secure_filename(file.filename)

        number = BoletoFile.__read_boleto_file_number(file)
        
        if BoletoFile.__validate_number(number):
            self.number = number
        else:
            self.number = ""
        
    @staticmethod
    def __read_boleto_file_number(file):
        number = ""

        if mimetypes.types_map['.pdf'] == file.mimetype:
            text = read_pdf_file(file)
            number = BoletoFile.__extract_boleto_number(text)
        
            if number:
                return number
            else:
                file = pdf_to_image(file)
            
        text = read_image(file, False)
        number = BoletoFile.__extract_boleto_number(text)

        if not number:
            text = read_image(file, True)
            number = BoletoFile.__extract_boleto_number(text)
        
        return number

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
        formattedNumber= '{}.{} {}.{} {}.{} {} {}'.format(
            formattedNumber[:5], formattedNumber[5:10], formattedNumber[10:15], formattedNumber[15:21], 
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
        b = a.replace(',','v')
        c = b.replace('.',',')
        return "R$ " + c.replace('v','.')
        