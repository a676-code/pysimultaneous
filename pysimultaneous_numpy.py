# pysimultaneous_numpy.py
# Author: Andrew Lounsbury
# Date: 3/17/24
# Description: a class for handling simultaneous games with n players, n >= 2. Payoffs for each player are stored in their own individual numpy array. 
import numpy as np

class Player:
    numStrats = -1
    rationality = -1
    
    def __init__(self,numStrats = 2, rationality = 0):
        self.numStrats = numStrats
        self.rationality = rationality

class simGame:    
    kMatrix = []
    impartial = False
    kOutcomes = [] # n-tuples that appear in kMatrix; won't be all of them
    kStrategies = [[] for i in range(4)] # 2D matrix containing the strategies each player would play for k-levels 0, 1, 2, 3
    mixedEquilibria = []
    numPlayers = -1
    payoffMatrix = [] # numPlayers long, contains the players' individual payoff matrices
    players = []
    pureEquilibria = []
    rationalityProbabilities = [0.0 for i in range(4)] # probability a player is L_i, i = 0, 1, 2, 3
    strategyNames = []
    
    def __init__(self, numPlayers = 2):
        # Creating players
        numStrats = [2 for x in range(numPlayers)]
        rationalities = [0 for x in range(numPlayers)]
        self.players = [Player(numStrats[x], rationalities[0]) for x in range(numPlayers)]
        
        # Creating kStrategies' 4 arrays of lists of size numPlayers and setting rationalityProbabilities
        for r in range(4):
            # resizing self.kStrategies[r]
            if numPlayers > len(self.kStrategies[r]):
                self.kStrategies[r] += [None] * (numPlayers - len(self.kStrategies[r]))
            else:
                self.kStrategies[r] = self.kStrategies[r][:numPlayers]
            self.rationalityProbabilities[r] = 0.0
        
        # Initializing strategy names
        if self.players[0].numStrats < 3:
            self.strategyNames.append(["U", "D"])
        else:
            self.strategyNames.append(["U"] + ["M" + str(i) for i in range(1, self.players[0].numStrats)] + ["D"])
        if self.players[1].numStrats < 3:
            self.strategyNames.append(["L", "R"])
        else:
            self.strategyNames.append(["L"] + ["C" + str(i) for i in range(self.players[0].numStrats)] + ["R"])
        for x in range(2, self.numPlayers):
            if self.players[x].numStrats < 3:
                self.strategyNames.append(["L(" + str(x) + ")", "R(" + str(x) + ")"])
            else: 
                self.strategyNames.append(["L(" + str(x) + ")"] + ["C(" + str(x) + ", " + str(i) + ")" for i in range(self.players[0].numStrats)] + ["R(" + str(x) + ")"])
        
        self.numPlayers = numPlayers
        self.payoffMatrix = []
        self.impartial = False
        
        # Creating dimensions for payoff matrix
        if self.numPlayers < 3:
            dimensions = tuple([self.players[x].numStrats for x in range(self.numPlayers)])
        else:
            product = 1
            for x in range(2, self.numPlayers):
                product *= self.players[x].numStrats
            dimensions = tuple([product] + [self.players[x].numStrats for x in range(2)])
            
        # Appending one matrix of payoffs for each player
        for x in range(self.numPlayers):
            self.payoffMatrix.append(np.zeros(dimensions))
        return
    
    def computeImpartiality(self):
        """ Checks if players 2,...,numPlayers have the same number of strategies as player 1? 
        """
        num = self.players[0].numStrats
        for x in range(1, self.numPlayers):
            if self.players[x].numStrats != num:
                self.impartial = False
                return
        impartial = True
    
    def enterPayoffs(self, payoffs = np.array([
        [[[0, 0], [0, 0]], [[0, 0], [0, 0]]], 
        [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
        ])):
        """Enters the payoffs into the payoff matrix. 

        Args:
            payoffs (numpy array, optional): the payoffs to be entered. Defaults to np.array([[[[0, 0], [0, 0]], [[0, 0], [0, 0]]], [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]]).
        """
        self.payoffMatrix = []
        for ar in payoffs:
            self.payoffMatrix.append(ar)
    
    def isBestResponse(self, profile):
        """Checks whether p1Strat and p2Strat are best responses relative to each other

        Args:
            p1Strat (int): p1's strategy
            p2Strat (int): p2's strategy
        """
        br = [True for x in range(self.numPlayers)]
        
        if self.numPlayers < 3:
            for i in range(self.players[0].numStrats):
                if self.payoffMatrix[0][profile[0]][profile[1]] < self.payoffMatrix[0][i][profile[1]]:
                    br[0] = False
            for j in range(self.players[1].numStrats):
                if self.payoffMatrix[1][profile[0]][profile[1]] < self.payoffMatrix[1][profile[0]][j]:
                    br[1] = False
        else:
            for x in range(self.numPlayers):
                if x < 2:
                    for i in range(self.players[0].numStrats):
                        if self.payoffMatrix[0][self.hash(profile)][profile[0]][profile[1]] < self.payoffMatrix[0][self.hash(profile)][i][profile[1]]:
                            br[0] = False
                    for j in range(self.players[1].numStrats):
                        if self.payoffMatrix[1][self.hash(profile)][profile[0]][profile[1]] < self.payoffMatrix[1][self.hash(profile)][profile[0]][j]:
                            br[1] = False
                else:
                    for m in range(self.payoffMatrix[0].shape[0]):
                        compProfile = profile # "compare profile"
                        compProfile[x] = m
                        if self.payoffMatrix[x][self.hash(profile)][profile[0]][profile[1]] < self.payoffMatrix[x][self.hash(compProfile)][profile[1]][profile[2]]:
                            br[x] = False
        return br
                        
    def hash(self, profile):
        """Converts a sequence of strategies into the index in a stack of payoff arrays that correspond to that sequence

        Args:
            profile (list): strategy profile (indices)

        Returns:
            int: the desired index
        """
        self.computeImpartiality() # ? 
        
        # c_2 + sum_{x = 3}^{nP - 1} (nS)^x * c_x
        num = 0 # return 0 if numPlayers < 2
        if self.numPlayers > 2:
            num = profile[2]
        if self.impartial:
            for x in range(3, self.numPlayers):
                if profile.at(x) > 0:
                    num += self.players[0] ** (x - 2) * self.profile[x]
        else: # c_2 + sum_{x=3}^{nP} nS_2 *...* nS_{x-1} * c_x
            if self.numPlayers > 3:
                product = 0
                for x in range(3, self.numPlayers):
                    product = 1
                    if profile[x] > 0:
                        for y in range(2, x - 1):
                            product *= self.players[y].numStrats
                            
                        num += product * profile[x]
        return num
    
    def print(self):
        """Prints the payoff matrix
        """
        for x in range(self.numPlayers):
            print(self.payoffMatrix[x])
            print()

    def readFromFile(self, fileName):
        addMoreOutcomesPast2 = False # kMatrix
        nP = -1 # numPlayers
        nS = -1 # numStrats
        r = -1 # rationality
        oldNumPlayers = -1
        oldNumStrats = [-1 for i in range(self.numPlayers)]
        oldSize = -1
        curList = []
        
        with open(fileName, 'r') as file:
            if file.readline().strip() == "together": 
                oldNumPlayers = self.numPlayers
                
                for x in range(self.numPlayers):
                    oldNumStrats[x] = self.players[x].numStrats
                    
                oldSize = len(self.payoffMatrix)
                
                # reading numPlayers
                nP = file.readline()
                self.numPlayers = int(nP)
                
                # reading numStrats for old players
                if oldNumPlayers <= self.numPlayers:
                    nS = file.readline().split(" ")
                    for n in nS:
                        n = n.rstrip()
                    # Getting rationalities
                    rats = file.readline().split(" ")
                    for rat in rats:
                        rat = rat.rstrip()
                                
                    for x in range(oldNumPlayers):
                        self.players[x].numStrats = int(nS[x])
                        self.players[x].rationality = int(rats[x])
                else:
                    nS = file.readline().split(" ")
                    for n in nS:
                        n = int(n.rstrip())
                    # Getting rationalities
                    rats = file.readline.split(" ")
                    for rat in rats:
                        rat = int(rat.rstrip())
                    
                    for x in range(numPlayers):
                        self.players[x].numStrats = int(nS[x])
                        self.players[x].rationality = rats[x]
                
                """
                add new players if there are more,
                resizing payoffMatrix and kMatrix,
                increase the size of kStrategy lists 
                """
                if oldNumPlayers != self.numPlayers:
                    if oldNumPLayers < numPlayers:
                        addMoreOutcomesPast2 = True
                    # Create new players and read rest of numStrats
                    for x in range(oldNumPlayers, self.numPlayers):
                        p = Player(int(nS[x]), rats[x])
                        players.append(p)
                        
                # FIXME
                # new matrices added to the end
                size = 1
                if self.numPlayers > 2:
                    for x in range(2, self.numPlayers):
                        size *= self.players[x].numStrats
                if size > self.payoffMatrix[0].shape[0]:
                    self.payoffMatrix += [None] * (size - len(self.payoffMatrix))
                else:
                    self.payoffMatrix = self.payoffMatrix[:size]
                
                size = 1
                if self.numPlayers > 2:
                    size = 4 ** (self.numPlayers - 2)
                if size > len(self.kMatrix):
                    self.kMatrix += [None] * (size - len(self.kMatrix))
                else:
                    self.kMatrix = self.kMatrix[:size]
                
                # FIXME
                # creating/deleting entries and reading values
                for m in range(len(self.payoffMatrix)):
                    # resizing p1
                    if self.players[0].numStrats > len(self.payoffMatrix[m]):
                        self.payoffMatrix[m] += [None] * (self.players[0].numStrats - len(self.payoffMatrix[m]))
                    else:
                        self.payoffMatrix[m] = self.payoffMatrix[m][:self.players[0].numStrats]
                    for i in range(self.players[0].numStrats):
                        # resizing p2
                        if self.players[1].numStrats > len(self.payoffMatrix[m][i]):
                            self.payoffMatrix[m][i] += [None] * (self.players[1].numStrats - len(self.payoffMatrix[m][i]))
                        else:
                            self.payoffMatrix[m][i] = self.payoffMatrix[m][i][:self.players[1].numStrats]
                        # Reading in the next row of payoffs
                        payoffs = file.readline().split(" ")
                        for payoff in payoffs:
                            payoff = float(payoff.rstrip())
                        groupedPayoffs = [payoffs[i:i + self.numPlayers] for i in range(0, len(payoffs), self.numPlayers)]
                        
                        for j in range(self.players[1].numStrats):
                            # Create new list if needed
                            if not self.payoffMatrix[m][i][j]:
                                newList = ListNode(0, False)
                                self.payoffMatrix[m][i][j] = newList
                            curList = self.payoffMatrix[m][i][j]
                            while curList.sizeOfLL() > self.numPlayers:
                                # Deleting
                                curList.removeAtIndex(curList.sizeOfLL() - 1)
                            
                            for x in range(self.numPlayers):
                                if m < oldSize and x < oldNumPlayers and i < oldNumStrats[0] and j < oldNumStrats[1]: # old matrix, old outcome, old payoff
                                    curList.updateListNode(int(groupedPayoffs[j][x]), x) # inserting payoff value
                                else: # Everything is new
                                    # Adding
                                    curList.appendNode(int(payoffs[x]), False)
                
                if addMoreOutcomesPast2:
                    for m in range((len(self.kMatrix))):
                        if 4 > len(self.kMatrix[m]):
                            self.kMatrix[m] += [None] * (4 - len(self.kMatrix[m]))
                        else:
                            self.kMatrix[m] = self.kMatrix[m][:4]
                        for i in range(4):
                            if 4 > len(self.kMatrix[m]):
                                self.kMatrix[m][i] += [None] * (4 - len(self.kMatrix[m][i]))
                            else:
                                self.kMatrix[m][i] = self.kMatrix[m][i][:4]
                            for j in range(4):
                                myList = [-1 for l in range(self.numPlayers)]
                                kMatrix[m][i][j] = myList
            else: # separate
                return
        print("Done reading from " + fileName)

    def removeStrategy(self, player, s):
        """Removes strategy s from player in the payoff matrix

        Args:
            player (int): index of the player
            s (int): index of the strategy
        """
        # FIXME
        if player == 0: # player is player 1
            for x in range(self.numPlayers):
                # deleting s-th row from every x-th matrix
                self.payoffMatrix[x] = np.delete(self.payoffMatrix[x], s, axis=0)
        elif player == 1: # player is player 2
            for x in range(self.numPlayers):
                # deleting s-th column from every x-th matrix
                self.payoffMatrix[x] = np.delete(self.payoffMatrix[x], s, axis=1)
        else: # player > 1
            numErased = 0
            product = 1
            m = 0
            end = [0 for x in range(self.numPlayers)]
            for y in range(self.numPlayers):
                if y != player:
                    end[y] = self.players[y].numStrats
                else:
                    end[y] = s
            
            profile = [0 for i in range(self.numPlayers)]
            while m < self.hash(end):
                profile = unhash(m)
                profile[player] = s # at start of section
                num = 1
                if player < self.numPlayers - 1:
                    for y in range(2, self.numPlayers):
                        if y != player:
                            num *= self.players[y].numStrats
                elif player == self.numPlayers - 1 and self.numPlayers > 3:
                    num = self.players[x].numStrats
                else:
                    print("Error: unexpected values for player and numPlayers")
                
                while numErased < num:
                    del self.payoffMatrix[hash(profile)]
                    numErased += 1
                    
                    # last player's matrices are all lined up; others' must be found
                    if x < self.numPlayers - 1:
                        print()
                        if profile[2] > 0: # simply decrement first number
                            profile[2] -= 1
                        else: # go through each succeeding number
                            y = 2
                            foundNonzero = False
                            while True:
                                profile[y] = self.players[y].numStrats - 1
                                # not last number and next number is nonzero
                                if y != self.numPlayers - 1 and profile[y + 1] != 0:
                                    profile[y + 1] -= 1
                                    foundNonzero = True
                                elif y != self.numPlayers - 1 and profile[y + 1] == 0:
                                    profile[y] = self.players[y].numStrats - 1
                                elif y == self.numPlayers - 1:
                                    profile[y] -= 1
                                y += 1
                                
                                if y >= self.numPlayers or profile[y] != 0 or foundNonzero:
                                    break
                                
                        incremented = False
                        y = 2
                        while not incremented and y < self.numPlayers:
                            if y != x:
                                if profile[y] != self.players[y].numStrats - 1:
                                    profile[y] += 1
                                    incremented = True
                            y += 1
                if x > 2 and x < self.numPlayers - 1 and product == 1:
                    for y in range(2, player - 1):
                        product *= self.players[y].numStrats
                m += product # move to the next one, which is the first in the next section
                
        # Decrement the number of strategies for player
        self.players[player].numStrats -= 1
        
        if self.impartial:
            impartial = False
        return
    
    def saveToFile(self, fileName, together=True):
        """Saves the data of a game to a text file

        Args:
            fileName (str): the file name
        """
        with open(fileName, 'w') as file:
            if together:
                file.write("together\n")
                file.write(str(self.numPlayers) + "\n")
                
                # write numStrats to file
                for x in range(self.numPlayers):
                    file.write(str(self.players[x].numStrats))
                    if x < self.numPlayers - 1:
                        file.write(" ")
                file.write("\n")
                
                # write rationalities to the file
                for x in range(self.numPlayers):
                    file.write(str(self.players[x].rationality))
                    if x < self.numPlayers - 1:
                        file.write(" ")
                file.write("\n")

                # write payoffMatrix to file
                if self.numPlayers < 3:
                    for i in range(self.players[0].numStrats):
                        for j in range(self.players[1].numStrats):
                            for x in range(self.numPlayers):
                                file.write(str(self.payoffMatrix[x][i][j]))
                                if x < self.numPlayers - 1:
                                    file.write(" ")
                            if j < self.players[1].numStrats - 1:
                                file.write(" ")
                        if i < self.players[0].numStrats - 1:
                            file.write("\n")
                else: 
                    for m in range(self.payoffMatrix[0].shape[0]):
                        for i in range(self.players[0].numStrats):
                            for j in range(self.players[1].numStrats):
                                for x in range(self.numPlayers):
                                    file.write(str(self.payoffMatrix[x][m][i][j]))
                                    if x < self.numPlayers - 1:
                                        file.write(" ")
                                if j < self.players[1].numStrats - 1:
                                    file.write(" ")
                            if i < self.players[0].numStrats - 1:
                                file.write("\n")
                        if m < self.payoffMatrix[0].shape[0] - 1:
                            file.write("\n\n")
            else: # separate
                file.write("separate\n")
                file.write(str(self.numPlayers) + "\n")
                
                # write numStrats to file
                for x in range(self.numPlayers):
                    file.write(str(self.players[x].numStrats))
                    if x < self.numPlayers - 1:
                        file.write(" ")
                file.write("\n")
                
                # write rationalities to the file
                for x in range(self.numPlayers):
                    file.write(str(self.players[x].rationality))
                    if x < self.numPlayers - 1:
                        file.write(" ")
                file.write("\n")

                # write payoffMatrix to file
                if self.numPlayers < 3:
                    for i in range(self.players[0].numStrats):
                        for j in range(self.players[1].numStrats):
                            for x in range(self.numPlayers):
                                file.write(str(self.payoffMatrix[x][i][j]))
                                if x < self.numPlayers - 1:
                                    file.write(" ")
                            if j < self.players[1].numStrats - 1:
                                file.write(" ")
                        if i < self.players[0].numStrats - 1:
                            file.write("\n")
                else: 
                    for x in range(self.numPlayers):
                        for m in range(self.payoffMatrix[0].shape[0]):
                            for i in range(self.players[0].numStrats):
                                for j in range(self.players[1].numStrats):
                                    file.write(str(self.payoffMatrix[x][m][i][j]))
                                    if j < self.players[1].numStrats - 1:
                                        file.write(" ")
                                if i < self.players[0].numStrats - 1:
                                    file.write("\n")
                            if m < self.payoffMatrix[0].shape[0] - 1:
                                file.write("\n\n")
                        if x < self.numPlayers - 1:
                            file.write("\n\n")
                return
            print("Saved to " + fileName + ".\n")
    
    def unhash(self, m):
        """Converts an index in a stack of payoff arrays into the sequence of strategies that produce that index

        Args:
            m (int): the index of the payoff array that we're unhashing

        Returns:
            list: a list of indices (strategies)
        """
        choice = 0
        prevValues = 0 # values from players below P_x
        productNumStrats = 1
        profile = [0 for i in range(self.numPlayers)]
        profile[0] = -1
        profile[1] = -1
        
        for x in range(2, self.numPlayers - 1):
            productNumStrats *= self.players[x].numStrats
            
        for x in range(self.numPlayers - 1, 1, -1):
            choice = 0
            while productNumStrats * choice + prevValues < m and choice != self.players[x].numStrats - 1:
                choice += 1
            
            if productNumStrats * choice + prevValues > m:
                choice -= 1
                
            prevValues += productNumStrats * choice
            profile[x] = choice
            productNumStrats = productNumStrats / self.players[x].numStrats
        return profile

arr = np.array([
    [[1, 2], [3, 4]],
    [[5, 6], [7, 8]],
    [[9, 10], [11, 12]]
])

G = simGame(3)
G.print()
G.enterPayoffs(arr)
G.print()
G.removeStrategy(1, 0)
print("G again:")
G.print()