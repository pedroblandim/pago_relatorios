# -*- coding: utf-8 -*-
import logging
import os
from flask import Flask, jsonify, send_from_directory, request
import pytesseract as ocr
import pathlib

from paymentsSheet import PaymentSheet
from boleto import read_boletos
from whatsappPix import WhatsappPix


if 'ON_HEROKU' not in os.environ and os.name == 'nt': # not in Heroku and OS is windows
    ocr.pytesseract.tesseract_cmd = os.environ.get(
        'PYTESSERACT_CMD_PATH')

CURRENT_PATH = pathlib.Path().resolve()

SHEET_NAME = "Relatório de Pagamentos.xlsx"

app = Flask(__name__)


@app.post("/")
def create_payment_sheet():
    payment_sheet = PaymentSheet(request)
    payment_sheet.create_sheet(CURRENT_PATH, SHEET_NAME)
    return send_from_directory(CURRENT_PATH, SHEET_NAME, as_attachment=True)


@app.route('/read-boletos-numbers', methods=['POST'])
def read_boletos_numbers():
    if request.method == 'POST':
        files = request.files.getlist('boletos')

        boletos = read_boletos(files)

        boletos_json_list = [
            {
                "fileName": boleto.getFilename(),
                'number': boleto.getFormattedNumber(),
                'amount': boleto.getAmount()
            }
            for boleto in boletos]

        return jsonify({"boletos": boletos_json_list})

@app.route('/read-whatsapp-pix', methods=['POST'])
def read_whatsapp_pix():
    if request.method == 'POST':
        pix_images = request.files.getlist('pix')

        whatsapp_pix_list = []

        for image in pix_images:
            whatsapp_pix = WhatsappPix(image)

            if whatsapp_pix:
                whatsapp_pix_list.append(whatsapp_pix)


        whatsapp_pix_json_list = [
            {
                'fileName': whatsapp_pix.get_filename(),
                'name': whatsapp_pix.get_name(),
                'pix_key': whatsapp_pix.get_pix_key(),
                'value': whatsapp_pix.get_value(),
            }
            for whatsapp_pix in whatsapp_pix_list]

        return jsonify({"pix_infos": whatsapp_pix_json_list})


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.warn')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
