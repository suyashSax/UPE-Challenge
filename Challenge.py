#!/usr/bin/env python
# coding: utf-8

import requests
global ROOT

def init_session():
    r = requests.post(ROOT + '/session', data={"uid": "404735401"})
    TOKEN = r.json()["token"]
    return TOKEN

def game_status(token):
    r = requests.get(ROOT + '/game?token=' + token)
    return r.json()

def out_of_bounds(p, size):
    if p[0] < 0 or p[1] < 0 or p[0] >= size[0] or p[1] >= size[1]:
        return True
    return False

def compute_move(src, d):
    if d == "UP":
        return (src[0], src[1]-1)
    if d == "DOWN":
        return (src[0], src[1]+1)
    if d == "LEFT":
        return (src[0]-1, src[1])
    if d == "RIGHT":
        return (src[0]+1, src[1])

def request_move(direction, token):
    r = requests.post(ROOT + '/game?token=' + token, data={"action":direction})
    res = r.json()["result"]
    
    return res

def search(token):
    visited = set()
    invalid = set()

    move_stack = []
        
    status = game_status(token)
    curr = (status["current_location"][0], status["current_location"][1])
    size = status["maze_size"]
    
    visited.add(curr)
    
    directions = ["UP", "RIGHT", "DOWN", "LEFT"]
    direction_back = {
        "UP": "DOWN",
        "DOWN": "UP",
        "LEFT": "RIGHT",
        "RIGHT": "LEFT"
    } 
        
    while (True):
        made_a_move = False        
        for direction in directions:
            next_point = compute_move(curr, direction)
            
            if next_point in invalid or next_point in visited:
                continue;
            
            if out_of_bounds(next_point, size):
                invalid.add(next_point)
                continue;

            move_result = request_move(direction, token)

            if move_result == "WALL":
                invalid.add(next_point)

            elif move_result == "SUCCESS":
                visited.add(next_point)
                move_stack.append(direction)
                curr = next_point
                made_a_move = True
                break;
            
            elif move_result == "END":
                return True;
            
            else:
                print ("Err... Timed out")
                return False
                
        if not made_a_move:
            # Backtrack
            last_move = move_stack.pop()
            
            prev_point = compute_move(curr, direction_back[last_move])
            request_move(direction_back[last_move], token)
            
            curr = prev_point
     
    return False;

def play(game, token):
    levels = game["total_levels"]
    
    if not levels:
        print ("Game probably completed, TOKEN still not invalidated")
        return
    
    for i in range(levels):
        res = search(token)
        if not res:
            print ("Gracefully accepting failure")
            return;
        print ("Completed Level", i + 1)
    print ("Challenge Complete ✅")

if __name__ == "__main__":
    ROOT = 'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com'
    TOKEN = init_session()
    play(game_status(TOKEN), TOKEN)
