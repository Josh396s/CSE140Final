from pacai.agents.capture.reflex import ReflexCaptureAgent
from pacai.core.directions import Directions
from collections import deque


def createTeam(firstIndex, secondIndex, isRed,
        first = 'pacai.student.DefensiveReflexAgent',
        second = 'pacai.student.OffensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    # """

    return [
        OffensiveReflexAgent(firstIndex, top = False),
        DefensiveeReflexAgent(secondIndex, top = False),
    ]


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    Operation blitzkreig:
        - Agent first tries to eat the closest power pellet capsule cheese whatever
        - If the power pellet is on, go after food while actively avoiding the enemy. The enemy is scared of you and we will use that to our advantage to exploit them and eat food.
        - If the power pellet is off, go after food while actively avoiding the enemy.
        - Depending on the agent index, before it crosses the halfway mark into enemy territory, it will get as close to enemy corners.
    This agent will follow operation blitzkreig.
    """

    def __init__(self, index, top, **kwargs):
        super().__init__(index)
        self.top = top
        # save power pellet locations
        self.powerPelletLocations = None
        self.enemy = False
        self.first = True
        self.in_enemy_territory = False
        self.powerPellet = False

        # # TODO: remove
        # import collections, pickle
        # with open('maze_distances.pickle', 'rb') as in_file:
        #     self.mazeDistances = pickle.load(in_file)
        # with open('valid_locations.pickle', 'rb') as in_file:
        #     self.valid_locations = pickle.load(in_file)

        # print current location
        

    def getFeatures(self, gameState, action):

        #self.mazeDistances = collections.defaultdict(int)
        if self.first == True:
            
            self.first= False
            import copy
            current_game_state = copy.deepcopy(gameState)
            
            # generate a dict of true map distances from every position in the grid, to every other position in the grid. Floyd-Warshall algorithm
            self.mazeDistances = {} # key = (pos1, pos2), value = distance
            # floyd warshall

            # generate list of valid pairs of positions in the grid (not walls). Set distance for each to 1 in maze distances. Utilize game_state to explore
            visited = set()
            queue = deque([current_game_state])
            while queue:
                current_game_state = queue.popleft()
                current_position = current_game_state.getAgentPosition(self.index)
                if current_position not in visited:
                    visited.add(current_position)
                    for action in current_game_state.getLegalActions(self.index):
                        successor = current_game_state.generateSuccessor(self.index, action)
                        if successor.getAgentPosition(self.index) not in visited:
                            queue.append(successor)
                            points = [current_position, successor.getAgentPosition(self.index)]
                            self.mazeDistances[points[0], points[1]] = 1
                            self.mazeDistances[points[1], points[0]] = 1
            

            self.valid_locations = copy.deepcopy(visited)
            visited = list(sorted(visited, key = lambda x: (x[0], x[1])))
            
            for i in visited:
                for j in visited:

                    if i != j:
                        if (i, j) not in self.mazeDistances:
                            self.mazeDistances[i, j] = 10000
                            self.mazeDistances[i, j] = 10000
                    else:
                        self.mazeDistances[i, j] = 0
                        self.mazeDistances[j, i] = 0    

            # perform floyd-warshall on maze distances to calculate distance to every point
            for k in visited:
                for i in visited:
                    for j in visited:
                        # skip duplicates
                        
                            self.mazeDistances[i, j] = min(self.mazeDistances[i, j], self.mazeDistances[i, k] + self.mazeDistances[k, j])

            # with open("output.txt", 'w') as out_file:
            #     out_file.write(str(sorted(self.mazeDistances.items())))
            # import pickle
            # # pickle mazedistances and valid locations
            # with open('maze_distances.pickle', 'wb') as out_file:
            #     pickle.dump(self.mazeDistances, out_file)
            # with open('valid_locations.pickle', 'wb') as out_file:
            #     pickle.dump(self.valid_locations, out_file)
            # import sys
            # sys.exit()
        # function that uses a queue and bfs to calculate maze distance using the maze
        def bfsDistance(destination):
            # if not self.valid_locations:
            #     self.valid_locations = valid_grid_positions = [(x, y) for x in range(1, gameState.getWalls()._width) for y in range(1, gameState.getWalls()._height) if not gameState.hasWall(x, y)]
            if destination not in self.valid_locations:
                return 0
            current_position = gameState.generateSuccessor(self.index, action).getAgentPosition(self.index)
            # convert values to int
            current_position = (int(current_position[0]), int(current_position[1]))
            destination = (int(destination[0]), int(destination[1]))
            return self.mazeDistances[current_position, destination]
        self.bfsDistance = bfsDistance
        '''
        Main Features:
        - Distance to Food
        - Distance to enemy corner
        - Distance to closest enemy
        - Distance to power pellet
        - Distance to enemy territotry (halfway mark)
        - Booleans for if enemy is on the enemy side
        '''
        if not self.powerPelletLocations:
            self.powerPelletLocations = self.getCapsules(gameState)[:]
        features = {}

        successor = self.getSuccessor(gameState, action)
        myPos = successor.getAgentPosition(self.index)

        # Computes distance to food
        # print food on red side

        foodList = successor.getBlueFood().asList() if self.red else successor.getRedFood().asList()
        prev_food_list = gameState.getBlueFood().asList() if self.red else gameState.getRedFood().asList()
        features['foodDistance'] = 1/min([bfsDistance(food) for food in foodList])
        closest_food = min(foodList, key = lambda x: bfsDistance(x))
        if len(prev_food_list) > len(foodList):
            features['foodDistance'] = 2
        # if closest food has another food next to it, add a priority of 1 to it. keep chaining it and add +1 for ever food in the cluster

        stack = [closest_food]
        visited = set()
        while stack:
            current_food = stack.pop()
            visited.add(current_food)
            # use self.mazeDistances
            adjacent_food = [food for food in foodList if self.mazeDistances[current_food, food] == 1]
            for food in adjacent_food:
                if food not in visited:
                    stack.append(food)
        features['foodDistance'] += len(visited) - 1
            

        def manhattanDistance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        # Computes distance to enemy corner. If self.top is true, then go to the top enemy corner. Else, go to the bottom enemy corner. If red, choose blue side corner. If blue, choose red side corner.
        if (not self.red):
            # get distance to closest valid position in grid to corner. For example, if 1,1 is not valid, check all positions to find the closest valid position to 1,1
            if (self.top):
                closest_valid_position = min(self.valid_locations, key = lambda x: manhattanDistance(x, (1, 1)))
                #features['enemyCornerDistance'] = bfsDistance(closest_valid_position)
                features['enemyCornerDistance'] = manhattanDistance(myPos, (1, 1))
                
            else:
                closest_valid_position = min(self.valid_locations, key = lambda x: manhattanDistance(x, (1, gameState.getWalls()._height)))
                #features['enemyCornerDistance'] = bfsDistance(closest_valid_position)
                features['enemyCornerDistance'] = manhattanDistance(myPos, (1, 1))

        else:
            if (self.top):
                closest_valid_position = min(self.valid_locations, key = lambda x: manhattanDistance(x, (gameState.getWalls()._width, 1)))
                #features['enemyCornerDistance'] = bfsDistance(closest_valid_position)
                features['enemyCornerDistance'] = manhattanDistance(myPos, (1, 1))
            else:
                closest_valid_position = min(self.valid_locations, key = lambda x: manhattanDistance(x, (gameState.getWalls()._width, gameState.getWalls()._height)))
                #features['enemyCornerDistance'] = bfsDistance(closest_valid_position)
                features['enemyCornerDistance'] = manhattanDistance(myPos, (1, 1))
  
        features['enemyCornerDistance'] = 1/features['enemyCornerDistance'] if features['enemyCornerDistance'] != 0 else 0


        # Computes distance to closest enemy
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [a.getPosition() for a in enemies if a.getPosition() is not None]
        closest_enemy_distance = min([bfsDistance(enemy) for enemy in enemyPos])
        features['enemyDistance'] = 1/closest_enemy_distance if closest_enemy_distance != 0 else 0
        features['enemyDistance2'] = 1/closest_enemy_distance if closest_enemy_distance != 0 else 1.1

        # Computes distance to red power pellet
        powerPellets = gameState.getCapsules()
        # filter out power pellets that are on the same side as the agent
        powerPellets = [powerPellet  if (powerPellet[0] <= gameState.getWalls()._width/2) != self.red else powerPellet[0] >= gameState.getWalls()._width/2   for powerPellet in powerPellets] 
        features['powerPelletDistance'] = 0
        if powerPellets:
            closest_power_pellet = min([bfsDistance(powerPellet) for powerPellet in powerPellets])
            features['powerPelletDistance'] = 1/closest_power_pellet if closest_power_pellet != 0 else 1.1
            # if previous power pellet list is greater than current power pellet list, then we ate a power pellet
            if len(gameState.getCapsules()) > len(successor.getCapsules()):
                features['powerPelletDistance'] = 2
        
        features['successorScore'] = self.getScore(successor)

        return features

    def getWeights(self, gameState, action):
        '''
        1. If agent is on its own side, prioritize moving to enemy corner 
        2. If agent is on enemy side, prioritize eating power pellet Capsule
        3. If power pellet is consumed, prioritize eating food
        4. Avoid enemy while agent is on enemey territory at all times.
        '''

        successor = self.getSuccessor(gameState, action)
        # defaault weights for all attribuets to 0
        
        weights = {
            'foodDistance': 1,
            'enemyCornerDistance': 0,
            'enemyDistance': 0,
            'powerPelletDistance': 2,
            'enemyOnEnemySide': 0,
            'successorScore':0,
            'enemyDistance2': 0
        }
        
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPos = [a.getPosition() for a in enemies if a.getPosition() is not None]
        closest_enemy_distance = min([self.bfsDistance(enemy) for enemy in enemyPos])
        #get closest enemy index
        closest_enemy_index = [enemyPos[i].index for i in range(len(enemyPos)) if self.bfsDistance(enemyPos[i]) == closest_enemy_distance][0]
        #if closest enemy is a ghost and is within 3 spaces, prioritize avoiding enemy
        halfway_mark = gameState.getWalls()._width/2
        if self.red:
            if successor.getAgentPosition(self.index)[0] > halfway_mark and closest_enemy_distance <= 3:
                weights['enemyDistance'] = -2
            if successor.getAgentPosition(self.index)[0] <= halfway_mark and closest_enemy_distance <= 5:
                weights['enemyDistance2'] = 2
        else:
            if successor.getAgentPosition(self.index)[0] < halfway_mark and closest_enemy_distance <= 3:
                weights['enemyDistance'] = -2
            if successor.getAgentPosition(self.index)[0] >= halfway_mark and closest_enemy_distance <= 5:
                weights['enemyDistance2'] = 2
        time_left = successor.getTimeleft()
        if time_left > 1100:
            weights['enemyCornerDistance'] = 1000

        
        # for enemey in enemies:
        #     if enemey._scaredTimer > 0:
        #         self.powerPellet = True
        
        # if  self.powerPellet:
        #     weights['powerPelletDistance'] = 0
        #     weights['foodDistance'] = 1




        return weights


class DefensiveeReflexAgent(OffensiveReflexAgent):
    def getWeights(self, gameState, action):
        '''
        1. If agent is on its own side, prioritize moving to enemy corner 
        2. If agent is on enemy side, prioritize eating power pellet Capsule
        3. If power pellet is consumed, prioritize eating food
        4. Avoid enemy while agent is on enemey territory at all times.
        '''

        successor = self.getSuccessor(gameState, action)
        # defaault weights for all attribuets to 0
        
        weights = {
            'foodDistance': 0,
            'enemyCornerDistance': 0,
            'enemyDistance': 1,
            'powerPelletDistance': 0,
            'enemyOnEnemySide': 0,
            'successorScore':0,
            'enemyDistance2': 0
        }
        
        # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        # enemyPos = [a.getPosition() for a in enemies if a.getPosition() is not None]
        # closest_enemy_distance = min([self.bfsDistance(enemy) for enemy in enemyPos])
        # #get closest enemy index
        # closest_enemy_index = [enemyPos[i].index for i in range(len(enemyPos)) if self.bfsDistance(enemyPos[i]) == closest_enemy_distance][0]
        # #if closest enemy is a ghost and is within 3 spaces, prioritize avoiding enemy
        # halfway_mark = gameState.getWalls()._width/2
        # if self.red:
        #     if successor.getAgentPosition(self.index)[0] > halfway_mark and closest_enemy_distance <= 3:
        #         weights['enemyDistance'] = -2
        #     if successor.getAgentPosition(self.index)[0] <= halfway_mark and closest_enemy_distance <= 5:
        #         weights['enemyDistance2'] = 2
        # else:
        #     if successor.getAgentPosition(self.index)[0] < halfway_mark and closest_enemy_distance <= 3:
        #         weights['enemyDistance'] = -2
        #     if successor.getAgentPosition(self.index)[0] >= halfway_mark and closest_enemy_distance <= 5:
        #         weights['enemyDistance2'] = 2
        # time_left = successor.getTimeleft()
        # if time_left > 1100:
        #     weights['enemyCornerDistance'] = 1000

        
        # for enemey in enemies:
        #     if enemey._scaredTimer > 0:
        #         self.powerPellet = True
        
        # if  self.powerPellet:
        #     weights['powerPelletDistance'] = 0
        #     weights['foodDistance'] = 1




        return weights
