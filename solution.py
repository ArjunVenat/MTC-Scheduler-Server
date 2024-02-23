##Takes in the data from the appropriate parser and generates the optimal solution

from Excel_Parser import *
from Qualtrics_Parser import *
from pulp import *
#from gurobipy import *

def get_data(mode, parameterTableOutput, file_path):
    if (mode == "Qualtrics"):
        # If raw Qualtrics input, we have the additional step of cleaning the data

        # Get the social_credit_score_list and priority_list from the parameterTableOutput, which is the result of the parameter_table_parser function
        social_credit_score_list, priority_list = parameterTableOutput
        
        # Pass the file as well as the lists into the cleaning function from Qualtrics_Parser.py, the result is a Pandas dataframe called cleaned
        cleaned = clean_data(input_path=file_path, social_credit_score_list=social_credit_score_list, priority_list=priority_list)

        # Pass in the cleaned dataframe as well as, for consistency, the social_credit_score_list and priority_list        
        student_workers, x_ijk = parse_data(cleaned, social_credit_score_list=social_credit_score_list, priority_list=priority_list)

        # Now set the lower and upper bound for each shift. 
        i, j, k = x_ijk.shape
        l_ijk = np.full((i, j, k), 2)
        u_ijk = np.full((i, j, k), 6)
    
        #Friday 2pm-6pm unavailable so change l_ijk and u_ijk to 0 for those
        # TODO: Read in lower and upper bounds on number of workers from the front end
        l_ijk[:, 4, 4:] = 0
        u_ijk[:, 4, 4:] = 0
        
        return cleaned, (student_workers, x_ijk, l_ijk, u_ijk, social_credit_score_list, priority_list)
    
    if (mode == "Cleaned"):
        # Same as mode == "Qualtrics" but we skip the clean_data part and go straight to parse_data
 
        social_credit_score_list, priority_list = parameterTableOutput

        cleaned = pd.read_excel(file_path)
        student_workers, x_ijk = parse_data(cleaned, social_credit_score_list=social_credit_score_list, priority_list=priority_list)

        i, j, k = x_ijk.shape
        l_ijk = np.full((i, j, k), 2)
        u_ijk = np.full((i, j, k), 6)
    
        #Friday 2pm-6pm unavailable so change l_ijk and u_ijk to 0 for those
        # TODO: Read in lower and upper bounds on number of workers from the front end
        l_ijk[:, 4, 4:] = 0
        u_ijk[:, 4, 4:] = 0
        
        return cleaned, (student_workers, x_ijk, l_ijk, u_ijk, social_credit_score_list, priority_list)
    
