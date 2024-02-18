from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from solution import *
from io import BytesIO
from parameter_table_parser import parameter_table_parser

app = Flask(__name__)
CORS(app)

@app.route('/get_cleaned', methods=['POST', 'GET'])
def get_cleaned():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    choices = request.form.get('parameterTableChoices')
    choices = json.loads(choices)
    
    if file.filename == '':
        return 'No selected file', 400

    parameterTableOutput = parameter_table_parser(choices)

    cleaned_df, _ = get_data("Qualtrics", parameterTableOutput, file)
    #solution = compute_solution(student_workers_q, x_ijk_q, l_ijk_q, u_ijk_q)
    
    excel_file_path = 'final_cleaned_and_converted.xlsx'
    cleaned_df.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)


@app.route('/get_solution', methods=['POST', 'GET'])
def get_solution():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400


    cleaned_df, (student_workers_q, x_ijk_q, l_ijk_q, u_ijk_q) = get_data("Qualtrics", file)
    solution = compute_solution(student_workers_q, x_ijk_q, l_ijk_q, u_ijk_q)
    
    excel_file_path = 'output.xlsx'
    solution.to_excel(excel_file_path, index=False)
    return send_file(excel_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)