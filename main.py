# -*- coding: utf-8 -*-
from flask import Flask, jsonify, send_from_directory, request

from boleto import BoletoFile
# from werkzeug import secure_filename

from paymentsSheet import PaymentSheet
import pathlib


CURRENT_PATH = pathlib.Path().resolve()

UPLOAD_FOLDER = CURRENT_PATH

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