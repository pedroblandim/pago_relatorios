

import logging
import re

from fileReader import read_image, remove_temp_file, save_temp_file


log = logging.getLogger('whatsapp-pix')

class WhatsappPix:

    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff'}

    REGEX_PATTERNS = {
        'name': r'[\n]?Nome[: ]+ ([\w ]+)[\n]?\b',
        'pix_key': r'[\n]?Pix[.: ]+ ([\d.-]+)[\n]?\b',
        'value': r'[\n]?Valor[:]? [R]?[$]?[ ]?([\d.,]+)[\n]?\b',
    }

    def __init__(self, file):
        if not WhatsappPix.allowed_file(file.filename):
            log.warning(
                'File with mimetype not allowed: ' + file.filename)
            return None
        
        self.filename = file.filename

        name, pix_key, value = WhatsappPix.__get_pix_infos(file)
        self.name = name
        self.pix_key = pix_key
        self.value = value

    @staticmethod
    def __get_pix_infos(file):

        filename = ""
        try:
            filename = save_temp_file(file)
            
            text = read_image(filename, False)

            name, pix_key, value = WhatsappPix.__extract_pix_infos(text)

            if not name or not pix_key or not value:
                text = read_image(filename, True)
                name, pix_key, value = WhatsappPix.__extract_pix_infos(text)

            return name, pix_key, value
        finally:
            if filename:
                remove_temp_file(filename)

    @staticmethod
    def __extract_pix_infos(text):
        name = ''
        pix_key = ''
        value = ''
        
        name = WhatsappPix.__match(WhatsappPix.REGEX_PATTERNS['name'], text, name)
        pix_key = WhatsappPix.__match(WhatsappPix.REGEX_PATTERNS['pix_key'], text, pix_key)
        value = WhatsappPix.__match(WhatsappPix.REGEX_PATTERNS['value'], text, value)

        return name, pix_key, value

    @staticmethod
    def __match(pattern, text, default):
        matchs = re.search(pattern, text, re.IGNORECASE)
        if matchs and matchs.groups():
            return matchs.group(1)
        
        return default

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in WhatsappPix.ALLOWED_EXTENSIONS

    def get_filename(self):
        return self.filename

    def get_name(self):
        return self.name

    def get_pix_key(self):
        return ''.join(filter(str.isdigit, self.pix_key))

    def get_value(self):
        return 'R$ ' + self.value