def compute_solution(student_workers, x_ijk, l_ijk, u_ijk):
    ## student_workers is an NumPy Array with shape (n, 5), where n is the number of student workers
    # column 1 is the index in the table corresponding to that worker: int in range [0, n)
    # column 2 is the name of the worker: str
    # column 3 is the type of the workers (PLA/GLA/TA): str
    # column 4 is the number of hours that the worker wants to work (the default is 1 for PLAs and 2 for GLAs/TAs unless additional hours were specified): int
    # column 5 is their shift preference for the workers (NaN if 1 hour, Back-To-Back, Same-Day): str
    # column 6 is the list of courses that the worker feels comfortable teaching: str
    # column 7 is their social credit score from 1-5: int
    # column 8 is if they were given preference, which is also reflected by the change in the preference weights(Yes/No): str  

    ## x_ijk is a NumPy array with shape (n, d, s), where n is the number of student workers, d is the number of days, and s is the number of shifts
    # Each element represents worker i's preference for working in day j shift k (X, 1, 2, 3), where X indicates that they are unavailable, and is a large number (in this case it is set to 10000)
    # 1, 2, and 3 are in order of most preferable to least preferable: int
    
    ## l_ijk, u_ijk are NumPy arrays with shape (d, s)
    # l_ijk is the minimum number of student workers required on day j shift k: int
    # u_ijk is the maximum number of student workers required on day j shift k: int
    
    # Note for some code below:
    # np.where(student_workers[:, 0] == i)[0] allows for a one-to-one mapping of the index column to the index of the worker i in x_ijk, l_ijk, u_ijk
    # This is because there may be missing values for whatever reason, such as for intentionally deleting a survey response
    # a_ijk is already accounted for in the indexing because it uses the key (i, j, k) instead of being an array with indices i, j, and k 


    scheduler_model = LpProblem("MTC Scheduler", LpMinimize)


    PLAs = student_workers[np.where(student_workers[:, 2] == "PLA")]
    GLAs = student_workers[np.where(student_workers[:, 2] == "GLA")] # TODO: Change from GLA to Grader/Tutor
    TAs = student_workers[np.where(student_workers[:, 2] == "TA")]
    
    
    ## Workers who prefer Back-To-Back Shifts ##
    # Back_To_Back_Workers = student_workers[np.where(student_workers[:, 4] == "Back-to-back shifts")]
    # Same_Day_Workers = student_workers[np.where(student_workers[:, 4] == "Same-day shifts")]
    
    ### Initialize Decision Variables ###
    a_ijk = {}
    varsKey = {}
    for i in student_workers[:, 0]:
        for j in range(x_ijk.shape[1]):
            for k in range(x_ijk.shape[2]):
                a_ijk[(i, j, k)] = LpVariable(name=f"a({i},{j},{k})", lowBound=0, upBound=1, cat=LpBinary)
                varsKey[f"a({i},{j},{k})"] = (i, j, k)
    
        
    ### Objective Function ###
    scheduler_model += lpSum([x_ijk[np.where(student_workers[:, 0] == i)[0], j, k]*a_ijk[i, j, k]
                                for i in student_workers[:, 0]
                                for j in range(x_ijk.shape[1])
                                for k in range(x_ijk.shape[2])])
    
    ### Constraints ###

    ## PLAs work one shift minimum ##

    for i in PLAs[:, 0]:
        scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                    for j in range(x_ijk.shape[1])
                    for k in range(x_ijk.shape[2])]) >= 1 
            )

    for i in PLAs[:, 0]:
        scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                    for j in range(x_ijk.shape[1])
                    for k in range(x_ijk.shape[2])]) <= student_workers[np.where(student_workers[:, 0] == i)[0], 3]
            )
    

    ## GLAs and TAs work two shifts minimum ##

    for i in np.vstack((GLAs, TAs))[:, 0]:
        scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                        for j in range(x_ijk.shape[1])
                        for k in range(x_ijk.shape[2])]) >= 2
            )
 

    for i in np.vstack((GLAs, TAs))[:, 0]:
        scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                        for j in range(x_ijk.shape[1])
                        for k in range(x_ijk.shape[2])]) <= student_workers[np.where(student_workers[:, 0] == i)[0], 3]
            )
        
    
    ## Set lower and upper bound on number of workers for each shift ##
    
    for j in range(x_ijk.shape[1]):
        for k in range(x_ijk.shape[2]):
            scheduler_model += (
                    lpSum([a_ijk[i, j, k] 
                        for i in student_workers[:, 0]]) >= l_ijk[np.where(student_workers[:, 0] == i)[0], j, k]
            )
            
    for j in range(x_ijk.shape[1]):
        for k in range(x_ijk.shape[2]):
            scheduler_model += (
                    lpSum([a_ijk[i, j, k]
                        for i in student_workers[:, 0]]) <= u_ijk[np.where(student_workers[:, 0] == i)[0], j, k]
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

    # Handle Social Credit Scores
    # Philosophy is to have a minimum average social score on each shift so that
    # social and reserved student workers get paired together
    
    ### Calculate Overall Average Social Score ###
    #overall_average_social_score = np.mean(student_workers[:, 6]) #column 7 --> index 6
    #print(overall_average_social_score)

    ### Constraints for Average Social Score ###
    #for j in range(x_ijk.shape[1]):
    #    for k in range(x_ijk.shape[2]):
            # Extract social credit scores for workers assigned to the shift
    #        social_scores = [a_ijk[i, j, k]*student_workers[i, 6] for i in range(x_ijk.shape[0])]
            #print(social_scores)
            # Ensure that the average social score is at least overall average - 0.5
    #        if len(social_scores) > 0:  # Check if there are workers assigned to the shift
    #            scheduler_model += (
    #                lpSum(social_scores) / len(social_scores) >= overall_average_social_score - 0.5
    #            )

    scheduler_model.solve()
    scheduler_model.writeLP("mtc_scheduler_model.lp")
    num_j = x_ijk.shape[1]
    num_k = x_ijk.shape[2]
    result_array = [[[] for _ in range(num_k)] for _ in range(num_j)]
    model_analytics = [[] for _ in range(len(student_workers[:, 0]))]
    
    time_columns = [
    "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",
    "3-4 PM", "4-5 PM", "5-6 PM"]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for v in scheduler_model.variables():
        #print(v)
        if v.varValue is not None and v.varValue > 1e-6:
            i, j, k = varsKey[v.name]
            weight = x_ijk[i, j, k]
            model_analytics[i].append(f"{days_of_week[j]} {time_columns[k]} shift with weight: {x_ijk[i, j, k]}")
            worker_name = student_workers[np.where(student_workers[:, 0] == i)][0, 1]
            result_array[j][k].append(worker_name)
            #result_array[j][k].append(i)
    
    result_array_transposed = list(map(list, zip(*result_array)))



    # Create a DataFrame with days of the week as index and time columns as columns
    df = pd.DataFrame(result_array_transposed, index=time_columns, columns=days_of_week)
    
    # Create a DataFrame with student names as the index
    analytics_df = pd.DataFrame(model_analytics, index=student_workers[:, 1])
    
    return df, analytics_df



if __name__=="__main__":

    input_path = "MTC - D24 Availability_February 20, 2024_21.31.xlsx" ##Qualtrics file path here
    mode = "Qualtrics"

    social_credit_score_list = [2] * 55 #change this as you wish but we have 55 MTC workers and by default I have them getting all 3's
    priority_list = [False] * 55

    parameterTableOutput = (social_credit_score_list, priority_list)

    cleaned, (student_workers, x_ijk, l_ijk, u_ijk, social_credit_score_list, priority_list) = get_data(mode, parameterTableOutput=parameterTableOutput, file_path=input_path)

    solution, analytics_df = compute_solution(student_workers, x_ijk, l_ijk, u_ijk)


    with pd.ExcelWriter("solution.xlsx") as writer:
            solution.to_excel(writer, sheet_name="output solution") #index not false to show the time columns
            analytics_df.to_excel(writer, sheet_name="model analytics")
