import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


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
                if key not in state or state[key] is False:
                    return False

        if 'Consumes' in rule:
            for key in rule['Consumes']:
                if key not in state or state[key] < rule['Consumes'][key]:
                    return  False

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
        
        if 'Requires' in rule:
            for key in rule['Produces']:
                if key not in next_state:
                    next_state[key] = rule['Produces'][key]
                else:
                    next_state[key] += rule['Produces'][key]

        if 'Consumes' in rule:
            for key in rule['Consumes']:
                if key not in next_state:
                    next_state[key] = rule['Consumes'][key]
                else:
                    next_state[key] -= rule['Consumes'][key]

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        goal_keys = goal.keys()
        state_keys = state.keys()

        if len(goal_keys) != len(state_keys):
            return False
        else:
            for key in goal_keys:
                if key not in state_keys or state[key] != goal[key]:
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


def total_item_cost(state):
    item_costs = {  "wood": 4, \
                    "plank": 5, \
                    "stick": 6, \
                    "coal": 33, \
                    "cobble": 33, \
                    "ore": 52, \
                    "ingot": 80, \
                    "wooden_axe": 29, \
                    "wooden_pickaxe": 29, \
                    "stone_axe": 44, \
                    "stone_pickaxe": 44, \
                    "iron_axe": 50, \
                    "iron_pickaxe": 50, \
                    "furnace": 61, \
                    "bench": 20, \
                    "rail": 60, \
                    "cart": 60 }
    total_cost = 0
    for item in state:
        total_cost += item_costs[item] * state[item]

    return total_cost

def heuristic(curr, goal):
    # Implement your heuristic here!
    return total_item_cost(goal) - total_item_cost(curr)

def search(graph, state, is_goal, limit, heuristic, goal):

    start_time = time()

    distances = {}
    previous = {}
    pqueue = []

    heappush(pqueue, ('initial', state, 0))
    distances[state] = 0
    previous[state] = (-1, 'initial')

    plan_found = False
    #goal = None

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit and len(pqueue) > 0 and not plan_found:
        name, keystate, estimation = heappop(pqueue)

        adj = graph(keystate)

        for action in adj:
            name = action[0]
            new_state = action[1]
            edge_cost = action[2]
            heur = heuristic(new_state, goal)
            print("prev state: ", keystate, "\nnew state: ", new_state, "\nheur: ", heur)
            new_estimation = distances[keystate] + edge_cost + heur

            if new_state not in distances or new_estimation < distances[new_state] + heur:
                distances[new_state] = distances[keystate] + edge_cost
                previous[new_state] = (keystate, name)
                heappush(pqueue, (name, new_state, new_estimation))
            """elif new_estimation < distances[new_state] + heur:
                distances[new_state] = distances[keystate] + edge_cost
                previous[new_state] = (keystate, name)
                heappush(pqueue, (name, new_state, new_estimation))"""

            if is_goal(new_state):
                plan_found = true
                #goal = new_state
                break
    
    if plan_found is True:
        print("Found plan")
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
    goal = State({key: 0 for key in Crafting['Goal']})

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
