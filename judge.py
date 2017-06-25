#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
import os
import random

suit = ["梅花","黑桃","方片","红桃"]
val  = ["-1","-1","2","3","4","5","6","7","8","9","10","J","Q","K","A"]
scorelist=["大同花顺", "同花顺", "四条", "葫芦", "同花", "顺子", "三条", "两对", "一对", "高牌"]

human_win_sarcasm = ["你居然赢了！这不可能！", "你居然赢了！再来一盘？", "我不服，再来一盘"]
computer_win_sarcasm = ["哈哈！输了吧", "你不可能战胜我的！认命吧", "输给我是正常的"]


def speak(text):
    # print("hello world")
    os.system("say -v Ting-Ting " + text)

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
    # return 1 when human wins
    # print("### sorted cards")
    # print(computer.sortedcards)
    # print(human.sortedcards)
    human_score = score(human)
    computer_score = score(computer)
    computer_card_string = ""
    human_card_string = ""

    # explicitly show the all cards of computer and human
    for it in computer.sortedcards:
        computer_card_string += suit[it[0]] + " " + val[it[1]]+"\t"
    # print("computer's cards:   %s" %(computer_card_string))
    for it in human.sortedcards:
        human_card_string += suit[it[0]] + " " + val[it[1]]+"\t"
    # print("human's cards:      %s" %(human_card_string))

    # print("human: ", scorelist[human_score])
    # print("computer: ", scorelist[computer_score])

    if human_score == computer_score:
        return tie(score, computer, human)
    elif human_score < computer_score:
        speak(random.choice(human_win_sarcasm))
        return 1
    else:
        speak(random.choice(computer_win_sarcasm))
        return 0
