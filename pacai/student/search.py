"""
In this file, you will implement generic search algorithms which are called by Pacman agents.
"""
import pacai.util.queue as queue
import pacai.util.stack as stack
import pacai.util.priorityQueue as priorityQueue

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first [p 85].

    Your search algorithm needs to return a list of actions that reaches the goal.
    Make sure to implement a graph search algorithm [Fig. 3.7].

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:
    ```
    print("Start: %s" % (str(problem.startingState())))
    print("Is the start a goal?: %s" % (problem.isGoal(problem.startingState())))
    print("Start's successors: %s" % (problem.successorStates(problem.startingState())))
    ```
    """
    frontier = stack.Stack()
    node = problem.startingState()
    frontier.push((node, []))
    explored = set()

    if(problem.isGoal(node)):
        return []
    
    while(True):
        if(frontier.isEmpty()):
            return None
        node = frontier.pop()
        coord = node[0]
        actions = node[1]
        if(problem.isGoal(coord)):
            return actions
        explored.add(coord)

        for states in problem.successorStates(coord):
            if states[0] not in explored:
                da_children = list(actions)
                da_children.append(states[1])
                frontier.push((states[0], da_children
                ))
    

def breadthFirstSearch(problem):
    """
    Search the shallowest nodes in the search tree first. [p 81]
    """
    frontier = queue.Queue()
    node = problem.startingState()
    frontier.push((node, []))
    explored = set()
    
    while(frontier.isEmpty() == False):
        node = frontier.pop()
        coord = node[0]
        actions = node[1]
        explored.add(coord)
        if(problem.isGoal(coord)):
            return actions
        
        for states in problem.successorStates(coord):
            da_children = list(actions)
            da_children.append(states[1])
            if states[0] not in explored:
                if(problem.isGoal(states[0])):
                    return da_children  
                frontier.push((states[0], da_children))
                explored.add(states[0])
    return []


def uniformCostSearch(problem):
    """
    Search the node of least total cost first.
    """
    frontier = priorityQueue.PriorityQueue()
    node = problem.startingState()
    frontier.push((node, []), 0)
    explored = set()

    if(problem.isGoal(node)):
        return []
    
    while(True):
        if(frontier.isEmpty()):
            return None
        node = frontier.pop()
        coord = node[0]
        actions = node[1]
        if(problem.isGoal(coord)):
            return actions
        explored.add(coord)

        for states in problem.successorStates(coord):
            if states[0] not in explored:
                da_children = list(actions)
                da_children.append(states[1])
                if(problem.isGoal(states[0])):
                    return da_children  
                frontier.push((states[0], da_children), states[2])
                explored.add(states[0])

def aStarSearch(problem, heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    node = problem.startingState()
    frontier = priorityQueue.PriorityQueue()
    frontier.push((node, [], 0), 0)
    explored = set()

    if(problem.isGoal(node)):
        return []
    
    while(True):
        if(frontier.isEmpty()):
            return None
        node = frontier.pop()
        coord = node[0]
        actions = node[1]

        if(problem.isGoal(coord)):
            return actions
        explored.add(coord)

        for states in problem.successorStates(coord):
            if states[0] not in explored:
                da_children = list(actions)
                da_children.append(states[1])
                if(problem.isGoal(states[0])):
                    return da_children  
                
                path_cost = len(da_children)
                heu_cost = heuristic(states[0], problem)
                total_cost = path_cost + heu_cost
                
                frontier.push((states[0], da_children, states[2]), total_cost)
                explored.add(states[0])
