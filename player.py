#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import numpy as np
import cv2
import time
import threading
import httplib, urllib, base64
import urllib2
import json
import traceback
from random import randint
from judge import *
import sqlite3

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': 'df955ff6c6e240b38701e3cb04c5052e',
}

params = urllib.urlencode({
    # Request parameters
})

colorBGR = [(105, 140, 255), (255, 144, 30), (140, 199, 0), (60, 20, 220), (2, 255, 255)]
recThickness = 2

discard_sarcasm = ["弃牌吧，少年！", "放弃是明智的选择！", "你居然放弃了！哈哈哈哈哈哈"]
neutral_sarcasm = ["你居然有一张扑克脸", "面无表情，很厉害", "看来是高手，面无表情"]
happiness_sarcasm = ["不要以为你就要赢了！", "我不会让你得逞的", "你太得意了！"]


try:
    conn = httplib.HTTPSConnection('api.cognitive.azure.cn')
except Exception as e:
    print("cannot connect to Azure API!")
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
    exit(1)

list = []
currentlist=[]
fixList = []

def setFixList(n):
    global fixList
    if n==1:
        # computer win, counter bluff
        fixList = [(2,9), (0,4), (3,1), (2,7), (0,12), (1,6), (2,12), (1,11), (3,3), (1,5)]
    elif n==2:
        # normal
        fixList = [(1,8), (2,6), (2,9), (3,3), (0,5), (0,10), (0,11), (1,11), (0,2), (0,14)]
    elif n==3:
        # human win, bluff
        fixList = [(0,11), (1,3), (1,6), (2,8), (0,3), (0,5), (0,12), (2,3), (0,13), (0,8)]

def addRectangle(img, rectangle, scores, index):
    color = colorBGR[index % len(colorBGR)]
    height = rectangle['height']
    left = rectangle['left']
    top = rectangle['top']
    width = rectangle['width']
    cv2.rectangle(img, (left, top), (left + width, top + height), color, recThickness)
    addScores(img, scores, color, left, top - 5)

def addScores(img, scores, color, x, y):
    neutral = scores['neutral']
    happiness = scores['happiness']
    scores.pop('neutral', None)
    max_emotion = max(scores, key=scores.get)
    max_score = scores[max_emotion]
    if (max_score < 0.1):
        max_emotion = 'neutral'
        max_score = neutral
    cv2.putText(img, max_emotion + ": " + str(max_score), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color)

class ImgRequest(object):

    def request(self, player):
    
        imgRGB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        ret, imgJPG = cv2.imencode(".jpg", imgRGB)
        try:
            conn.request("POST", "/emotion/v1.0/recognize?%s" % params, imgJPG, headers)
            response = conn.getresponse()
            face_data = response.read()
            # print("emotion: " + face_data)
        except Exception as e:
            traceback.print_exc()
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            exit(1)
        people_info = json.loads(face_data)

        goodHand = 3
        if (len(people_info) > 0):
            goodHand = evaluateEmotion(people_info[0]['scores'])
        player.setHumanGoodHand(goodHand)

        index = 0
        for p in people_info:
            rectangle = p['faceRectangle']
            scores = p['scores']
            addRectangle(self.frame, rectangle, scores, index)
            print("[%d]: %s" %(index, scores))
            index = index + 1
        cv2.imshow("requested", self.frame)

    def setFrame(self, frame):
        self.frame = frame

def evaluateEmotion(scores):
    neutral = scores['neutral']
    happiness = scores['happiness']
    surprise = scores['surprise']
    sadness = scores['sadness']
    contempt = scores['contempt']
    disgust = scores['disgust']
    anger = scores['anger']
    fear = scores['fear']
    if (max([happiness, surprise, sadness, contempt, disgust, anger, fear]) < 0.05):
        speak(random.choice(neutral_sarcasm))
        return 3
    if (happiness > 0.9):
        speak(random.choice(happiness_sarcasm))
        return 5
    if (happiness > 0.7):
        speak("看你的表情很有自信")
        return 4
    if (anger > 0.15 or disgust > 0.2 or fear > 0.2 or contempt > 0.2):
        speak("惊不惊喜？意不意外？")
        return 1
    if (sadness > 0.2):
        speak("怎么这么伤心？你这个菜鸡！")
        return 0
    if (surprise > 0.2):
        speak("惊不惊喜？意不意外？")
        return 2;
    return 3

def transfer(card):
    #print("second", tmplisth, tmplistc)
    t=""
    color = ['A','B','C','D']
    t+=color[card[0]]
    num = ['0','0','2','3','4','5','6','7','8','9','0','j','q','k','a']
    t+=num[card[1]]
    return t

def initial():
    global list
    for i in range(4):
        for j in range(2,15):
            list.append((i,j))


