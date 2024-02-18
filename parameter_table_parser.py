import numpy as np

def parameter_table_parser(choices):
    #input is [{"id":1,"name":"Q4","social_credit_score":3,"prioritize":false}, {}, {}, ...] where number of elements is number of rows in table
    #returns 2 lists:
        #List of social_credit_scores Ex: [3, 2, 5, 2, ...]
        #List of prioritize choices [false, false, true, false, ...]
    
    choices = choices[2:]

    social_credit_scoreList = []
    priority_list = []

    for i in choices:
        #id = i.get("id")
        #name = i.get("name")
        social_credit_score = i.get("social_credit_score")
        prioritizeAnswer = i.get("prioritize")

        social_credit_scoreList.append(social_credit_score)
        priority_list.append(prioritizeAnswer)

    print(social_credit_scoreList)
    print(priority_list)
    
    social_credit_scoreList = np.array(social_credit_scoreList)
    priority_list = np.array(priority_list)


    return social_credit_scoreList, priority_list
