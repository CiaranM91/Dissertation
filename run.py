from flask import Flask, request, jsonify, render_template, url_for
import json
import copy 
import random
from random import randint
import os.path
app = Flask(__name__)

COLUMNS = 8
ROWS = 8
NUMBEROFGEMS = 7
EMPTYSPACE = -1
firstGemX = None
firstGemY = None
clickX = None
clickY = None
selectedgem = None   
score = 0  

def canMakeMove(board):
    # Return True if the board is in a state where a matching
    # move can be made on it. Otherwise return False.

    # The patterns in oneOffPatterns represent gems that are configured
    # in a way where it only takes one move to make a triplet.
    oneOffPatterns = (((0,1), (1,0), (2,0)),
                      ((0,1), (1,1), (2,0)),
                      ((0,0), (1,1), (2,0)),
                      ((0,1), (1,0), (2,1)),
                      ((0,0), (1,0), (2,1)),
                      ((0,0), (1,1), (2,1)),
                      ((0,0), (0,2), (0,3)),
                      ((0,0), (0,1), (0,3)))

    # The x and y variables iterate over each space on the board.
    # If we use + to represent the currently iterated space on the
    # board, then this pattern: ((0,1), (1,0), (2,0))refers to identical
    # gems being set up like this:
    #
    #     +A
    #     B
    #     C
    #
    # That is, gem A is offset from the + by (0,1), gem B is offset
    # by (1,0), and gem C is offset by (2,0). In this case, gem A can
    # be swapped to the left to form a vertical three-in-a-row triplet.
    #
    # There are eight possible ways for the gems to be one move
    # away from forming a triple, hence oneOffPattern has 8 patterns.

    for x in range(COLUMNS):
        for y in range(ROWS):
            for pat in oneOffPatterns:
                # check each possible pattern of "match in next move" to
                # see if a possible move can be made.
                if (getGemAt(board, x+pat[0][0], y+pat[0][1]) == \
                    getGemAt(board, x+pat[1][0], y+pat[1][1]) == \
                    getGemAt(board, x+pat[2][0], y+pat[2][1]) != None) or \
                   (getGemAt(board, x+pat[0][1], y+pat[0][0]) == \
                    getGemAt(board, x+pat[1][1], y+pat[1][0]) == \
                    getGemAt(board, x+pat[2][1], y+pat[2][0]) != None):
                    return True # return True the first time you find a pattern
    return False


def getNewGems(board):
    # count the number of empty spaces in each column on the board
    for x in range(COLUMNS):
        for y in range(ROWS-1, -1, -1): # start from bottom, going up
            if board[x][y] == EMPTYSPACE:
                possibleGems = list(range(1,NUMBEROFGEMS))
                for offsetX, offsetY in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    # Narrow down the possible gems we should put in the
                    # blank space so we don't end up putting an two of
                    # the same gems next to each other when they drop.
                    neighborGem = getGemAt(board, x + offsetX, y + offsetY)
                    if neighborGem != None and neighborGem in possibleGems:
                        possibleGems.remove(neighborGem)

                newGem = random.choice(possibleGems)
                board[x][y] = newGem
                
    return board

def pullDownAllGems(board):
    # pulls down gems on the board to the bottom to fill in any gaps
    for x in range(ROWS):
        gemsInColumn = []
        for y in range(COLUMNS):
            if board[x][y] != EMPTYSPACE:
                gemsInColumn.append(board[x][y])
        board[x] = ([EMPTYSPACE] * (ROWS - len(gemsInColumn))) + gemsInColumn
    return board



def checkGemSelection(firstGemX, firstGemY, currentGemX, currentGemY):
    
    if firstGemX == currentGemX + 1 and firstGemY == currentGemY:
        return firstGemX, firstGemY, currentGemX, currentGemY
    elif firstGemX == currentGemX - 1 and firstGemY == currentGemY:
        return firstGemX, firstGemY, currentGemX, currentGemY
    elif firstGemY == currentGemY + 1 and firstGemX == currentGemX:
        return firstGemX, firstGemY, currentGemX, currentGemY
    elif firstGemY == currentGemY - 1 and firstGemX == currentGemX:
       return firstGemX, firstGemY, currentGemX, currentGemY
    else:
        # These gems are not adjacent and can't be swapped.
        return None


def buildBoard():
    #Setting all elements to 1 initially
    board = [[1]*COLUMNS for i in range(ROWS)]
    #Creating a random board with zero matches to begin
    for r in range(ROWS):
        for c in range(COLUMNS):
            board[r][c] = randint(1, NUMBEROFGEMS)
            while (r>0 and board[r][c] == board[r - 1][c]) or (c > 0 and board[r][c] == board[r][c - 1]):
                board[r][c] = randint(1, NUMBEROFGEMS) 
    return board  

