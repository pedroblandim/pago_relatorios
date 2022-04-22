

import logging


log = logging.getLogger('whatsapp-pix')

class WhatsappPix:

    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff'}

    def __init__(self, file):
        if not WhatsappPix.allowed_file(file.filename):
            log.warning(
                'File with mimetype not allowed: ' + file.filename)
            return None
        
        self.filename = file.filename

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in WhatsappPix.ALLOWED_EXTENSIONS

    def getFilename(self):
        return self.filename