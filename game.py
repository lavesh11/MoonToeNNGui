import collections
import pickle
import random
import math
import itertools
import time

EMPTY = 0
PLAYER_X = 1
PLAYER_O = -1
DRAW = 2

BOARD_SIZE = 15
LINE = 5

NAMES = {0: '-', 1: 'X', -1: 'O'}

def printboard(state):
    cells = []
    print ' ',
    for i in range(BOARD_SIZE):
        print '{0}'.format(str(i).center(5)),
    print '\n'
    for i in range(BOARD_SIZE):
        print i,
        for j in range(BOARD_SIZE):
            print '{0}'.format(NAMES[state[i][j]].center(5)),
        print('\n')

def emptyboard():
    state = []
    for i in range(BOARD_SIZE):
        state.append([])
        for j in range(BOARD_SIZE):
            state[i].append(0)
    return state


def inside(i, j):
    return BOARD_SIZE > i >= 0 and BOARD_SIZE > j >=0


def gameover(state):
    # Horizontal winning
    total_zero = 0
    for i in range(BOARD_SIZE):
        ct = {0:0, 1:0, -1:0}
        for j in range(LINE-1):
            ct[state[i][j]] += 1
            if state[i][j] == 0:
                total_zero+=1
        for j in range(LINE-1,BOARD_SIZE):
            if state[i][j] == 0:
                total_zero+=1
            ct[state[i][j]]+=1
            # print i,j,state[i][j],ct[state[i][j]]
            if state[i][j] != 0 and ct[state[i][j]] == LINE:
                return state[i][j]
            ct[state[i][j-LINE+1]]-=1

    # Vertical winning
    for j in range(BOARD_SIZE):
        ct = {0:0, 1:0, -1:0}
        for i in range(LINE-1):
            ct[state[i][j]]+=1
        for i in range(LINE-1,BOARD_SIZE):
            ct[state[i][j]]+=1
            if state[i][j] != 0 and ct[state[i][j]] == LINE:
                return state[i][j]
            ct[state[i-LINE+1][j]]-=1

    # Diagonal winning
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            ct1 = {0:0, 1:0, -1:0}
            ct2 = {0: 0, 1: 0, -1: 0}
            for k in range(LINE):
                x,y = i+k,j+k
                if inside(x,y):
                    ct1[state[x][y]]+=1
                x,y = i+k,j-k
                if inside(x,y):
                    ct2[state[x][y]]+=1
            if ct1[1] == LINE or ct2[1] == LINE:
                return 1
            elif ct1[-1] == LINE or ct2[-1] == LINE:
                return -1

    if total_zero == 0:
        return 2
    return 0

