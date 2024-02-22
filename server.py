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

    cleaned_df, (student_workers_q, x_ijk_q, l_ijk_q, u_ijk_q, social_credit_score_list, priority_list) = get_data("Qualtrics", parameterTableOutput, file)
    solution = compute_solution(student_workers_q, x_ijk_q, l_ijk_q, u_ijk_q)
    print("solution df", solution)

    excel_file_path = 'solution_and_cleaned_data.xlsx'
    with pd.ExcelWriter(excel_file_path) as writer:
        solution.to_excel(writer, index=False, sheet_name="output solution")
        cleaned_df.to_excel(writer, index=False, sheet_name="cleaned data")

    return send_file(excel_file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)