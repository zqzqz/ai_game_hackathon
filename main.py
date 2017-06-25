#!/usr/local/bin/python
# -*- coding:utf-8 -*-

from player import *

lock = threading.Lock()

cap = cv2.VideoCapture(0)
windowSize = (480, 270)

imgRequest = ImgRequest()


def video_loop():
    global frame
    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, windowSize)
        if (not ret):
            continue
        imgRequest.setFrame(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    exit(0)

def game():
    global frame
    db = sqlite3.connect("test.db")
    dbcursor = db.cursor()
    human = player(request_arg=imgRequest, db_arg=db, dbcursor_arg=dbcursor)
    human.setname('player')
    computer = player(db_arg=db, dbcursor_arg=dbcursor)
    computer.setname('computer')
    r_int = 0
    while(True):
        r_int = r_int + 1
        x = raw_input(">>>: enter to begin")
        print "============================================= "
        print "### round ", r_int, " begins"
        win_flag, round_num = round(human, computer, r_int)
        if win_flag:
            print "### human wins!"
        else:
            print "### computer wins!"
        print "### number of rounds: ", round_num
        human.reset()
        computer.reset()
        # break


if __name__ == '__main__':
    # cv2.namedWindow('requested', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('requested', windowSize[0], windowSize[1])
    game_thread = threading.Thread(group=None, target=game)
    game_thread.start()
    video_loop()
    # main()
