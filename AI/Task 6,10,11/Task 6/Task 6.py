rows = 5
cols = 5
acts = ['up', 'down', 'left', 'right']  # set of actions available
terminal_states = {(0, 4): 10, (1, 2): -2, (2, 3): 8, (4, 2): 6}  # fixed values
blocked_states = [(1, 1), (1, 3), (1, 4), (2, 4), (3, 1), (3, 2), (3, 3), (3, 4), (4, 3), (4, 4)]
REWARD = -0.5
DISCOUNT_FACTOR = 0.9  # gamma value


def is_valid_state(state):
    return (0 <= state[0] < rows) and (0 <= state[1] < cols) and (state not in blocked_states)


def reward_function(state):
    if state in terminal_states:
        return terminal_states[state]
    return REWARD


def transition_function(state, action, values):
    if action == 'up':
        next_state = (state[0] - 1, state[1])
    elif action == 'down':
        next_state = (state[0] + 1, state[1])
    elif action == 'left':
        next_state = (state[0], state[1] - 1)
    elif action == 'right':
        next_state = (state[0], state[1] + 1)
    else:
        return None

    if not is_valid_state(next_state):
        return None

    intended_value = 0.8 * values[next_state]
    right_angle_value = 0.1 * values[state]
    opposite_value = 0.1 * values[state]

    return intended_value + right_angle_value + opposite_value


def calculate_value(state, values):
    if state in terminal_states:
        return reward_function(state)

    max_value = float("-inf")

    for action in acts:
        transition_value = transition_function(state, action, values)
        if transition_value is None:
            continue

        action_value = reward_function(state) + DISCOUNT_FACTOR * transition_value
        max_value = max(max_value, action_value)

    return max_value


def print_values(values, iteration):
    print(f'\nUtility values after {iteration} iterations:')
    for state, value in sorted(values.items()):
        print(f'{state} Utility: {value:.2f}')


def value_iteration(theta=1e-4, max_iterations=1000):
    values = {}
    for row in range(rows):
        for col in range(cols):
            state = (row, col)
            if is_valid_state(state):
                values[state] = 0.0

    iteration = 0
    converged_iteration = None

    while iteration < max_iterations:
        delta = 0.0
        new_values = {}

        for state in values:
            old_v = values[state]
            new_v = calculate_value(state, values)
            new_values[state] = new_v

            diff = abs(new_v - old_v)
            delta = max(delta, diff)

        values = new_values

        if iteration % 5 == 0 and iteration != 0:
            print_values(values, iteration)

        if delta < theta:
            converged_iteration = iteration
            break

        iteration += 1

    if converged_iteration is not None:
        if converged_iteration % 5 != 0:
            print_values(values, converged_iteration)
    else:
        print_values(values, iteration)

    # final convergence report
    print(f"\nConverged at iteration: {converged_iteration if converged_iteration is not None else iteration}")

    return values


if __name__ == "__main__":
    value_iteration()
