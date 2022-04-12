import mimetypes
import re
from tika import parser
from werkzeug.utils import secure_filename


class BoletoFile():
    PATTERN = '[0-9]{5}.[0-9]{5} [0-9]{5}.[0-9]{6} [0-9]{5}.[0-9]{6} [0-9] [0-9]{14}'

    def __init__(self, file):
        self.file_name = secure_filename(file.filename)

        if mimetypes.types_map['.pdf'] == file.mimetype:
            raw = parser.from_buffer(file)
            text = raw['content']
            print(text)
            pass
        else:
            # text = read_image(file)
            pass

        self.number = self.__extract_boleto_number(text)
    
    def __extract_boleto_number(self, text):
        return re.search(BoletoFile.PATTERN, text)[0]