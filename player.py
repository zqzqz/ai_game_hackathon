from random import randint
from judge import *

list = []
currentlist=[]

def initial():
    global list
    for i in range(4):
        for j in range(2,15):
            list.append((i,j))


class player(object):
    def __init__(self):
        self.name = 'Unnamed'
        self.cards = []
        self.sortedcards = []
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
        print("input a to bet or input b to give up.")
        x = input("ïnput: ")
        if x=='b':
            return 0
        else:
            return 1

    def auto_choice(self):  #use api here
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
                    print(i[1], end=' ')
                elif i[1]==11:
                    print('J', end=' ')
                elif i[1]==12:
                    print('Q', end=' ')
                elif i[1]==13:
                    print('K', end=' ')
                else:
                    print('A', end=' ')
                flag = False
            else:
                print("暗牌", end=' ')



def round(human, computer):
    global list, currentlist
    win_flag = -1
    round_num = 0

    currentlist = list
    computer.fetch()
    human.fetch()
    computer.fetch()
    human.fetch()

    print("computer's cards: ", end='')
    computer.printcards()
    print()
    print("human's cards: ", end='')
    human.printcards()
    print()

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

    round_num+=1
    if win_flag >=0 :
        return (win_flag, round_num)

    for k in range(3):
        computer.fetch()
        human.fetch()
        print("computer's cards: ", end='')
        computer.printcards()
        print()
        print("human's cards: ", end='')
        human.printcards()
        print()
        # print("tmp cards")
        # print(human.cards, computer.cards)
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

        round_num += 1
        if win_flag >= 0:
            return (win_flag, round_num)

    if decidewinner(computer, human):
        win_flag = 1
    else:
        win_flag = 0
    return (win_flag, round_num)
