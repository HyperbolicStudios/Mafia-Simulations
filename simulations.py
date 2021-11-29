#definitions
import sys, os
import math
import random
from random import sample
#import numpy as np
#import matplotlib.pyplot as plt
random.seed

class player_object(): #player object
    def __init__(self,id,alignment,role,bp_status):
        self.id = id
        self.alignment = alignment
        self.role = role
        self.healed = False
        self.bp_status = bp_status
        self.shots = 3 #used for vig roles
class result_object(): #result object, used to store statistics about each simulated game
    def __init__(self,winner,length):
        self.winner = winner
        self.length = length

# Disable printing
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
# Restore printing
def enablePrint():
    sys.stdout = sys.__stdout__

def getPlayersByNotAlignment(playerlist,alignment):
    selectPlayers = []
    for player in playerlist:
        if player.alignment != alignment:
            selectPlayers.append(player)
    return(selectPlayers)

def getPlayersByAlignment(playerlist,alignment):
    selectPlayers = []
    for player in playerlist:
        if player.alignment == alignment:
            selectPlayers.append(player)
    return(selectPlayers)

def print_playerlist(playerlist):
    print("{} Players left: ".format(len(playerlist)),end="")
    for player in playerlist:
        print("Player {} ({}), ".format(player.id,player.alignment[:1]),end="")
    print("\n")
    return

def print_rolelist(playerlist):
    for player in playerlist:
        print("Player {}: {} {}".format(player.id,player.alignment,player.role))
    return

def cultcheck(playerlist): #after the CL dies, kill all the cultists
    numplayers = len(playerlist)
    #print_playerlist(playerlist)
    is_leader_alive = False

    for player in playerlist: #check if CL is alive
        if player.role == "cult leader":
            is_leader_alive = True

    if is_leader_alive == False: #if CL is dead, kill the cultists
        for player in playerlist:
            cultists = []
            if player.alignment == "cult":
                cultists.append(player)
            for cultist in cultists:
                playerlist.remove(cultist)

    return(playerlist)

def evaluate_victory(playerlist):
    number_of_players = len(playerlist)
    number_of_mafia = 0
    number_of_town = 0
    number_of_cult = 0
    number_of_sk = 0
    for player in playerlist:
        if player.alignment == "mafia":
            number_of_mafia += 1
        if player.alignment == "town":
            number_of_town += 1
        if player.alignment == "cult":
            number_of_cult += 1
        if player.role == "sk":
            number_of_sk += 1
    if number_of_sk == 1 and number_of_players == 1:
        return("sk win")
    if number_of_mafia > number_of_players/2:
        return("mafia win")
    if number_of_cult > number_of_players/2 and number_of_mafia == 0:
        return("cult win")
    if number_of_town == number_of_players:
        return("town win")
    else:
        return(0)

def playGame(total_players, total_doctors, total_vigs, total_mafia,total_cult,total_sk):

    playerlist = []
    #role assignment
    for id in range(1,total_mafia+1): #generates scum
        playerlist.append(player_object(id,"mafia","goon",False))
#note: a cute thing about the range function is that range(n,n) doesn't contain anything, and range (n,n+1) only contains 1 number (n), so if (for ex.) total_doctors = 0, no doctors will be generated
    for id in range(total_mafia+1,total_mafia+total_doctors+1): #generates doctor(s)
        playerlist.append(player_object(id,"town","doctor",False))

    for id in range(total_mafia+total_doctors+1,total_mafia+total_doctors+total_vigs+1): #generates vigs
        playerlist.append(player_object(id,"town","vig",False))

    for id in range(total_mafia+total_doctors+total_vigs+1,total_mafia+total_doctors+total_vigs+total_cult+1): #generates cult leader
        playerlist.append(player_object(id,"cult","cult leader",False))

    for id in range(total_mafia+total_doctors+total_vigs+total_cult+1,total_mafia+total_doctors+total_vigs+total_cult+total_sk+1): #generate SK
        playerlist.append(player_object(id,"neutral","sk",False))

    for id in range(total_mafia+total_doctors+total_vigs+total_cult+total_sk+1,total_players+1): #generates VTs
        playerlist.append(player_object(id,"town","vt",False))

    print_rolelist(playerlist)

    for cycle in range(1,100): #the game starts
        x = evaluate_victory(playerlist) #check if someone won
        if(x!=0): #evaluate_victory returns 0 if no one has won the game
            print(evaluate_victory(playerlist))
            return(result_object(x,cycle))

        print("\nIt is now day {}.".format(cycle))
        #lynch
        lynched = sample(playerlist,1)[0]
        playerlist.remove(lynched)
        print("Player {} was lynched.".format(lynched.id))

        playerlist = cultcheck(playerlist)
    #    print_playerlist(playerlist)

        x = evaluate_victory(playerlist) #evaluate victory
        if(x!=0):
            print(evaluate_victory(playerlist))
            return(result_object(x,cycle))

        print("It is now night {}.".format(cycle))

        #doctors select who to heal
        for player in playerlist:
            if player.role == "doctor":
                candidates = []
                for candidate in playerlist:
                    if candidate.id != player.id:
                        candidates.append(candidate)
                target = sample(candidates,1)[0]
                for player_j in playerlist:
                    if target.id == player_j.id:
                        player_j.bp_status = True
                        print("Player {} bp is set to {} tonight.".format(player_j.id,player_j.bp_status))

