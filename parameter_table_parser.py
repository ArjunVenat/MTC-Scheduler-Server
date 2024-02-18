
def parameter_table_parser(choices):
    #input is [{"id":1,"name":"Q4","socialButterflyScore":3,"prioritize":false}, {}, {}, ...] where number of elements is number of rows in table
    #returns 2 lists:
        #List of socialButterflyScores Ex: [3, 2, 5, 2, ...]
        #List of prioritize choices [false, false, true, false, ...]
    
    choices = choices[2:]

    socialButterflyScoreList = []
    prioritizeList = []

    for i in choices:
        #id = i.get("id")
        #name = i.get("name")
        socialButterflyScore = i.get("socialButterflyScore")
        prioritizeAnswer = i.get("prioritize")

        socialButterflyScoreList.append(socialButterflyScore)
        prioritizeList.append(prioritizeAnswer)

    print(socialButterflyScoreList)
    print(prioritizeList)


    return socialButterflyScoreList, prioritizeList
