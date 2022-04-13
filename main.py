# -*- coding: utf-8 -*-
import logging
import os
from flask import Flask, jsonify, send_from_directory, request
import pytesseract as ocr

from boleto import BoletoFile

from paymentsSheet import PaymentSheet
import pathlib


if 'ON_HEROKU' not in os.environ:
    ocr.pytesseract.tesseract_cmd = os.environ.get('PYTESSERACT_CMD_PATH') # not in Heroku's environment

CURRENT_PATH = pathlib.Path().resolve()

SHEET_NAME = "Relatório de Pagamentos.xlsx"

app = Flask(__name__)


@app.post("/")
def create_payment_sheet():
    payment_sheet = PaymentSheet(request)
    payment_sheet.create_sheet(CURRENT_PATH, SHEET_NAME)
    return send_from_directory(CURRENT_PATH, SHEET_NAME, as_attachment=True)


@app.route('/read-boletos-numbers', methods = ['GET', 'POST'])
def read_boletos_numbers():
    boletos_numbers = {}
    if request.method == 'POST':
        files = request.files.getlist('boletos')
        
        for file in files:
            if not BoletoFile.allowed_file(file.filename):
                app.logger.warning('File with mimetype not allowed: ' + file.filename)
                continue

            boleto = BoletoFile(file)

            if not boleto.number:
                app.logger.warning('Could not read number from boleto: ' + file.filename)

            boletos_numbers[boleto.filename] = {
                'number': boleto.getFormattedNumber(),
                'amount': boleto.getAmount()
            }

        return jsonify({ "boletos": boletos_numbers })

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.warn')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)