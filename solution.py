##Takes in the data from the appropriate parser and generates the optimal solution

from Excel_Parser import *
from Qualtrics_Parser import *
from pulp import *
#from gurobipy import *

def get_data(mode, file_path=""):
    #mode is either Excel or Qualtrics
    if (mode == "Excel"):
        ep = Excel_Parser(file_path)
        student_workers, x_ijk = ep.get_all_data()
        i, j, k = x_ijk.shape
        l_ijk = np.full((i, j, k), 2)
        u_ijk = np.full((i, j, k), 5)
    
        #Friday 2pm-6pm unavailable so change l_ijk and u_ijk to 0 for those
        l_ijk[:, 4, 4:] = 0
        u_ijk[:, 4, 4:] = 0
        
        return (student_workers, x_ijk, l_ijk, u_ijk)
    
    if (mode == "Qualtrics"):
        ...
        
def compute_solution(student_workers, x_ijk, l_ijk, u_ijk):
    ## student_workers is an NumPy Array with shape (n, 5), where n is the number of student workers
    # column 1 is the index in the table corresponding to that worker: int in range [0, n)
    # column 2 is the name of the worker: str
    # column 3 is the type of the workers (PLA/GLA/TA): str
    # column 4 is the number of hours that the worker wants to work (the default is 1 for PLAs and 2 for GLAs/TAs unless additional hours were specified)
    # column 5 is their shift preference for the workers (NaN if 1 hour, Back-To-Back, Same-Day): str
    
    ## x_ijk is a NumPy array with shape (n, d, s), where n is the number of student workers, d is the number of days, and s is the number of shifts
    # Each element represents worker i's preference for working in day j shift k (X, 1, 2, 3), where X indicates that they are unavailable, and is a large number (in this case it is set to 10000)
    # 1, 2, and 3 are in order of most preferable to least preferable: int
    
    ## l_ijk, u_ijk are NumPy arrays with shape (d, s)
    # l_ijk is the minimum number of student workers required on day j shift k: int
    # u_ijk is the maximum number of student workers required on day j shift k: int
    
    scheduler_model = LpProblem("MTC Scheduler", LpMinimize)

    PLAs = student_workers[np.where(student_workers[:, 2] == "PLA")]
    GLAs = student_workers[np.where(student_workers[:, 2] == "GLA")]
    TAs = student_workers[np.where(student_workers[:, 2] == "TA")]
    
    print(PLAs)
    print(GLAs)
    print(TAs)
    
    ## Workers who prefer Back-To-Back Shifts ##
    # Back_To_Back_Workers = student_workers[np.where(student_workers[:, 4] == "Back-To-Back")]
    # Same_Day_Workers = student_workers[np.where(student_workers[:, 4] == "Same-Day")]
    
    ### Initialize Decision Variables ###
    a_ijk = {}
    varsKey = {}
    for i in range(x_ijk.shape[0]):
        for j in range(x_ijk.shape[1]):
            for k in range(x_ijk.shape[2]):
                a_ijk[(i, j, k)] = LpVariable(name=f"a({i},{j},{k})", lowBound=0, upBound=1, cat=LpBinary)
                varsKey[f"a({i},{j},{k})"] = (i, j, k)
    
        
    ### Objective Function ###
    scheduler_model += lpSum([x_ijk[i, j, k]*a_ijk[i, j, k]
                                for i in student_workers[:, 0]
                                for j in range(x_ijk.shape[1])
                                for k in range(x_ijk.shape[2])])
    
    ### Constraints ###

    ## PLAs work one shift ##
    for i in PLAs[:, 0]:
        scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                    for j in range(x_ijk.shape[1])
                    for k in range(x_ijk.shape[2])]) == 1 # Change from 1 to the worker's preferred number of hours (student_workers[i, 3])
            )
    
    ## GLAs and TAs work two shifts ##
    
    for i in np.vstack((GLAs, TAs))[:, 0]:
        scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                        for j in range(x_ijk.shape[1])
                        for k in range(x_ijk.shape[2])]) == 2 # Change from 2 to the worker's preferred number of hours (student_workers[i, 3])
            )
    
    ## Set lower and upper bound on number of workers for each shift ##
    
    for j in range(x_ijk.shape[1]):
        for k in range(x_ijk.shape[2]):
            scheduler_model += (
                    lpSum([a_ijk[i, j, k] 
                        for i in student_workers[:, 0]]) >= l_ijk[i, j, k]
            )
            
    for j in range(x_ijk.shape[1]):
        for k in range(x_ijk.shape[2]):
            scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                        for i in student_workers[:, 0]]) <= u_ijk[i, j, k]
            )
    
    ## Handle Back-To-Back Shifts ##
    """
    for i in Back_To_Back_Workers[:, 0]:
            scheduler_model += (
                    lpSum(np.to_binary([a_ijk[i, j, :]) & (np.to_binary(a_ij) >> 1) for j in x_ijk.shape[1]]) > 0)
        
    """
    #np.to_binary is not a real function, I am just using it as a placeholder for some function that converts the vector a_ijk[i, j, :] to a binary vector
    
    
    ## Handle Same-Day Shifts ##
    """for i in Same_Day_Workers[:, 0]:
                scheduler_model += (
                        lpSum( for j in x_ijk.shape[1]]) > 0)
    """

    scheduler_model.solve()
    num_j = x_ijk.shape[1]
    num_k = x_ijk.shape[2]
    result_array = [[[] for _ in range(num_k)] for _ in range(num_j)]

    for v in scheduler_model.variables():
        if v.varValue is not None and v.varValue > 1e-6:
            i, j, k = varsKey[v.name]
            worker_name = student_workers[np.where(student_workers[:, 0] == i)][0, 1]
            #result_array[j][k].append(worker_name)
            result_array[j][k].append(i)
        
    return result_array

if __name__=="__main__":
    student_workers, x_ijk, l_ijk, u_ijk = get_data("Excel", "MTC Availability Template.xlsx")
    solution = compute_solution(student_workers, x_ijk, l_ijk, u_ijk)
    print(solution)