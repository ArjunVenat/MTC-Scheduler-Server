from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from solution import *
from io import BytesIO
from frontend_parameter_parsers import *
from table_data import *

app = Flask(__name__)
CORS(app)

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

@app.route('/api/clean_raw', methods=['POST'])
def clean_raw():
    if 'file' not in request.files:
        return 'No file part', 401
    
    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 402

    mapping = json.loads(request.form.get('mapping'))
    parsedMapping = {}
    for row in mapping:
        parsedMapping[row["questionText"]] = row["desiredCol"]

    numWorkers = len(pd.read_excel(file, header=1))
    cleanedData = clean_data(file, social_credit_score_list=[3]*numWorkers, priority_list=["No"]*numWorkers, header=1, original_to_new_mapping=parsedMapping)
    
    excel_file_path = 'cleaned.xlsx'
    with pd.ExcelWriter(excel_file_path) as writer:
        cleanedData.to_excel(writer, index=False, sheet_name="cleaned data")
    
    return send_file(excel_file_path, as_attachment=True)

@app.route('/api/feasibility_check', methods=['POST'])
def feasibility_check():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    hoursTable = json.loads(request.form.get('hoursTable'))
    dayRange = json.loads(request.form.get('dayRange'))
    timeRange = json.loads(request.form.get('timeRange'))
    dayRange, timeRange, indices = fix_day_time(dayRange, timeRange)

    df = pd.read_excel(file)

    hoursMap = {"PLA": 1, "TA": 2, "Grader/ Tutor": 1}
    maxWorkerHours = df["Max-hours"].sum()
    minWorkerHours = df["Position"].apply(lambda x: hoursMap[x]).sum()

    l_jk, u_jk = hours_table_parser(hoursTable, dayRange, timeRange, indices=indices)
    
    lowerBound = np.sum(l_jk)
    upperBound = np.sum(u_jk)

    # print(maxWorkerHours, minWorkerHours)
    # print(lowerBound, upperBound)

    message = "Success, please wait for solution file to download"
    statusFlag = False
    if (upperBound < minWorkerHours):
        message = f"Not all workers will be assigned a shift, please increase add more workers to shifts"
        statusFlag = True
    if (lowerBound > maxWorkerHours):
        message = f"Not enough worker hours to satisfy minimum workers constraint"
        statusFlag = True

    toReturn = jsonify({'message': message, 'statusFlag': statusFlag})
    return toReturn

@app.route('/api/reclean', methods=['POST'])
def reclean():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    parameterTableOutput = request.form.get('parameterTableOutput')
    parameterTableOutputJSON = json.loads(parameterTableOutput)

    social_credit_score_list = [row.get("creditScore") for row in parameterTableOutputJSON]
    priority_list = [row.get("prioritize") for row in parameterTableOutputJSON]
    print(social_credit_score_list)
    print(priority_list)
    cleanedData = clean_data(file, social_credit_score_list=social_credit_score_list, priority_list=priority_list, header=0, original_to_new_mapping={})
    
    excel_file_path = 'cleaned.xlsx'
    with pd.ExcelWriter(excel_file_path) as writer:
        cleanedData.to_excel(writer, index=False, sheet_name="cleaned data")
    
    return send_file(excel_file_path, as_attachment=True)


@app.route('/api/get_solution', methods=['POST'])
def get_solution():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    parameterTableOutput = request.form.get('parameterTableOutput')
    hoursTable = request.form.get('hoursTable')
    dayRange = request.form.get('dayRange')
    timeRange = request.form.get('timeRange')
    parameterTableOutputJSON = json.loads(parameterTableOutput)
    hoursTableJSON = json.loads(hoursTable)
    dayRangeJSON = json.loads(dayRange)
    timeRangeJSON = json.loads(timeRange)

    social_credit_score_list = [row.get("creditScore") for row in parameterTableOutputJSON]
    priority_list = [row.get("prioritize") for row in parameterTableOutputJSON]

    print(dayRangeJSON, timeRangeJSON)
    print(parameterTableOutputJSON)
    print(hoursTableJSON)
    print(social_credit_score_list)
    print(priority_list)
    
    dayRange, timeRange, indices = fix_day_time(dayRange=dayRangeJSON, timeRange=timeRangeJSON)
    l_jk, u_jk = hours_table_parser(hoursTable=hoursTableJSON, dayRange=dayRange, timeRange=timeRange, indices=indices)
    cleaned, (student_workers, x_ijk, l_jk, u_jk, social_credit_score_list, priority_list) = get_data("Cleaned", parameterTableOutput=(social_credit_score_list, priority_list), file_path=file, l_jk=l_jk, u_jk=u_jk, time_columns=timeRange, days_of_week=dayRange)
    df, analytics_df = compute_solution(student_workers=student_workers, x_ijk=x_ijk, l_jk=l_jk, u_jk=u_jk, days_of_week=dayRange, time_columns=timeRange)
    
    excel_file_path = 'solution.xlsx'
    with pd.ExcelWriter(excel_file_path) as writer:
        df.to_excel(writer, sheet_name="output solution") #index not false to show the time columns
        analytics_df.to_excel(writer, sheet_name="model analytics", index=False)
    return send_file(excel_file_path, as_attachment=True)

    
if __name__ == '__main__':
    app.run()