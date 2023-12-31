from flask import Flask, request, jsonify
from flask_cors import CORS
from solution import *

app = Flask(__name__)
CORS(app)

#Get optimal schedule to be displayed on React client-side
@app.route('/api/display_solution', methods=['GET'])
def display_solution():
    student_workers, x_ijk, l_ijk, u_ijk = get_data("Excel", "MTC Availability Template.xlsx")
    solution = compute_solution(student_workers, x_ijk, l_ijk, u_ijk)
    data = {"solution": solution}
    return jsonify(data)
if __name__ == '__main__':
    app.run()
