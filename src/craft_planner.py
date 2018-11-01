import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

max_items = {  "wood": 4, \
                "plank": 4, \
                "stick": 8, \
                "coal": 1, \
                "cobble": 8, \
                "ore": 6, \
                "ingot": 6, \
                "wooden_axe": 1, \
                "wooden_pickaxe": 1, \
                "stone_axe": 1, \
                "stone_pickaxe": 1, \
                "iron_axe": 1, \
                "iron_pickaxe": 1, \
                "furnace": 1, \
                "bench": 1, \
                "rail": 0, \
                "cart": 0 }
item_tier = {   "wood": 0, \
                    "plank": 0, \
                    "stick": 0, \
                    "coal": 0, \
                    "cobble": 1, \
                    "ore": 2, \
                    "ingot": 2, \
                    "wooden_axe": 0, \
                    "wooden_pickaxe": 0, \
                    "stone_axe": 1, \
                    "stone_pickaxe": 1, \
                    "iron_axe": 2, \
                    "iron_pickaxe": 2, \
                    "furnace": 1, \
                    "bench": 0, \
                    "rail": 3, \
                    "cart": 3 }


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if 'Requires' in rule:
            for key in rule['Requires']:
                if state[key] < 1:
                    return False

        if 'Consumes' in rule:
            for key in rule['Consumes']:
                if state[key] < rule['Consumes'][key]:
                    return  False

        for key in rule['Produces']:
            if state[key] + rule['Produces'][key] > max_items[key]:
                return False

        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = State(state)
        
        if 'Produces' in rule:
            for key in rule['Produces']:
                """if key not in next_state:
                    next_state[key] = rule['Produces'][key]
                else:
                    next_state[key] += rule['Produces'][key]"""
                next_state[key] += rule['Produces'][key]

        if 'Consumes' in rule:
            for key in rule['Consumes']:
                """if key not in next_state:
                    next_state[key] = rule['Consumes'][key]
                else:
                    next_state[key] -= rule['Consumes'][key]"""
                next_state[key] -= rule['Consumes'][key]

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        """goal_keys = goal.keys()
        state_keys = state.keys()

        if len(goal_keys) != len(state_keys):
            return False
        else:
            for key in goal_keys:
                if key not in state_keys or state[key] != goal[key]:
                    return False"""
        for key in goal:
            if state[key] < goal[key]:
                return False

        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)

def get_depth(state):
    item_depth = {  "wood": 0, \
                    "plank": 1, \
                    "stick": 2, \
                    "coal": 4, \
                    "cobble": 4, \
                    "ore": 6, \
                    "ingot": 6, \
                    "wooden_axe": 3, \
                    "wooden_pickaxe": 3, \
                    "stone_axe": 5, \
                    "stone_pickaxe": 5, \
                    "iron_axe": 7, \
                    "iron_pickaxe": 7, \
                    "furnace": 5, \
                    "bench": 2, \
                    "rail": 7, \
                    "cart": 7 }

    max_depth = 0
    for item in state:
        if state[item] > 0 and item_depth[item] > max_depth:
            max_depth = item_depth[item]
    return max_depth

def tier(state):
    max_tier = -1
    for item in state:
        if item_tier[item] > max_tier:
            max_tier = item_tier[item]
    return max_tier

def heuristic(curr, goal):
    # Implement your heuristic here!
    """items = {  "wood": 4, \
                "plank": 5, \
                "stick": 8, \
                "coal": 1, \
                "cobble": 10, \
                "ore": 8, \
                "ingot": 8, \
                "wooden_axe": 1, \
                "wooden_pickaxe": 1, \
                "stone_axe": 1, \
                "stone_pickaxe": 1, \
                "iron_axe": 1, \
                "iron_pickaxe": 1, \
                "furnace": 1, \
                "bench": 1, \
                "rail": 48, \
                "cart": 1 }
    for item in curr:
        if curr[item] > items[item]:
            return inf"""

    """curr_tier = tier(curr)
    val_items = 0
    if curr_tier < tier(goal):
        wanted_items = [    [], \
                            ["wooden_pickaxe", "cobble"], \
                            ["stone_pickaxe", "ore", "ingot"] \
                            ["ingot"]]
        for item in state:
            if item in wanted_items[curr_tier + 1]:
                val_items += curr[item]
            else:
                val_items -= curr[item]

    return (0 - val_items)*0"""
    return tier(goal) - tier(curr)

def search(graph, state, is_goal, limit, heuristic, goal):

    start_time = time()

    distances = {}
    previous = {}
    pqueue = []

    heappush(pqueue, (0, state, 'initial'))
    distances[state] = 0
    previous[state] = (-1, 'initial')

    plan_found = False
    last_state = None

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit and len(pqueue) > 0 and not plan_found:
    #while len(pqueue) > 0 and not plan_found:
        estimation, keystate, name = heappop(pqueue)

        if is_goal(keystate):
            plan_found = True
            last_state = keystate
            break

        adj = graph(keystate)

        for action in adj:
            new_name = action[0]
            new_state = action[1]
            edge_cost = action[2]
            heur = heuristic(new_state, goal)
            #print("attempted: ", new_name, "\nheur: ", heur)
            #print("prev state: ", keystate, "\nnew state: ", new_state, "\nheur: ", heur)
            new_estimation = distances[keystate] + edge_cost + heur

            if new_state not in distances or new_estimation < distances[new_state] + heur:
                distances[new_state] = distances[keystate] + edge_cost
                previous[new_state] = (keystate, name)
                heappush(pqueue, (new_estimation, new_state, new_name))
    
    if plan_found is True:
        path = []

        print("Elapsed Time: ", time() - start_time)

        curr_state = last_state
        while curr_state != state:
            path.insert(0, previous[curr_state])
            curr_state = previous[curr_state][0]

        return path
    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])
    goal = State(Crafting['Goal'])

    if 'rail' in goal:
        max_items['rail'] = 32
    if 'cart' in goal:
        max_items['cart'] = goal['cart']

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic, goal)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
