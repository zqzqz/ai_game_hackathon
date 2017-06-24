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

#connect database
db = sqlite3.connect("test.db")
dbcursor = db.cursor()

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': 'df955ff6c6e240b38701e3cb04c5052e',
}

params = urllib.urlencode({
    # Request parameters
})

colorBGR = [(255,0,0), (0,255,0), (0,0,255)]
textBGR = (255,0,0)
recThickness = 2

try:
    conn = httplib.HTTPSConnection('api.cognitive.azure.cn')
except Exception as e:
    print("cannot connect to Azure API!")
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
    exit(1)

list = []
currentlist=[]

def addRectangle(img, rectangle, scores, index):
    color = colorBGR[index % len(colorBGR)]
    height = rectangle['height']
    left = rectangle['left']
    top = rectangle['top']
    width = rectangle['width']
    cv2.rectangle(img, (left, top), (left + width, top + height), color, recThickness)
    addScores(img, scores, color, left, top - 5)

def addScores(img, scores, color, x, y):
    happiness = scores['happiness']
    cv2.putText(img, "happiness: " + str(happiness), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color)


class ImgRequest(object):

    def request(self):
        imgRGB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        ret, imgJPG = cv2.imencode(".jpg", imgRGB)
        # if (not ret):
            #print("frame encode error!")
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

def initial():
    global list
    for i in range(4):
        for j in range(2,15):
            list.append((i,j))


class player(object):
    def __init__(self, request_arg=None):
        self.name = 'Unnamed'
        self.cards = []
        self.sortedcards = []
        self.imgRequest = request_arg

    def setname(self, str):
        self.name = str
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
            return 0
        else:
            # human fetch a card, analyze his emotion
            print("send photo as request")
            self.imgRequest.request()
            return 1

    def auto_choice(self,rival):  #use api here
        #select computer's win rate from database
        selectstr="%"
        for card in self.sortedcards:
            selectstr = selectstr+transfer(card)+"%"
        dbcursor.execute("select avg(rate) from cardtable where value like \'"+selectstr+"\'")
        rate = dbcursor.fetchall()
        print("computer rate  ",rate)
        
        #select human's  win rate (one known card)
        selectstr = "%"+transfer(rival.cards[0])+"%"
        dbcursor.execute("select avg(rate) from cardtable where value like \'"+selectstr+"\'")
        rivalrate = dbcursor.fetchall()
        print("computer rate  ",rivalrate)
        
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

def round(human, computer):
    global list, currentlist
    win_flag = -1
    round_num = 0

    currentlist = list
    computer.fetch()
    human.fetch()
    computer.fetch()
    human.fetch()

    print_cards(human, computer)

    if computer.cards[0][1] > human.cards[0][1]:
        order_flag = 0
        if computer.auto_choice(human)== False:
            win_flag = 1
        elif human.choice()== False :
            win_flag = 0
    else:
        order_flag = 1
        if human.choice()== False :
            win_flag = 0
        elif computer.auto_choice(human)== False :
            win_flag = 1

    round_num+=1
    if win_flag >=0 :
        return (win_flag, round_num)

    for k in range(3):
        computer.fetch()
        human.fetch()
        print_cards(human, computer)
        if not order_flag:
            order_flag = 0
            if computer.auto_choice(human) == False:
                win_flag = 1
            elif human.choice() == False:
                win_flag = 0
        else:
            order_flag = 1
            if human.choice() == False:
                win_flag = 0
            elif computer.auto_choice(human) == False:
                win_flag = 1

        round_num += 1
        if win_flag >= 0:
            return (win_flag, round_num)

    if decidewinner(computer, human):
        win_flag = 1
    else:
        win_flag = 0
    return (win_flag, round_num)
