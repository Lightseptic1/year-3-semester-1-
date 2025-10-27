DOMAINS = {
    'Hana': ['Vanilla', 'Chocolate', 'Cheesecake'],  # Hana
    'Youssef': ['Vanilla', 'Chocolate', 'Cheesecake'],  # Youssef
    'Ahmed': ['Vanilla', 'Chocolate', 'Cheesecake'],   # Ahmed
    'Zeina': ['Vanilla', 'Chocolate', 'Cheesecake']
}

# Order of assignment
VARIABLES = ['Hana', 'Youssef', 'Ahmed', 'Zeina']
def is_consistent(var, value, assignment):
    """
    Check if assigning 'value' to 'var' breaks any rules
    with already assigned variables.
    """
    # Rule 1: A ≠ B
    if var == 'Hana' and 'Youssef' in assignment:
        if value == assignment['Youssef']:
            return False
    if var == 'Youssef' and 'Hana' in assignment:
        if value == assignment['Hana']:
            return False

    # Rule 2: B = C
    if var == 'Youssef' and 'Ahmed' in assignment:
        if value != assignment['Ahmed']:
            return False
    if var == 'Ahmed' and 'Youssef' in assignment:
        if value != assignment['Youssef']:
            return False
    if var == 'Zeina' and 'Hana' in assignment and value == assignment['Hana']:
        return False
    if var == 'Hana' and 'Zeina' in assignment and value == assignment['Zeina']:
        return False
    

    return True
def backtrack(assignment, tries):
    if len(assignment) == len(VARIABLES):
        return assignment
    var = next(v for v in VARIABLES if v not in assignment)
    for value in DOMAINS[var]:
        tries['attempts'] += 1
        if is_consistent(var, value, assignment):
            assignment[var] = value
            res = backtrack(assignment, tries)
            if res is not None:
                return res
            del assignment[var]
            tries['backtracks'] += 1
    return None
def backtrack_fowardchecker(assignment, domains, tries):
    if len(assignment) == len(VARIABLES):
        return assignment
    var = next(v for v in VARIABLES if v not in assignment)
    for value in domains[var]:
        tries['attempts'] += 1
        if not is_consistent(var, value, assignment):
            continue
        temp = {**assignment, var:value}
        pruned = {v:domains[v][:] for v in VARIABLES}
        pruned[var] = [value]
        valid = True
        for nb in VARIABLES:
            if nb == var or nb in assignment:
                continue
            filtered = [cand for cand in pruned[nb] if is_consistent(nb, cand, temp)]
            if not filtered:
                valid = False
                break
            pruned[nb] = filtered
        if not valid:
            continue
        res = backtrack_fowardchecker(temp, pruned, tries)
        if res is not None:
            return res
        tries['backtracks'] += 1
    return None
print("--- Starting Backtracking Search ---")
t1 = {'attempts': 0, 'backtracks': 0}
sol1 = backtrack({}, t1)
print('Solution:', sol1)
print('Attempts:', t1['attempts'], 'Backtracks:', t1['backtracks'])

print('\n--- Backtracking + Forward Checking ---')
init_domains = {v: DOMAINS[v][:] for v in VARIABLES}
t2 = {'attempts': 0, 'backtracks': 0}
sol2 = backtrack_fowardchecker({}, init_domains, t2)
print('Solution:', sol2)
print('Attempts:', t2['attempts'], 'Backtracks:', t2['backtracks'])