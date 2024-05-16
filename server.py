from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from solution import *
from io import BytesIO
from parameter_table_parser import parameter_table_parser
from table_data import *

app = Flask(__name__)
CORS(app)

# @app.route('/get_cleaned', methods=['POST', 'GET'])
# def get_cleaned():
#     if 'file' not in request.files:
#         return 'No file part', 400

#     file = request.files['file']
#     choices = request.form.get('parameterTableChoices')
#     choices = json.loads(choices)
#     mode = request.form.get('mode')

#     if file.filename == '':
#         return 'No selected file', 400

#     parameterTableOutput = parameter_table_parser(choices, mode)
    
#     cleaned_df, _ = get_data(mode, parameterTableOutput, file)

#     excel_file_path = 'cleaned.xlsx'
#     with pd.ExcelWriter(excel_file_path) as writer:
#         cleaned_df.to_excel(writer, index=False, sheet_name="cleaned data")

#     return send_file(excel_file_path, as_attachment=True)

@app.route('/api/clean_raw', methods=['POST', 'GET'])
def clean_raw():
    if 'file' not in request.files:
        return 'No file part', 401

    file = request.files['file']
    mapping = request.form.get('mapping')
    
    mapping = json.loads(mapping)

    if file.filename == '':
        return 'No selected file', 402
    
    print(mapping)
    
    tempDF = pd.read_excel(file, header=1)
    print(len(tempDF))
    
    cleanedData = clean_data(file, social_credit_score_list=[3]*len(tempDF), original_to_new_mapping=mapping, time_columns=[
        "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",
        "3-4 PM", "4-5 PM", "5-6 PM"],
    days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    priority_list=["No"]*len(tempDF))
    
    print("Cleaned DF:")
    print(cleanedData)
    return cleanedData.to_json(orient = "records")
    #return jsonify(cleanedData.to_dict())

@app.route('/api/get_solution', methods=['POST', 'GET'])
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

    _, (student_workers, x_ijk, l_jk, u_jk, social_credit_score_list, priority_list) = get_data(mode, parameterTableOutput, file)
    solution, analytics_df = compute_solution(student_workers, x_ijk, l_jk, u_jk)

    excel_file_path = 'solution.xlsx'
    with pd.ExcelWriter(excel_file_path) as writer:
        solution.to_excel(writer, sheet_name="output solution") #index not false to show the time columns
        analytics_df.to_excel(writer, sheet_name="model analytics", index=False)
    return send_file(excel_file_path, as_attachment=True)


@app.route('/api/populate_table', methods=['POST'])
def populate_table():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    fileType = request.form.get("filetype")
    print(fileType)

    if file.filename == '':
        return 'No selected file', 400

    if fileType == "raw":
        df = pd.read_excel(file, header=1)
        columns = get_column_names(df, fileType)
        return jsonify({"columns": columns})

    elif fileType == "clean":
        df = pd.read_excel(file)
        newDf = get_column_names(df, fileType)
        return newDf.to_json()

    print(columns)
    # except:
    #     return 'Incorrect File', 401

    
if __name__ == '__main__':
    app.run(debug=True)