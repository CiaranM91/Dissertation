import json
import copy
import random
from random import randint


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
highscore = 0
random.seed(5)

def searchMoves(board):
    possible_moves = []
    # Return True if the board is in a state where a matching
    # move can be made on it. Otherwise return False.

    # The patterns in oneOffPatterns represent gems that are configured
    # in a way where it only takes one move to make a triplet.
    oneOffPatterns = (
        ((0, 1), (1, 0), (2, 0), (0, 0), (0, 1)),
        ((0, 1), (1, 1), (2, 0), (2, 0), (2, 1)),
        ((0, 0), (1, 1), (2, 0), (1, 0), (1, 1)),
        ((0, 1), (1, 0), (2, 1), (1, 0), (1, 1)),
        ((0, 0), (1, 0), (2, 1), (2, 0), (2, 1)),
        ((0, 0), (1, 1), (2, 1), (0, 0), (0, 1)),
        ((0, 0), (0, 2), (0, 3), (0, 0), (0, 1)),
        ((0, 0), (0, 1), (0, 3), (0, 2), (0, 3)),
    )

    # The x and y variables iterate over each space on the board.
    # If we use + to represent the currently iterated space on the
    # board, then this pattern: ((0,1), (1,0), (2,0))refers to identical
    # gems being set up like this:
    #
    #     ABxC
    #     xB
    #     xC
    #
    # That is, gem A is offset from the + by (0,1), gem B is offset
    # by (1,0), and gem C is offset by (2,0). In this case, gem A can
    # be swapped to the left to form a vertical three-in-a-row triplet.
    #
    # There are eight possible ways for the gems to be one move
    # away from forming a triple, hence oneOffPattern has 8 patterns.

    for x in range(ROWS):
        for y in range(COLUMNS):
            for pat in oneOffPatterns:
                # check each possible pattern of "match in next move" to
                # see if a possible move can be made.
                if (
                    getGemAt(board, x + pat[0][0], y + pat[0][1])
                    == getGemAt(board, x + pat[1][0], y + pat[1][1])
                    == getGemAt(board, x + pat[2][0], y + pat[2][1])
                    != None
                ) :
                    gem1 = [x+pat[3][0], y+pat[3][1]]
                    gem2 = [x+pat[4][0], y+pat[4][1]]
                    move = [tuple(gem1), tuple(gem2)]
                    possible_moves.append(move)

                elif (
                    getGemAt(board, x + pat[0][1], y + pat[0][0])
                    == getGemAt(board, x + pat[1][1], y + pat[1][0])
                    == getGemAt(board, x + pat[2][1], y + pat[2][0])
                    != None
                ):
                    gem1 = [x+pat[3][1], y+pat[3][0]]
                    gem2 = [x+pat[4][1], y+pat[4][0]]
                    move = [tuple(gem1), tuple(gem2)]
                    possible_moves.append(move)

    return possible_moves


def canMakeMove(board):
    # Return True if the board is in a state where a matching
    # move can be made on it. Otherwise return False.

    # The patterns in oneOffPatterns represent gems that are configured
    # in a way where it only takes one move to make a triplet.
    oneOffPatterns = (
        ((0, 1), (1, 0), (2, 0)),
        ((0, 1), (1, 1), (2, 0)),
        ((0, 0), (1, 1), (2, 0)),
        ((0, 1), (1, 0), (2, 1)),
        ((0, 0), (1, 0), (2, 1)),
        ((0, 0), (1, 1), (2, 1)),
        ((0, 0), (0, 2), (0, 3)),
        ((0, 0), (0, 1), (0, 3)),
    )

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

    for x in range(ROWS):
        for y in range(COLUMNS):
            for pat in oneOffPatterns:
                # check each possible pattern of "match in next move" to
                # see if a possible move can be made.
                if (
                    getGemAt(board, x + pat[0][0], y + pat[0][1])
                    == getGemAt(board, x + pat[1][0], y + pat[1][1])
                    == getGemAt(board, x + pat[2][0], y + pat[2][1])
                    != None
                ) or (
                    getGemAt(board, x + pat[0][1], y + pat[0][0])
                    == getGemAt(board, x + pat[1][1], y + pat[1][0])
                    == getGemAt(board, x + pat[2][1], y + pat[2][0])
                    != None
                ):
                    return True  # return True the first time you find a pattern
    return False


def getNewGems(board):
    # count the number of empty spaces in each column on the board
    for x in range(ROWS):
        for y in range(COLUMNS - 1, -1, -1):  # start from bottom, going up
            if board[x][y] == EMPTYSPACE:
                possibleGems = list(range(1, NUMBEROFGEMS))
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
    
    # Setting all elements to 1 initially
    board = [[1] * COLUMNS for i in range(ROWS)]
    # Creating a random board with zero matches to begin
    for x in range(ROWS):
        for y in range(COLUMNS):
            board[x][y] = randint(1, NUMBEROFGEMS)
            while (x >= 0 and board[x][y] == board[x - 1][y]) or (
                x >= 0 and board[x][y] == board[x][y - 1]
            ):
                board[x][y] = randint(1, NUMBEROFGEMS)
    return board


