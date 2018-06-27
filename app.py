from flask import Flask, render_template, jsonify, request
from game import Agent, emptyboard, gameover, NAMES,  BOARD_SIZE, printboard
import numpy as np
from network_helpers import load_network
import tensorflow as tf
from moon_toe import emptyboard, available_moves, apply_move,gameover, state_key
from network_helpers import create_network

app = Flask(__name__)

input_layer, output_layer, variables = create_network(11, (100, 100, 100, 100, 100), output_nodes=1,output_softmax=False)
def action1(board_state):
    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        load_network(session, variables, 'MoonGo_reinforcement.pickle')
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
        return move

import math
def easy(board_state):
    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        load_network(session, variables, 'MoonGo_reinforcement.pickle')
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
        for x in range(10):
            print positions[x][0], ' co-ordinate ',positions[x][1]
        print '--------------------------------------------'
        for x in range(min(5,len(positions))):
            board_state[positions[x][1][0]][positions[x][1][1]] = -1
            if (abs(gameover(board_state))==1):
                return positions[x][1]
            print (positions[x][1][0],positions[x][1][1]), 'val ',positions[x][0]
            minval1 = -999999
            move1 = None
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board_state[i][j] == 0:
                        board_state[i][j] = 1
                        if (abs(gameover(board_state)) == 1):
                            return (i,j)
                        ol = session.run(output_layer, feed_dict={input_layer: np.array(state_key(board_state,-1)).reshape(1, 11)})
                        if ol > minval1:
                            print (i, j), ol
                            minval1 = ol
                            move1 = (i,j)
                        board_state[i][j] = 0
            board_state[positions[x][1][0]][positions[x][1][1]] = 0
            #print 'minval1 ',minval1, ' move1 ',move1
            if math.fabs(minval1+1) < minval:
                move = (positions[x][1][0],positions[x][1][1])
                minval = math.fabs(minval1+1)
        #print 'cur ',positions[0][1], ' can ', move
        print '*$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$*'
        return move

def easy1(board_state):
    with tf.Session() as session:
        session.run(tf.initialize_all_variables())
        load_network(session, variables, 'MoonGo_reinforcement.pickle')
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
            print (positions[x][1][0],positions[x][1][1]), 'val ',positions[x][0]
            minval1 = -999999
            move1 = None
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board_state[i][j] == 0:
                        board_state[i][j] = 1
                        ol = session.run(output_layer, feed_dict={input_layer: np.array(state_key(board_state,-1)).reshape(1, 11)})
                        print (i,j), ol
                        if ol > minval1:
                            minval1 = ol
                            move1 = (i,j)
                        board_state[i][j] = 0
            board_state[positions[x][1][0]][positions[x][1][1]] = 0
            print 'minval1 ',minval1, ' move1 ',move1
            if math.fabs(minval1+1) < minval:
                move = (positions[x][1][0],positions[x][1][1])
                minval = math.fabs(minval1+1)
        return move


@app.route('/')
def index():
    return render_template('index.html')


def is_board_full(state):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if state[i][j] == 0:
                return False
    return True


@app.route('/move', methods=['POST'])
def move():
    post = request.get_json()
    board = post.get('board')
    chance = post.get('chance')
    state = emptyboard()
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == ' ':
                state[i][j] = 0
            elif board[i][j] == 'X':
                state[i][j] = 1
            else:
                state[i][j] = -1

    player = post.get('player')
    computer = post.get('computer')

    # print board,player,computer
    winner = gameover(state)
    #print("check here",winner)
    # Check if player won
    if winner == 2:
        return jsonify(tied = True, computer_wins = False, player_wins = False, board = board)
    elif NAMES[winner] == player:
        return jsonify(tied = False, computer_wins = False, player_wins = True, board = board)

    #print chance
    #print state

    if chance:
        #print 'Using O pickle'
        computer_move = easy(state)
    else:
        #print 'Using O pickle'
        computer_move = easy(state)

    #print computer_move,computer
    # Make the next move
    board[computer_move[0]][computer_move[1]] = computer
    state[computer_move[0]][computer_move[1]] = -1
    winner = gameover(state)

    #print("check comp",winner)
    # Check if computer won
    if winner == 2:
        return jsonify(computer_row = computer_move[0], computer_col = computer_move[1],
                      computer_wins = False, player_wins = False, tied=True, board=board)
    # Check if game is over
    elif NAMES[winner] == computer:
        return jsonify(computer_row = computer_move[0], computer_col = computer_move[1],
                       computer_wins = True, player_wins = False, tied=False, board = board)
    # Game still going
    return jsonify(computer_row = computer_move[0], computer_col = computer_move[1],
                   computer_wins = False, player_wins = False, board = board)

if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=8081)
