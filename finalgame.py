from network_helpers import load_network
import functools
from moon_toe import emptyboard, available_moves, apply_move,gameover, state_key
from network_helpers import create_network
import tensorflow as tf
import numpy as np

EMPTY = 0
PLAYER_X = 1
PLAYER_O = -1
DRAW = 2

BOARD_SIZE = 10
LINE_SIZE = 5

NAMES = {0: '_', 1: 'X', -1: 'O'}

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

if __name__ == '__main__':
    input_layer, output_layer, variables = create_network(11, (100, 100, 100, 100, 100), output_nodes=1,output_softmax=False)
    '''
    def make_training_move(board_state, side):
        a1 = Agent(side, lossval=-1)
        move = a1.random_greedy(board_state)
        return move

    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        load_network(session, variables, 'MoonGo_reinforcement.pickle')
        board_state = emptyboard()
        if bool(random.getrandbits(1)):
            side = 1
        else:
            side = -1
        while True:
            board_state = apply_move(board_state, make_training_move(board_state, side), side)
            printboard(board_state)
            ol = session.run(output_layer, feed_dict={input_layer: np.array(state_key(board_state)).reshape(1, 10)})
            print 'network output value ', ol
            winner = gameover(board_state)
            print 'winner ', winner
            if winner != 0:
                break
            side = -side
            '''
    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        # MoonGo_supervised_cross_prob MoonGo_reinforcement
        load_network(session, variables, 'MoonGo_reinforcement.pickle')
        while 1:
            board_state = emptyboard()
            player_turn = 1

            while True:
                printboard(board_state)
                _available_moves = list(available_moves(board_state))

                if len(_available_moves) == 0:
                    print("no moves left, game ended a draw")
                    break
                if player_turn > 0:
                    action = raw_input('your move? ')
                    move = (int(action.split(',')[0]), int(action.split(',')[1]))
                else:
                    positions = []
                    for i in range(BOARD_SIZE):
                        for j in range(BOARD_SIZE):
                            if board_state[i][j] == 0:
                                board_state[i][j] = -1
                                ol = session.run(output_layer, feed_dict={input_layer: np.array(state_key(board_state,1)).reshape(1, 11)})
                                positions.append((ol,(i,j)))
                                board_state[i][j] = 0
                    positions = sorted(positions, key=lambda tup: tup[0])
                    minval = 999999
                    move = None
                    for x in range(min(3,len(positions))):
                        board_state[positions[x][1][0]][positions[x][1][1]] = -1
                        print (positions[x][1][0],positions[x][1][1])
                        minval1 = -999999
                        move1 = None
                        for i in range(BOARD_SIZE):
                            for j in range(BOARD_SIZE):
                                if board_state[i][j] == 0:
                                    board_state[i][j] = 1
                                    ol = session.run(output_layer, feed_dict={input_layer: np.array(state_key(board_state,-1)).reshape(1, 11)})
                                    #print (i,j), ol
                                    if ol > minval1:
                                        minval1 = ol
                                        move1 = (i,j)
                                    board_state[i][j] = 0
                        board_state[positions[x][1][0]][positions[x][1][1]] = 0
                        print 'minval1 ',minval1, ' move1 ',move1
                        if minval1 < minval:
                            move = (positions[x][1][0],positions[x][1][1])
                            minval = minval1
                if move not in _available_moves:
                    print("illegal move ", move)
                    break

                board_state = apply_move(board_state, move, player_turn)

                winner = gameover(board_state)
                if winner != 0 and winner != 2:
                    print("we have a winner, side: %s" % player_turn)
                    break
                player_turn = -player_turn
