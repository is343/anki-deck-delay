#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 22:24:56 2017

@author: Ivan


info on the anki directory: https://www.juliensobczak.com/tell/2016/12/26/anki-scripting.html
"""

import sqlite3
import shutil
import datetime
import time



# deck 1450345949539 == Korean; 1461588996278 == countries; 1462459650256 == states


def open_deck(deck='1450345949539'):
    '''
    str -> list (of tuples)
    searches for all the cards from a given deck and returns it
    '''
    c.execute("SELECT * FROM cards WHERE did= ?", (deck,))
    cardsFromDeck = c.fetchall()
    return cardsFromDeck


# for checking on if cards are due today
todayDate = datetime.date.today()
ankiCreateDate = datetime.date(2015, 4, 13)
difference = (todayDate - ankiCreateDate).days #stripping time from the datetime

def check_for_due(cards):
    '''
    list (of tuples) -> bool
    goes through a list of cards from a deck and
    varifies that something is due today
    '''
    # cards[[][8]] == due
    for card in cards:
        # if something's due today
        if card[8] <= difference - 1: # -1 to prevent delaying down to 0 cards
            return True
    return False


def how_many_days_to_delay(cards):
    '''
    list (of tuples) -> int
    goes through a list of cards from a deck and
    finds the max number of days it is behind
    '''
    delay_days = 0
    # cards[[][8]] == due
    for card in cards:
        # if something's due today
        comparison = card[8] <= difference - 1
        if card[8] <= difference - 1: # -1 to prevent delaying down to 0 cards
            days_behind = difference - 1 - card[8]
            if days_behind > delay_days:
                delay_days = days_behind
    return delay_days



def not_new_cards(cards):
    '''
    list (of tuples) -> list (of tuples)
    goes through a list of cards from a deck and
    removes any cards that have not been studied yet
    '''
    notNewCards = []
    # cards[[][6]] == type: 0=new, 1=learning, 2=due
    for card in cards:
        if card[6] == 0:
            continue
        notNewCards.append(card)
    return notNewCards


def delay(cards, days=1):
    '''
    list (of tuples), int -> list (of tuples)
    goes through the list of cards and delays them
    all by the given number of days
    '''
    # cards[[][0]] == (card) id
    # cards[[][8]] == due
    newList = []
    for card in cards:
        newList.append([card[0], (card[8] + days)])
    return newList


def update_database(cards):
    '''
    list -> ---
    goes through each card id and updates the
    database with the new due date
    '''
    # new indexes are [0] for id, and [1] for due date
    with conn:  # replaces the need for "conn.commit()" at the end of the program
        for card in cards:
            c.execute("""UPDATE cards SET due= ?
                      WHERE id= ?""", (card[1], card[0]))


def run_program(decks, delay_all=False):
    '''
    list -> ---
    goes through each deck from the chosen
    decks to delay and runs the steps for each deck
    '''
    for deckToRun in decks:
        deck = open_deck(deckToRun)
        cards = not_new_cards(deck)
        if check_for_due(cards):
            if delay_all:
                days_to_delay = how_many_days_to_delay(cards)
                print('Delayed cards for', days_to_delay, 'days')
                cards = delay(cards, days_to_delay)
            else:
                cards = delay(cards)
            update_database(cards)
            print('Cards in deck ' + str(deckToRun) + ' have been delayed.')
        else:
            print('No due cards in deck ' + str(deckToRun) + ' to delay')
        

def run(delay_all=False):
    '''
    main execution of the program to delay cards
    opens and closes the connection to the database
    '''
    # create backup of the collection before we edit anything
    shutil.copy(r'/home/pi/Documents/Anki/User 1/collection.anki2', r'/home/pi/Documents/Anki/User 1/collection_backup.anki2')

    # making these global so they can be within other function scopes
    global conn
    conn = sqlite3.connect(r'/home/pi/Documents/Anki/User 1/collection.anki2')
    global c
    c = conn.cursor()


    # deck 1450345949539 == Korean; 1461588996278 == countries; 1462459650256 == states
    run_program([1450345949539, 1461588996278, 1462459650256], delay_all)
    conn.close()
    print('Process completed.')




#get reset time to compare against
resetTime = datetime.datetime(2015, 5, 8, 5, 0, 0)


def getting_time():
    while datetime.datetime.now().hour != resetTime.hour:
        print("current hour is:", datetime.datetime.now().hour, ".. waiting 30 minutes...")
        time.sleep(1800) # pausing for 30 mins to check again 
    run()
    print("Sleeping for 23 hours and 20 minutes..")
    time.sleep(84000)


print("Please close Anki before choosing an option.")
print('Press 1 to dalay cards by one day')
print('Press 2 to delay cards by all days they are behind')
option = input('Press 3 to wait and delay cards by one day at night').lower()

while True:
    if option == '3':
        getting_time()
    elif option == '1':
        run()
        break
    elif option == '2':
        run(True)
        break
    else:
        print('Press 1 to dalay cards by one day')
        print('Press 2 to delay cards by all days they are behind')
        option = input('Press 3 to wait and delay cards by one day at night').lower()

    

