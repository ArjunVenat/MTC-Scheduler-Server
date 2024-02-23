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
    mode = request.form.get('mode')

    if file.filename == '':
        return 'No selected file', 400

    parameterTableOutput = parameter_table_parser(choices, mode)
    
    cleaned_df, _ = get_data(mode, parameterTableOutput, file)

    excel_file_path = 'cleaned.xlsx'
    with pd.ExcelWriter(excel_file_path) as writer:
        cleaned_df.to_excel(writer, index=False, sheet_name="cleaned data")

    return send_file(excel_file_path, as_attachment=True)


@app.route('/get_solution', methods=['POST', 'GET'])
def get_solution():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    choices = request.form.get('parameterTableChoices')
    choices = json.loads(choices)
    mode = request.form.get('mode')
    print("mode = ", mode)

    if file.filename == '':
        return 'No selected file', 400

    parameterTableOutput = parameter_table_parser(choices, mode)

    _, (student_workers, x_ijk, l_ijk, u_ijk, social_credit_score_list, priority_list) = get_data(mode, parameterTableOutput, file)
    solution, analytics_df = compute_solution(student_workers, x_ijk, l_ijk, u_ijk)

    excel_file_path = 'solution.xlsx'
    with pd.ExcelWriter(excel_file_path) as writer:
        solution.to_excel(writer, sheet_name="output solution") #index not false to show the time columns
        analytics_df.to_excel(writer, sheet_name="model analytics")
    return send_file(excel_file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)