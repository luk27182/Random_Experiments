# %%
import csv
from scipy.stats import entropy

valid_words_path = './data/valid-words.csv'
word_bank_path = './data/word-bank.csv'

valid_words = []
word_bank = []
with open(valid_words_path, 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        valid_words += row

with open(word_bank_path, 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        word_bank += row

# %%
def make_guess(truth, pred):
    truth = [c for c in truth]
    pred = [c for c in pred]
    score = ["X" for i in range(5)]

    for i in range(len(truth)):
        if truth[i] == pred[i]:
            score[i] = "G"
            truth[i] = "SOLVED_TGT"
            pred[i] = "SOLVED_SRC"
    
    for i in range(len(truth)):
        if pred[i] in truth:
            score[i] = "Y"
            truth[truth.index(pred[i])] = "SOLVED_TGT"
            pred[i] = "SOLVED_SRC"
    return "".join(score)

# %%
def calculate_best_split(candidates, valid_words):
    if len(candidates) == 1:
        return candidates[0], {"GGGGG": [candidates[0]]}
    
    theoretical_best = entropy(range(len(candidates)))

    highest_entropy = -1
    best_guess = None
    best_buckets = None

    for guess in candidates+valid_words: # We add candidates to make them checked first
        buckets = dict()
        for candidate in candidates:
            score = make_guess(truth=candidate, pred=guess)
            if score in list(buckets.keys()):
                buckets[score].append(candidate)
            else:
                buckets[score] = [candidate]
        my_entropy = entropy(list([len(bucket) for bucket in buckets.values()]))
        if my_entropy > highest_entropy:
            highest_entropy = my_entropy
            best_guess = guess
            best_buckets = buckets
            if my_entropy == theoretical_best:
                return best_guess, best_buckets
    return best_guess, best_buckets

# %%
def calculate_tree(buckets, depth, prev_guess):
    for bucket in sorted(list(buckets.keys()), reverse=False):
        if not bucket == "GGGGG":
            candidates = buckets[bucket]
            guess, new_buckets = calculate_best_split(candidates, valid_words)

            i = 0
            while str(i)+guess in node_names:
                i += 1
            node_names.append(str(i)+guess)
            nodes.append({"name": str(i)+guess, "label": guess, "parent": prev_guess, "path_from_parent": bucket, "depth":1})

            calculate_tree(buckets=new_buckets, depth=depth+1, prev_guess=str(i)+guess)

print("calculating initial split... (this may take a while)")
guess, buckets = calculate_best_split(word_bank, valid_words)
print(f"Initial guess: {guess}. Calculating Tree...")
node_names = ["0"+guess]
nodes = [{"name": "0"+guess, "label": guess, "parent": None, "path_from_parent": None, "depth":0}]
calculate_tree(buckets=buckets, depth=1, prev_guess="0"+guess)

# %%
color_mapping = {'G': '🟩', 'X': '◻️', 'Y': '🟨'}
for n, parent in enumerate(nodes):
    print(f"{n+1}. GUESS: {parent['label']}")
    children = [node for node in nodes if node["parent"] == parent["name"]]
    for child in children:
        score = ''.join([color_mapping[char] for char in child['path_from_parent']])
        print(f"if {score}, GO TO: {nodes.index(child)+1}")