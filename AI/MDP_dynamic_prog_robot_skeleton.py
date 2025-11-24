# Step 1: Define the states and actions
# - The warehouse is represented as a 3x3 grid.
# - Define all possible states as tuples (i, j) where i, j are row and column indices.
# - Define possible actions: ["UP", "DOWN", "LEFT", "RIGHT"].
# - Define the goal state, e.g., (2, 2).
# - Set the discount factor (gamma), e.g., 0.9.

states = [(0,1), (0,2), (1,0), (1,2), (2,0), (2,1)]  # TODO: Create a list of states (3x3 grid).
actions = ["UP", "DOWN", "LEFT", "RIGHT"] # TODO: Define the actions: "UP", "DOWN", "LEFT", "RIGHT".
goal_state = {(0,0) :2, (1,1):10, (2,2):5}  # TODO: Set the goal state as a specific grid position.
gamma = 0.9  # TODO: Set the discount factor (e.g., 0.9).

# Step 2: Define the reward function
# - Create a function that returns a high reward (e.g., 10) for reaching the goal state.
# - For all other states, return a small negative reward (e.g., -1) to encourage faster convergence.

def reward(state):
   return (goal_state.get(state, -1))
    

# Step 3: Define the transition model
# - Create a function that determines the next state given the current state and an action.
# - Ensure the agent does not move outside the grid boundaries.
# - For invalid actions (e.g., moving up from the top row), the state should remain the same.

def transition(state, action):
    # TODO: Implement the logic for transitioning between states based on actions.
    # Actions include "UP", "DOWN", "LEFT", "RIGHT".
    pass

# Step 4: Implement the Value Iteration Algorithm
# - Initialize a value function V for all states, starting with 0.
# - Iteratively update the value of each state using the Bellman equation:
#   V[state] = max(reward(state) + gamma * V[next_state] for all actions)
# - Stop iterating when the changes in value (delta) are below a small threshold (theta).

def value_iteration(states, actions, theta=1e-4, gamma=0.9):
    # Initialize V as a dictionary with states as keys and 0 as initial values
    V = {s: 0.0 for s in states}

    while True:
        delta = 0
        for state in states:
            if state in goal_state:
                v_old = V[state]
                V[state] = reward(state)
                delta = max(delta, abs(v_old - V[state]))
                continue

            v_old = V[state]

            # Bellman update: max over actions
            action_values = []
            for a in actions:
                next_state = transition(state, a)
                action_values.append(reward(state) + gamma * V[next_state])

            V[state] = max(action_values)

            delta = max(delta, abs(v_old - V[state]))

        # Convergence check
        if delta < theta:
            break

    return V

# Step 5: Run Value Iteration
# - Call the value_iteration function with the defined states and actions.
# - Store the resulting values in a variable.

values = value_iteration(states,actions, theta=1e-4, gamma=gamma) # TODO: Run the value_iteration function with states and actions.

# Step 6: Display the Results
# - Print the optimal state values in a 3x3 grid format for easier interpretation.
# - Use nested loops to iterate over the grid rows and columns.

print("Optimal State Values in Warehouse:")
for i in range(3):  # TODO: Iterate through rows.
    # TODO: Collect the values for the current row and format them.
    row_values = None
    print(" | ".join(row_values))  # Print row values separated by ' | '.
