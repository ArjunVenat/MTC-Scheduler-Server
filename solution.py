##Takes in the data from the appropriate parser and generates the optimal solution

from Excel_Parser import *
from Qualtrics_Parser import *
from pulp import *
#from gurobipy import *

def get_data():
    ...
    
def compute_solution():
    scheduler_model = LpProblem("MTC Scheduler", LpMinimize)
    ep = Excel_Parser("MTC Availability Template.xlsx")
    student_workers, x_ijk = ep.get_all_data()
    i, j, k = x_ijk.shape
    
    l_ijk = np.full((i, j, k), 2)
    u_ijk = np.full((i, j, k), 5)
    
    #Friday 2pm-6pm unavailable so change l_ijk and u_ijk to 0 for those
    l_ijk[:, 4, 4:] = 0
    u_ijk[:, 4, 4:] = 0
    

    PLAs = student_workers[np.where(student_workers[:, 2] == "PLA")]
    GLAs = student_workers[np.where(student_workers[:, 2] == "GLA")]
    TAs = student_workers[np.where(student_workers[:, 2] == "TA")]
    
    print(PLAs)
    print(GLAs)
    print(TAs)
    
    
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
                    for k in range(x_ijk.shape[2])]) == 1 
            )
    
    ## GLAs and TAs work two shifts ##
    
    for i in np.vstack((GLAs, TAs))[:, 0]:
        scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                        for j in range(x_ijk.shape[1])
                        for k in range(x_ijk.shape[2])]) == 2 
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
    
    scheduler_model.solve()
    print(LpStatus[scheduler_model.status])
    print(scheduler_model.objective.value())
    
    toReturn = [v for v in scheduler_model.variables() if all((v.varValue is not None, v.varValue > 1e-6))]
    print(toReturn)

compute_solution()    
