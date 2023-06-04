from pacai.agents.capture.reflex import ReflexCaptureAgent
from pacai.agents.capture.capture import CaptureAgent
from pacai.core.directions import Directions
from pacai.bin.capture import CaptureGameState
from pacai.util import util
import time
import random


def createTeam(firstIndex, secondIndex, isRed,
        first = 'ReflexCaptureAgent1',
        second = 'ReflexCaptureAgent2'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    # """

    return [
        ReflexCaptureAgent1(firstIndex),
        ReflexCaptureAgent2(secondIndex),
    ]


class ReflexCaptureAgent1(CaptureAgent):
    """
    A reflex agent that tries to keep its side Pacman-free.
    This is to give you an idea of what a defensive agent could be like.
    It is not the best or only way to make such an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest return from `ReflexCaptureAgent.evaluate`.
        """

        actions = gameState.getLegalActions(self.index)

        start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """

        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)

        return stateEval

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """

        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()

        if (pos != util.nearestPoint(pos)):
            # Only half a grid position was covered.
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def getFeatures(self, gameState, action):
        features = {}
        height = gameState.getInitialLayout().getHeight()

        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if (myState.isPacman()):
            features['onDefense'] = 0
        
        # Computes distance to invaders we can see.
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)

        #If we have invaders, defend
        if (len(invaders) > 0 and features['onDefense'] == 1): 
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

            if (action == Directions.STOP):
                features['stop'] = 1

            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if (action == rev):
                features['reverse'] = 1
        
        #If there are no invaders, attack
        else:
            features = {}
            successor = self.getSuccessor(gameState, action)
            features['successorScore'] = self.getScore(successor)
    
            # Compute distance to the nearest food.
            foodPositions = []
            foodList = self.getFood(successor).asList()
            for foodPos in foodList:
                if(foodPos[0] >= (height//2)):
                    foodPositions.append(foodPos)

            #Compute the distance to the nearest capsule
            capsulePositions = []
            if(1 in CaptureAgent.getTeam(self, gameState)): #If we're Red
                capsuleList = CaptureGameState.getRedCapsules(successor)
            else: #If we're Blue
                capsuleList = CaptureGameState.getBlueCapsules(successor)
            for capPos in capsuleList:
                if(capPos[0] >= (height//2)):
                    capsulePositions.append(capPos)


            #Getting shortest distance to food, if any
            if (len(foodPositions) > 0):
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodPositions])
                features['distanceToFood'] = minDistance
            
            #Getting shortest distance to capsule, if any
            if(len(capsulePositions) > 0):
                minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsulePositions])
                features['distanceToCapusle'] = minDistance

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -1000,
            'onDefense': 10,
            'invaderDistance': -10,
            'stop': -100,
            'reverse': -2,
            'successorScore': 100,
            'distanceToFood': -1,
            'distanceToCapusle': -10000
        }

class ReflexCaptureAgent2(CaptureAgent):
    """
    A reflex agent that tries to keep its side Pacman-free.
    This is to give you an idea of what a defensive agent could be like.
    It is not the best or only way to make such an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest return from `ReflexCaptureAgent.evaluate`.
        """

        actions = gameState.getLegalActions(self.index)

        start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights.
        """

        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        stateEval = sum(features[feature] * weights[feature] for feature in features)

        return stateEval

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """

        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()

        if (pos != util.nearestPoint(pos)):
            # Only half a grid position was covered.
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def getFeatures(self, gameState, action):
        features = {}
        height = gameState.getInitialLayout().getHeight()

        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if (myState.isPacman()):
            features['onDefense'] = 0
        
        # Computes distance to invaders we can see.
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)

        #If we have invaders, defend
        if (len(invaders) > 0 and features['onDefense'] == 1): 
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

            if (action == Directions.STOP):
                features['stop'] = 1

            rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
            if (action == rev):
                features['reverse'] = 1
        
        #If there are no invaders, attack
        else:
            features = {}
            successor = self.getSuccessor(gameState, action)
            features['successorScore'] = self.getScore(successor)
    
            # Compute distance to the nearest food.
            foodPositions = []
            foodList = self.getFood(successor).asList()
            for foodPos in foodList:
                if(foodPos[0] <= (height//2)):
                    foodPositions.append(foodPos)

            #Compute the distance to the nearest capsule
            capsulePositions = []
            if(1 in CaptureAgent.getTeam(self, gameState)): #If we're Red
                capsuleList = CaptureGameState.getRedCapsules(successor)
            else: #If we're Blue
                capsuleList = CaptureGameState.getBlueCapsules(successor)
            for capPos in capsuleList:
                if(capPos[0] <= (height//2)):
                    capsulePositions.append(capPos)


            #Getting shortest distance to food, if any
            if (len(foodPositions) > 0):
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodPositions])
                features['distanceToFood'] = minDistance
            
            #Getting shortest distance to capsule, if any
            if(len(capsulePositions) > 0):
                minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsulePositions])
                features['distanceToCapusle'] = minDistance

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -1000,
            'onDefense': 10,
            'invaderDistance': -10,
            'stop': -100,
            'reverse': -2,
            'successorScore': 100,
            'distanceToFood': -1,
            'distanceToCapusle': -10000
        }