#mafia select who to kill
        if getPlayersByAlignment(playerlist,"mafia") != []:
            target = sample(getPlayersByNotAlignment(playerlist,"mafia"),1)[0] #select a random townie
            if target.bp_status != True:
                playerlist.remove(player)
                print("Player {} was killed by the mafia.".format(player.id))
            if target.bp_status == True:
                print("Mafia kill BLOCKED.")

#vig kill(s)
        for player in playerlist:
            if player.role == "vig" and player.shots > 0:
                player.shots =-1
                candidates = []
                for candidate in playerlist:
                    if candidate.id != player.id:
                        candidates.append(candidate)
                target = sample(candidates,1)[0]
                #kill target if not bp
                if target.bp_status == False:
                    playerlist.remove(target)
                    print("Player {} was killed by a vig.".format(player.id))
                else:
                    print("Vig kill BLOCKED.")
#sk kill
        for player in playerlist:
            if player.role == "sk":
                candidates = []
                for candidate in playerlist:
                    if candidate.id != player.id:
                        candidates.append(candidate)
                target = sample(candidates,1)[0]
            #kill target
                if target.bp_status == False:
                    playerlist.remove(target)
                    print("Player {} was killed by an sk.".format(player.id))
                else:
                    print("Sk kill BLOCKED.")
        playerlist = cultcheck(playerlist)
    #recruits
        for player in playerlist:
            if player.role == "cult leader":
                candidates = getPlayersByNotAlignment(playerlist,"cult")
                target = sample(candidates,1)[0]
                if target.alignment == "town":
                    target.alignment = "cult"
                    target.role = "cult follower"
                    print("Player {} was recruited.".format(target.id))
        #reset all bp to False
        for player in playerlist:
            player.bp_status = False

def run_batch(total_players,total_doctors,total_vigs,total_mafia,total_cult,total_sk): #run a batch of games under identical conditions, and print the statistics
    alignments = []
    results = []
    for i in range(1,2001):
        if(i%1000 == 0):
            print("Game {}...".format(i))
        blockPrint()
        result = playGame(total_players,total_doctors,total_vigs,total_mafia,total_cult,total_sk)
        enablePrint()
        results.append(result)
        if result.winner not in alignments:
            alignments.append(result.winner)

    #for alignment in alignments:
        #print("{} percentage: {}".format(alignment,results.count(alignment)/len(results)))
    print("Ran Batch. Setup: {} players, {} mafia, {} cult leaders, {} doctors, {} vigs, {} SKs. Results:".format(total_players,total_mafia,total_cult,total_doctors,total_vigs,total_sk))

    for alignment in alignments:
        count = 0
        for result in results:
            if alignment == result.winner:
                count +=1
        print("{}: {}".format(alignment,count/len(results)))
    s = 0
    for result in results:
        s = s+result.length
    print("Average game length: {} cycles".format(s/len(results)))
    return(results)
    #printHistogram(25,results)

#results = run_batch(13,1,1,2,0)
results = run_batch(total_players = 17,total_doctors=3,total_vigs = 2,total_mafia = 3,total_cult = 1,total_cult = 1)
#playGame(3,0,0,0,0,1)