def getGemAt(board, x, y):
    if x < 0 or y < 0 or x >= COLUMNS or y >= ROWS:
        return None
    else:
        print('Gem at ',x,',',y,'is',board[x][y])
        return int(board[x][y])

def findMatchingGems(board):
    gemsToRemove = [] # a list of lists of gems in matching triplets that should be removed
    
    # loop through each space, checking for 3 adjacent identical gems
    for x in range(COLUMNS):
        for y in range(ROWS):
            # look for horizontal matches
            if getGemAt(board, x, y) == getGemAt(board, x + 1, y) == getGemAt(board, x + 2, y) and getGemAt(board, x, y) != EMPTYSPACE:
                targetGem = board[x][y]
                offset = 0
                removeSet = []
                while getGemAt(board, x + offset, y) == targetGem:
                    # keep checking if there's more than 3 gems in a row
                    removeSet.append((x + offset, y))
                    board[x + offset][y] = EMPTYSPACE
                    offset += 1
                gemsToRemove.append(removeSet)

            # look for vertical matches
            if getGemAt(board, x, y) == getGemAt(board, x, y + 1) == getGemAt(board, x, y + 2) and getGemAt(board, x, y) != EMPTYSPACE:
                targetGem = board[x][y]
                offset = 0
                removeSet = []
                while getGemAt(board, x, y + offset) == targetGem:
                    # keep checking, in case there's more than 3 gems in a row
                    removeSet.append((x, y + offset))
                    board[x][y + offset] = EMPTYSPACE
                    offset += 1
                gemsToRemove.append(removeSet)

    return gemsToRemove


board = buildBoard() 
@app.route('/')
def index():
    data = json.dumps(board)
    score = 0
    return render_template('index.html', data=data, score=score)



@app.route('/make_selection', methods=['GET', 'POST'])
def game():
    global score
    global board
    global firstGemX
    global firstGemY
    global clickX
    global clickY 
    if canMakeMove(board) == False:
        board = buildBoard()
        return json.dumps(board)
    i = request.args.get('i', type=int)
    j = request.args.get('j', type=int)
    
    clickX = j
    clickY = i
    selectedgem = int(getGemAt(board, clickX, clickY))
    
    if selectedgem == None and not firstGemX:
        print('Option 1')
        #if selected gem is not on board and no gem previously selected return the current board
        return json.dumps(board)

    elif selectedgem != None and firstGemX == None:
        print('Option 2')

        #if selected gem is valid and no gem currently selected
        #create new first selection and return both it and the board
        firstGemX = clickX
        firstGemY = clickY
        selectedgem = None
        final_value = json.dumps(board) + 'X'+str(firstGemY)+'X'+str(firstGemX)+'X'+str(score)
        
        return final_value

    elif selectedgem != None and firstGemX != None:
        print('Option 3')

        #if selected gem is valid and first selection made go into game mechanics
        if checkGemSelection(firstGemX, firstGemY, clickX, clickY) == None:
            print('Option 4')
            #if the selections are not next to each other return the board and unselect
            firstGemX, firstGemY = None, None
            selectedgem = None
            return json.dumps(board)+'X'+str(None)+'X'+str(None)+'X'+str(score)

        elif checkGemSelection(firstGemX, firstGemY, clickX, clickY) != None:
            print('Option 5')
            #if valid selection follow game engine
            #assigning gem valuies for swap
            print(firstGemX, firstGemY, clickX, clickY)
            firstGem = int(getGemAt(board, firstGemX, firstGemY))
            secondGem = int(getGemAt(board, clickX, clickY))
            #swapping gems
            print('Before swap', firstGem, secondGem)
            board[firstGemX][firstGemY] = secondGem
            board[clickX][clickY] = firstGem
            
            matchedGems = findMatchingGems(board)
            
            if matchedGems == []:
                print("Option 6")
                #if there are no matches swap back
                board[firstGemX][firstGemY] = firstGem
                board[clickX][clickY] = secondGem
                return json.dumps(board)+'X'+str(None)+'X'+str(None)+'X'+str(score)
            else:
                print('Option 7')
                print(matchedGems)
                while matchedGems != []:
                    scoreAdd = 0
                    # Remove matched gems, then pull down the board.
                    for gemSet in matchedGems:
                        scoreAdd += (10 + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            board[gem[0]][gem[1]] = EMPTYSPACE
                    score += scoreAdd
                    print('Before pulling down gems', board)
                    #pulling down all gems
                    board = pullDownAllGems(board)
                    print('After pulling gems',board)
                    
                    board = getNewGems(board)
                    print('With new gems', board)
                    firstGemX = None
                    firstGemY = None
                    selectedgem = None
                    if canMakeMove(board) == False:
                        board = buildBoard()

                    return json.dumps(board)+'X'+str(None)+'X'+str(None)+'X'+str(score)

               
            
        

if __name__ == "__main__":
    app.run(debug = True)       
   