class player(object):

    def __init__(self, request_arg=None, db_arg=None, dbcursor_arg=None):
        self.name = 'Unnamed'
        self.cards = []
        self.sortedcards = []
        self.imgRequest = request_arg
        self.humanGoodHand = 3
        self.update = False
        self.db = db_arg
        self.dbcursor = dbcursor_arg

    def setname(self, str):
        self.name = str

    def setHumanGoodHand(self, goodHand):
        self.humanGoodHand = goodHand

    def fetchFixed(self):
        global fixList
        nextCard = fixList[0]
        del fixList[0]
        self.cards.append(nextCard)

        length = len(self.sortedcards)
        for k in range(length):
            if nextCard[1] >= self.sortedcards[k][1]:
                self.sortedcards.insert(k, nextCard)
                break
        if length == len(self.sortedcards):
            self.sortedcards.append(nextCard)

    def fetch(self):
        global currentlist
        # print(currentlist)
        x = randint(0, len(currentlist) -1)

        tmp = currentlist[x]
        del currentlist[x]
        self.cards.append(tmp)

        length = len(self.sortedcards)
        for k in range(length):
            if tmp[1] >= self.sortedcards[k][1]:
                self.sortedcards.insert(k, tmp)
                break
        if length == len(self.sortedcards):
            self.sortedcards.append(tmp)

    def reset(self):
        self.sortedcards=[]
        self.cards=[]

    def choice(self):
        print("###")
        print("Bid: a | Fold: b")
        x = raw_input(">>>: ")
        if x=='b':
            speak(random.choice(discard_sarcasm))
            return 0
        else:
            # human fetch a card, analyze his emotion
            print("send photo as request")
            self.imgRequest.request(self)
            return 1

    def auto_choice(self):  #use api here
        #select computer's win rate from database
        selectstr="%"
        for card in self.sortedcards:
            selectstr = selectstr+transfer(card)+"%"
        self.dbcursor.execute("select avg(rate) from cardtable where value like \'"+selectstr+"\'")
        rate = 0.5
        if len(self.sortedcards) < 4:
            rate_searched = self.dbcursor.fetchall()[0][0]
            if rate_searched != None:
                rate = rate_searched
            print("computer rate  ",rate)
        # do decision

        print("computer rate  ",rate)
        print("humanGoodHand: ", self.humanGoodHand)
        if (self.humanGoodHand > 4):
            return 0
        elif (self.humanGoodHand < 2):
            return 1
        else:
            score = rate * self.humanGoodHand
            if score > 1.0:
                return 1
            else:
                return 0
        return 1


    def printcards(self):
        flag = True
        for i in self.cards:
            if flag or self.name!="computer":
                if i[0]==0:
                    print("梅花",end=' ')
                elif i[0]==1:
                    print("黑桃",end=' ')
                elif i[0]==2:
                    print("方片",end=' ')
                else:
                    print("红桃",end=' ')
                if i[1]<11:
                    print(i[1], end='\t')
                elif i[1]==11:
                    print('J', end='\t')
                elif i[1]==12:
                    print('Q', end='\t')
                elif i[1]==13:
                    print('K', end='\t')
                else:
                    print('A', end='\t')
                flag = False
            else:
                print("暗牌", end='\t')

def print_cards (human, computer):
    print("computer's cards:   ", end='')
    computer.printcards()
    print()
    print("human's cards:      ", end='')
    human.printcards()
    print()

def round(human, computer, round_num):
    global list, currentlist
    initial()
    setFixList(round_num)
    win_flag = -1
    term_num = 0

    currentlist = list
    
    if round_num <4:
        computer.fetchFixed()
        human.fetchFixed()
        computer.fetchFixed()
        human.fetchFixed()
    else:
        computer.fetch()
        human.fetch()
        computer.fetch()
        human.fetch()

    print_cards(human, computer)

    #computer calculate human's win rate
    #computer.select_rival_rate(human)

    if computer.cards[0][1] > human.cards[0][1]:
        order_flag = 0
        if computer.auto_choice()== False:
            win_flag = 1
        elif human.choice()== False :
            win_flag = 0
    else:
        order_flag = 1
        if human.choice()== False :
            win_flag = 0
        elif computer.auto_choice()== False :
            win_flag = 1

    term_num+=1
    if win_flag >=0 :
        return (win_flag, round_num)

    for k in range(3):
        if round_num<4:
            computer.fetchFixed()
            human.fetchFixed()
        else:
            computer.fetch()
            human.fetch()
        print_cards(human, computer)
        if not order_flag:
            order_flag = 0
            if computer.auto_choice() == False:
                win_flag = 1
            elif human.choice() == False:
                win_flag = 0
        else:
            order_flag = 1
            if human.choice() == False:
                win_flag = 0
            elif computer.auto_choice() == False:
                win_flag = 1

        term_num += 1
        if win_flag >= 0:
            return (win_flag, round_num)

    if decidewinner(computer, human):
        win_flag = 1
    else:
        win_flag = 0
    return (win_flag, round_num)