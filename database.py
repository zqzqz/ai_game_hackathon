import sqlite3
from judge import *
from random import *
import time

tmplisth=[]
tmplistc=[]
cx = sqlite3.connect("d:\\test.db")
cu = cx.cursor()
def dbset():
    pass
    cu.execute("""create table cardtable (id integer primary key autoincrement, value char[11], wins long, loss long, rate float)""")
    #cu.execute("insert into cardtable ('A1A2A3A4',1,0)")
    #cu.execute("update cardtable set wins = wins + 1")



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
        return 1

    def auto_choice(self):  #use api here
        return 1

def round(human, computer):
    global list, currentlist, tmplistc, tmplisth
    win_flag = -1
    round_num = 0

    currentlist = list
    computer.fetch()  #各抽两次
    human.fetch()
    computer.fetch()
    human.fetch()

    if computer.cards[0][1] >= human.cards[0][1]:
        order_flag = 0   # 0 computer first
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
        if round_num==3:
            tmplisth = human.sortedcards+[]
            tmplistc = computer.sortedcards+[]
            #print("asdadg",tmplisth, tmplistc)
        if win_flag >= 0:
            return (win_flag, round_num)

    if decidewinner(computer, human):
        win_flag = 1
    else:
        win_flag = 0
    return (win_flag, round_num)

def transfer(card):

    #print("second", tmplisth, tmplistc)
    t=""
    color = ['A','B','C','D']
    t+=color[card[0]]
    num = ['0','0','2','3','4','5','6','7','8','9','0','j','q','k','a']
    t+=num[card[1]]
    return t

def train():
    global tmplisth, tmplistc
    print(time.strftime('%Y-%m-%d %X', time.localtime()))
    human = player()
    human.setname('player')
    computer = player()
    computer.setname('computer')
    for i in range(20000):
        print(i)
        initial() #初始化卡牌
        win_flag= round(human, computer)  #一个回合
        #print("third", tmplisth, tmplistc)

        hstr = ""   #tmplisth human first four cards; tmplistc computer
        for i in tmplisth:
            hstr += transfer(i)
        cstr = ""
        for i in tmplistc:
            cstr += transfer(i)
        if win_flag:  #1 human wins
            cu.execute("select id,wins,loss from cardtable where value ='"+hstr+"'")
            tmp = cu.fetchall()
            if tmp==[]:
                cu.execute("insert into cardtable (value,wins,loss,rate) values('"+ hstr+"',1,0,1)")
                cx.commit()
            else:
                id, wins, loss = tmp[0]
                wins = wins+1
                rate = wins/(wins+loss)
                cu.execute("update cardtable set wins = "+str(wins)+", rate ="+str(rate)+", rate ="+str(rate)+"  where id = "+str(id))
                cx.commit()
            cu.execute("select id,wins,loss from cardtable where value ='" + cstr + "'")
            tmp = cu.fetchall()
            if tmp == []:
                cu.execute("insert into cardtable (value,wins,loss,rate) values('" + cstr + "',0,1,0)")
                cx.commit()
            else:
                id, wins, loss = tmp[0]
                loss = loss + 1
                rate = wins / (wins + loss)
                cu.execute("update cardtable set loss = "+str(loss)+", rate ="+str(rate)+" where id = " + str(id))
                cx.commit()
        else:
            cu.execute("select id,wins,loss from cardtable where value ='" + hstr + "'")
            tmp = cu.fetchall()
            if tmp == []:
                cu.execute("insert into cardtable (value,wins,loss,rate) values('" + hstr + "',0,1,0)")
                cx.commit()
            else:
                id, wins, loss = tmp[0]
                loss = loss + 1
                rate = wins / (wins + loss)
                cu.execute("update cardtable set loss = " + str(loss) + ",rate=" +str(rate)+" where id = " + str(id))
                cx.commit()
            cu.execute("select id,wins,loss from cardtable where value ='" + cstr + "'")
            tmp = cu.fetchall()
            if tmp == []:
                cu.execute("insert into cardtable (value,wins,loss,rate) values('" + cstr + "',1,0,1)")
                cx.commit()
            else:
                id, wins, loss = tmp[0]
                wins = wins + 1
                rate = wins / (wins + loss)
                cu.execute("update cardtable set wins = " + str(wins) + ", rate=" + str(rate)+" where id = " + str(id))
                cx.commit()
        human.reset()
        computer.reset()
    print(time.strftime('%Y-%m-%d %X', time.localtime()))


def test():
    cu.execute("select * from cardtable")
    datarows = cu.fetchall()
    for datarow in datarows:
        print(datarow)
    cu.execute("select sum(wins),sum(loss) from cardtable")
    print(cu.fetchall())
    cu.execute("select * from cardtable where rate between 0.1 and 0.9")
    #cu.execute("select count(1) from cardtable group by value having count(1) > 1")
    #cu.execute("select count(1) from cardtable")
    print(cu.fetchall())





#dbset()
train()
#test()