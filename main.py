from player import *


def main():
    global list
    initial()

    human = player()
    human.setname('player')
    computer = player()
    computer.setname('computer')
    r_int = 0
    while 1:
        r_int = r_int + 1
        print('round ', r_int, ' begins')
        win_flag, round_num = round(human, computer)
        print("computer's cards: ", end='')
        computer.printcards()
        print()
        print("human's cards: ", end='')
        human.printcards()
        print()
        if win_flag:
            print("human wins!")
        else:
            print("computer wins!")
        print("number of rounds: ", round_num)
        human.reset()
        computer.reset()
        break


if __name__ == '__main__':
    main()
