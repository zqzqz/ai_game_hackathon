def flush(obj):
    tmp = obj.sortedcards[0][0]
    for i in obj.sortedcards:
        if i[0] != tmp:
            return 0
    return 1

def straight(obj):
    tmp = obj.sortedcards[0][1]
    for i in range(1, len(obj.sortedcards)):
        if obj.sortedcards[i][1]!=(tmp-1):
            return 0
        else:
            tmp = obj.sortedcards[i][1]
    return 1



def score(obj):
    flush_flag = flush(obj)
    if flush_flag:
        straight_flag = straight(obj)
        if straight_flag:
            if obj.sortedcards[0][1]==14:
                return 0
            else:
                return 1
        else:
            return 4
    else:
        straight_flag = straight(obj)
        if straight_flag:
            return 5
        else:
            if obj.sortedcards[0][1]==obj.sortedcards[3][1] or obj.sortedcards[1][1]==obj.sortedcards[4][1]:
                return 2
            if (obj.sortedcards[0][1]==obj.sortedcards[2][1] and obj.sortedcards[3][1]==obj.sortedcards[4][1]) or (obj.sortedcards[0][1]==obj.sortedcards[1][1] and obj.sortedcards[2][1]==obj.sortedcards[4][1]):
                return 3
            if  obj.sortedcards[0][1]==obj.sortedcards[2][1] or obj.sortedcards[2][1]==obj.sortedcards[4][1]:
                return 6
            if (obj.sortedcards[0][1]==obj.sortedcards[1][1] and obj.sortedcards[2][1]==obj.sortedcards[3][1]) or (obj.sortedcards[0][1]==obj.sortedcards[1][1] and obj.sortedcards[3][1]==obj.sortedcards[4][1]) or (obj.sortedcards[1][1]==obj.sortedcards[2][1] and obj.sortedcards[3][1]==obj.sortedcards[4][1]):
                return 7
            if obj.sortedcards[0][1]==obj.sortedcards[1][1] or obj.sortedcards[1][1]==obj.sortedcards[2][1] or obj.sortedcards[2][1]==obj.sortedcards[3][1] or obj.sortedcards[3][1]==obj.sortedcards[4][1]:
                return 8
            return 9

def tie(score, computer, human):
    if score==9:
        for i in range(5):
            if human.sortedcards[i][1]>computer.sortedcards[i][1]:
                return 1
            elif human.sortedcards[i][1]<computer.sortedcards[i][1]:
                return 0



def decidewinner(computer, human):
    # return 1 human wins
    # print("sorted cards")
    # print(computer.sortedcards)
    # print(human.sortedcards)
    human_score = score(human)
    computer_score = score(computer)

    scorelist=["大同花顺", "同花顺", "四条", "葫芦", "同花", "顺子", "三条", "两对", "一对", "高牌"]
    #print("human: ", scorelist[human_score])
    #print("computer: ", scorelist[computer_score])

    if human_score == computer_score:
        return tie(score, computer, human)
    elif human_score<computer_score:
        return 1
    else:
        return 0
