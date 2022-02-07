import json
import string


def argmax(xs):
    return max(range(len(xs)), key=lambda i : xs[i])

def char_to_idx(c):
    return ord(c) - ord('a')

def word_counts(word):
    # Returns the count of each letter in the word
    return [word.count(c) for c in string.ascii_lowercase]


class WordState:
    def __init__(self, greens, yellows, grays, known_not) -> None:
        self.greens = greens
        self.yellows = yellows
        self.grays = grays

        self.known_not = known_not
    
    def word_valid(self, word):
        for i, green in enumerate(self.greens):
            if green != None and word[i] != green:
                return False
        counts = word_counts(word)
        for gray, limit in self.grays.items():
            if counts[char_to_idx(gray)] >= limit:
                return False
        for yellow, count in self.yellows.items():
            if counts[char_to_idx(yellow)] < count:
                return False
        for i, c in enumerate(word):
            if c in self.known_not[i]:
                return False
        return True

    def filter_list(self, word_list):
        # Filter out words that do not match the green letters
        return list(filter(lambda w: self.word_valid(w), word_list))


    def __repr__(self) -> str:
        return f"{self.greens}"

start_state = WordState([None, None, None, None, None], {c: 0 for c in string.ascii_lowercase}, {}, [{}, {}, {}, {}, {}])


class Game:
    def __init__(self, word) -> None:
        self.word = word
        wc = word_counts(word)
        self.gold_counts = {c: wc[i] for i, c in enumerate(string.ascii_lowercase)}

    def guess(self, state, guess) -> WordState:
        new_greens = [c for c in state.greens]
        new_grays = {c: v for c, v in state.grays.items()}
        new_known_not = [{c for c in kn} for kn in state.known_not]

        wc = word_counts(guess)
        found_grays = {}
        for i, c in enumerate(guess):
            if c == self.word[i]:
                new_greens[i] = c
            elif c in self.word:
                new_known_not[i].add(c)
            if wc[char_to_idx(c)] > self.gold_counts[c]:
                found_grays[c] = self.gold_counts[c] + 1
        
        new_yellows = {c: min(self.gold_counts[c], max(wc[char_to_idx(c)], state.yellows[c])) for c in string.ascii_lowercase}
        for c in found_grays:
            new_grays[c] = min(new_grays[c], found_grays[c]) if c in new_grays else found_grays[c]
        return WordState(new_greens, new_yellows, new_grays, new_known_not)
            

with open("dict.json") as infile:
    json_dict = json.load(infile)
    solutions = json_dict['solutions']
    herrings = json_dict['herrings']
all_words = solutions + herrings


def letter_stats(word_list):
    stats = [[0 for _ in range(26)] for _ in range(5)]
    for word in word_list:
        for i, c in enumerate(word):
            stats[i][char_to_idx(c)] += 1
    return stats

def most_likely(word_list):
    stats = letter_stats(word_list)
    score = [sum([stats[i][char_to_idx(c)] for i, c in enumerate(word)]) for word in word_list]
    high = argmax(score)
    return word_list[high]

def do_turn(game, state, words):
    to_guess = most_likely(words)
    new_state = game.guess(state, to_guess)
    new_words = new_state.filter_list(words)
    return new_state, new_words, to_guess


def play_game(goal_word, max_turns=6):
    game = Game(goal_word)
    cur_state = start_state
    cur_words = solutions
    for turn in range(max_turns):
        cur_state, cur_words, guessed = do_turn(game, cur_state, cur_words)
        # print(f"Turn {turn+1}: Guessed '{guessed}'. State: {cur_state}, Remaining: {cur_words}")
        if guessed == goal_word:
            print(f"Guessed {goal_word} in {turn+1} turns.")
            return True, turn+1
    print(f"Did not guess {goal_word}.")
    return False, -1
    

guessed_turns = []
not_guessed = []
for word in solutions:
    solved, turns = play_game(word)
    if solved:
        guessed_turns.append(turns)
    else:
        not_guessed.append(word)

print(f"Average turns for solved: {sum(guessed_turns) / len(guessed_turns)}")
print(f"Couldn't guess: {not_guessed}")
