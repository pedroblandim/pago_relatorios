from openpyxl import Workbook
from datetime import date
from openpyxl.styles import Font, PatternFill
import json
from urllib.request import urlopen


def create_xlsx():
    return Workbook()

def set_format_xlsx(workbook, nome_empresa):
    data_atual = date.today()
    font_style_title = Font(bold=True)
    font_style = Font(bold=True, color="FFFFFF")
    fill_pattern = PatternFill(patternType='solid', fgColor="45818D")

    planilha = workbook.worksheets[0]

    planilha.title = 'Relatório de Pagamentos'

    planilha['a1'] = nome_empresa.upper()
    planilha['b1'] = data_atual.strftime('%d/%m/%Y')
    planilha['a1'].font = planilha['b1'].font = font_style_title

    planilha['a3'] = 'NOME'
    planilha['b3'] = 'VALOR'
    planilha['c3'] = 'TIPO'
    planilha['a3'].font = planilha['b3'].font = planilha['c3'].font = font_style
    planilha['a3'].fill = planilha['b3'].fill =planilha['c3'].fill = fill_pattern

    return planilha

def add_values_xlsx(planilha, data):
    starting_row = 4
    for item in data:
        planilha.cell(row=starting_row, column=1).value = item['name']
        planilha.cell(row=starting_row, column=2).value = item['value']
        planilha.cell(row=starting_row, column=3).value = item['type']
        starting_row+=1
    return planilha

def soma_total(planilha, data):
    soma_valor = 0
    starting_row = 4
    for item in data:
        soma_valor += item['value']
        starting_row += 1
    planilha.cell(row = starting_row + 1, column=1).value = 'Total'
    planilha.cell(row = starting_row + 1, column=2).value = soma_valor
    return planilha

def main():
    url = "http://localhost:3000/Pagamentos"
    json_data = urlopen(url)

    data = json.loads(json_data.read())


    workbook = create_xlsx()
    planilha = set_format_xlsx(workbook, 'Pagô')

    add_values_xlsx(planilha, data)
    soma_total(planilha,data)

    workbook.save('/Users/piemonte/Desktop/Programas/pythonProject/testeRelatorio.xlsx')

if __name__ == '__main__':
    main()