def getGemAt(board, x, y):
    if x < 0 or y < 0 or x >= ROWS or y >= COLUMNS:
        return None
    else:
        return int(board[x][y])


def findMatchingGems(board):
    gemsToRemove = (
        []
    )  # a list of lists of gems in matching triplets that should be removed

    # loop through each space, checking for 3 adjacent identical gems
    for x in range(ROWS):
        for y in range(COLUMNS):
            # look for horizontal matches
            if (
                getGemAt(board, x, y)
                == getGemAt(board, x + 1, y)
                == getGemAt(board, x + 2, y)
                and getGemAt(board, x, y) != EMPTYSPACE
            ):
                targetGem = board[x][y]
                offset = 0
                removeSet = []
                while getGemAt(board, x + offset, y) == targetGem:
                    # keep checking if there's more than 3 gems in a row
                    removeSet.append((x + offset, y))
                    offset += 1
                gemsToRemove.append(removeSet)
            # look for vertical matches
            if (
                getGemAt(board, x, y)
                == getGemAt(board, x, y + 1)
                == getGemAt(board, x, y + 2)
                and getGemAt(board, x, y) != EMPTYSPACE
            ):
                targetGem = board[x][y]
                offset = 0
                removeSet = []
                while getGemAt(board, x, y + offset) == targetGem:
                    # keep checking, in case there's more than 3 gems in a row
                    removeSet.append((x, y + offset))
                    offset += 1
                gemsToRemove.append(removeSet)
    return gemsToRemove


board = buildBoard()


def game(board, gems):
    if canMakeMove == False:
            board = buildBoard()
            score = 0

    gem1 = gems[0]
    gem2 = gems[1]
    score = 0

    firstGem = int(getGemAt(board, gem1[0], gem1[1]))
    secondGem = int(getGemAt(board, gem2[0], gem2[1]))
    # swapping gems

    board[gem1[0]][gem1[1]] = secondGem
    board[gem2[0]][gem2[1]] = firstGem

    matchedGems = findMatchingGems(board)
    
    while matchedGems != []:
        scoreAdd = 0
        # Remove matched gems, then pull down the board.
        for gemSet in matchedGems:
            scoreAdd += 10 + (len(gemSet) - 3) * 10
            for gem in gemSet:
                board[gem[0]][gem[1]] = EMPTYSPACE
        score += scoreAdd
        # check for new matches
        matchedGems = findMatchingGems(board)

        # pulling down all gems
        board = pullDownAllGems(board)
        # fill new gems
        board = getNewGems(board)
        # again check for matches
        matchedGems = findMatchingGems(board)
        
        if canMakeMove == False:
            board = buildBoard()
            score = 0

        state = [board, score]
        return state


def treeSearch(board, numIterations, depthOfSearch):
    randomGen = random.Random()
    possibleMoves = searchMoves(board)
    averageCount = []

    for _ in range(len(possibleMoves)):
        averageCount.append([0, 0])

    for _ in range(numIterations):
        moveindex = randomGen.randint(0, len(possibleMoves)-1)
        boardCopy = copy.deepcopy(board)

        scorecount = 0
        averageCount[moveindex][0] += 1
        for _ in range(depthOfSearch):

            state = takeRandomMove(boardCopy)
            boardCopy = state[0]
            scorecount += state[1]
            averageCount[moveindex][1] += scorecount

    scoredmoves = []

    for x in range(len(possibleMoves)):
        score = averageCount[x][1]
        if(averageCount[x][0] > 0):
            score = score/(0.0+averageCount[moveindex][0])
            scoredmoves.append((possibleMoves[x], score))

        # Randomise the possible moves list
    randomGen.shuffle(scoredmoves)
      # Sort the possible moves list
    scoredmoves.sort(key=lambda x: x[1])
      # Return the move at the top or bottom, whichever has the highest score associated with it
    bestMove = scoredmoves[-1]
    print(scoredmoves)
    print(averageCount)
    return bestMove


def takeRandomMove(board):
    randomGen = random.Random()
    newBoard = copy.deepcopy(board)
    possibleMoves = searchMoves(board)
    print(possibleMoves)
    while possibleMoves == []:
        newBoard = buildBoard()
        possibleMoves = searchMoves(newBoard)
    #print('moves :',possibleMoves)
    move = randomGen.choice(possibleMoves)
    
    #print('selected',move)
    state = game(newBoard, move)
    
    return state

print(treeSearch(board, 50, 5))