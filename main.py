# -*- coding: utf-8 -*-
from flask import Flask, jsonify, send_from_directory, flash, request, redirect

import mimetypes
from BoletoFile import BoletoFile
# from werkzeug import secure_filename

from PaymentSheet import PaymentSheet
import pathlib


CURRENT_PATH = pathlib.Path().resolve()

ALLOWED_EXTENSIONS = {'pdf', 'jpeg', 'png', 'gif', 'bmp', 'tiff'}
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
            if file.filename == '' or not allowed_file(file.filename):
                continue

            boleto = BoletoFile(file)
            boletos_numbers[boleto.file_name] = boleto.number
        

        return jsonify(boletos_numbers)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS