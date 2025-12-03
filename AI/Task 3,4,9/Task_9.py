rules = [
    ({"burnt_outside", "raw_inside"}, "Heat too high"),
    ({"too_salty"}, "Too much salt"),
    ({"too_bland"}, "Needs seasoning"),
    ({"pasta_mushy"}, "Pasta overcooked"),
    ({"rice_hard"}, "Not enough water or not cooked long enough"),
]

questions = {
    "burnt_outside": "Is the outside burnt",
    "raw_inside": "Is the inside still raw",
    "too_salty": "Is the dish too salty",
    "too_bland": "Does the dish taste bland",
    "pasta_mushy": "Is the pasta mushy",
    "rice_hard": "Is the rice still hard",
}
def get_symptoms():
    symptoms = set()
    for key, q in questions.items():
        ans = input(q + " (y/n): ").strip().lower()
        if ans == "y":
            symptoms.add(key)
    return symptoms

def infer(symptoms):
    conclusions = []
    for conds, diagnosis in rules:
        if conds.issubset(symptoms):
            conclusions.append(diagnosis)
    return conclusions

def main():
    print("Cooking Expert System")
    symptoms = get_symptoms()
    results = infer(symptoms)

    if results:
        print("\nPossible causes:")
        for r in results:
            print("-", r)
    else:
        print("\nNo matching rule found.")

if __name__ == "__main__":
    main()