class Agent(object):
    def __init__(self, player, lossval = 0):
        self.values = {}
        self.player = player
        self.epsilon = 0.1
        self.lossval = lossval
        self.prevstate = None
        self.prevvalue = 0
        self.alpha = 0.99

    def winnerval(self, winner, key=None):
        if winner == self.player:
            return 1
        elif winner == DRAW:
            return 0
        elif winner == EMPTY:
            return (math.log(key[0]+1)+math.sqrt(key[1])+key[2]+(2*key[3])**2-(math.log(key[4]+1)+math.sqrt(key[5])+3*key[6]+(5*key[7])**2)+1000)/2000
        else:
            return self.lossval

    def add(self, state, key):
        winner = gameover(state)
        self.values[key] = self.winnerval(winner,key)

    def available_moves(self,state):
        for i, j in itertools.product(range(BOARD_SIZE), range(BOARD_SIZE)):
            if state[i][j] == 0:
                yield (i, j)

    def lookup(self, state):
        c = self.possible(state)
        if self.player == 1:
            key = (c[(1,0,4)],c[(2,0,3)],c[(3,0,2)],c[(4,0,1)],c[(0,1,4)],c[(0,2,3)],c[(0,3,2)],c[(0,4,1)])
        else:
            key = (c[(0,1,4)],c[(0,2,3)],c[(0,3,2)],c[(0,4,1)], c[(1,0,4)],c[(2,0,3)],c[(3,0,2)],c[(4,0,1)])
        if not key in self.values:
            print 'value not found'
            self.add(state, key)
        return self.values[key]

    def backup(self, nextval):
        if self.prevstate != None:
            self.values[self.prevstate] += self.alpha * (nextval - self.prevvalue)

    def episode_over(self, winner):
        self.backup(self.winnerval(winner))
        self.prevstate = None
        self.prevvalue = 0

    def state_formula(self, state):
        c = self.possible(state)
        if self.player == 1:
            key = (c[(1,0,4)],c[(2,0,3)],c[(3,0,2)],c[(4,0,1)],c[(5,0,0)],c[(0,1,4)],c[(0,2,3)],c[(0,3,2)],c[(0,4,1)],c[(0,5,0)])
        else:
            key = (c[(0,1,4)],c[(0,2,3)],c[(0,3,2)],c[(0,4,1)],c[(0,5,0)], c[(1,0,4)],c[(2,0,3)],c[(3,0,2)],c[(4,0,1)],c[(5,0,0)])
        return math.log(key[0]+1)+math.sqrt(key[1])+key[2]+(2*key[3])**2+((5*key[4])**3)-(math.log(key[5]+1)+math.sqrt(key[6])+3*key[7]+(5*key[8])**2)

    def random_greedy(self,state):
        maxval = -999999999
        maxpos = None
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if state[i][j] == 0:
                    state[i][j] = self.player
                    val = self.state_formula(state)
                    state[i][j] = EMPTY
                    if val > maxval:
                        maxval = val
                        maxpos = (i, j)
        return maxpos


    def greedy(self,state):
        maxval = -999999999
        maxpos = None
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if state[i][j]==0:
                    state[i][j]= self.player
                    val = self.lookup(state)
                    state[i][j]=EMPTY
                    if val>maxval:
                        maxval = val
                        maxpos = (i,j)
        self.backup(maxval)
        #print 'in func ', maxpos
        return maxpos

    def action(self, state):
        #print 'in action'
        return self.greedy(state)

    def possible(self, state):
        line = collections.defaultdict(lambda: 0)
        for i in range(BOARD_SIZE):
            ct = {0: 0, 1: 0, -1: 0}
            for j in range(LINE - 1):
                ct[state[i][j]] += 1
            for j in range(LINE - 1, BOARD_SIZE):
                ct[state[i][j]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[i][j - LINE + 1]] -= 1

        for j in range(BOARD_SIZE):
            ct = {0: 0, 1: 0, -1: 0}
            for i in range(LINE - 1):
                ct[state[i][j]] += 1
            for i in range(LINE - 1, BOARD_SIZE):
                ct[state[i][j]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[i - LINE + 1][j]] -= 1

        for i in range(BOARD_SIZE - LINE + 1):
            ct = {0: 0, 1: 0, -1: 0}
            for k in range(LINE - 1):
                ct[state[i + k][k]] += 1
            inc = LINE - 1
            while inside(i + inc, inc):
                ct[state[i + inc][inc]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[i + inc - LINE + 1][inc - LINE + 1]] -= 1
                inc += 1
            ct = {0: 0, 1: 0, -1: 0}
            if i != 0:
                for k in range(LINE - 1):
                    ct[state[k][i + k]] += 1
                inc = LINE - 1
                while inside(inc, i + inc):
                    ct[state[inc][i + inc]] += 1
                    line[(ct[1],ct[-1],ct[0])] += 1
                    ct[state[inc - LINE + 1][i + inc - LINE + 1]] -= 1
                    inc += 1

        for i in range(LINE - 1, BOARD_SIZE):
            ct = {0: 0, 1: 0, -1: 0}
            for k in range(LINE - 1):
                ct[state[k][i - k]] += 1
            inc = LINE - 1
            while inside(inc, i - inc):
                ct[state[inc][i - inc]] += 1
                line[(ct[1],ct[-1],ct[0])] += 1
                ct[state[inc - LINE + 1][i - inc + LINE - 1]] -= 1
                inc += 1
            ct = {0: 0, 1: 0, -1: 0}
            if i != BOARD_SIZE - 1:
                for k in range(LINE - 1):
                    ct[state[BOARD_SIZE - i - 1 + k][BOARD_SIZE - 1 - k]] += 1
                inc = LINE - 1
                while inside(BOARD_SIZE - i - 1 + inc, BOARD_SIZE - 1 - inc):
                    ct[state[BOARD_SIZE - i - 1 + inc][BOARD_SIZE - 1 - inc]] += 1
                    line[(ct[1],ct[-1],ct[0])] += 1
                    ct[state[BOARD_SIZE - i - 1 + inc - LINE + 1][BOARD_SIZE - 1 - inc + LINE - 1]] -= 1
                    inc += 1
        return line

def play(agent1, agent2):
    state = emptyboard()
    for k in range(BOARD_SIZE*BOARD_SIZE):
        if k % 2 == 0:
            move = agent1.action(state)
            state[move[0]][move[1]] = agent1.player
        else:
            move = agent2.action(state)
            state[move[0]][move[1]] = agent2.player
        winner = gameover(state)
        if winner != EMPTY:
            # print winner
            return winner

    # print winner
    return winner

def play_test(agent1, agent2,val):
    state = emptyboard()
    for k in range(BOARD_SIZE*BOARD_SIZE):
        #printboard(state)
        #time.sleep(3)
        if k % 2 == 0:
            move = agent1.action(state,val)
            state[move[0]][move[1]] = agent1.player
        else:
            move = agent2.action(state,-val)
            state[move[0]][move[1]] = agent2.player
        winner = gameover(state)
        if winner != EMPTY:
            #printboard(state)
            #time.sleep(3)
            # print winner
            return winner

    # print winner
    return winner

class Human(object):
    def __init__(self, player):
        self.player = player

    def action(self, state):
        printboard(state)
        parsed = False
        while not parsed:
            try:
                action = raw_input('your move? ')
                move = (int(action.split(',')[0]), int(action.split(',')[1]))
                parsed = True
            except ValueError:
                print 'incorrect input'
        return move

    def episode_over(self, winner):
        if winner == DRAW:
            print 'GAME DRAW.'
        else:
            print 'Player {0} wins'.format(NAMES[winner])

if __name__ == '__main__':
    a1 = Agent(1, lossval=-1)
    a2 = Agent(-1, lossval=-1)
    with open('gameX4.pickle', 'rb') as handle:
        c = pickle.load(handle)
    a1.values = c

    print 'pickleX files loaded'
    with open('gameO4.pickle', 'rb') as handle:
        c = pickle.load(handle)
    a2.values = c

    print 'pickleO files loaded'

    while True:
        a3 = Human(1)
        a4 = Human(-1)
        x = raw_input('press 1 for 1st chance otherwise 2')
        if int(x) == 1:
            winner = play(a3, a2)
            a3.episode_over(winner)
            a2.episode_over(winner)
        else:
            winner = play(a1, a4)
            a1.episode_over(winner)
            a4.episode_over(winner)
