import json


def argmax(xs):
    return max(range(len(xs)), key=lambda i : xs[i])

def char_to_idx(c):
    return ord(c) - ord('a')


class WordState:
    def __init__(self, greens, yellows, grays) -> None:
        self.greens = greens
        self.yellows = yellows
        self.grays = grays
    
    def word_valid(self, word):
        for i, green in enumerate(self.greens):
            if green != None and word[i] != green:
                return False
        for yellow in self.yellows:
            if yellow not in word:
                return False
        for gray in self.grays:
            if gray in word:
                return False
        return True

    def filter_list(self, word_list):
        # Filter out words that do not match the green letters
        return list(filter(lambda w: self.word_valid(w), word_list))


    def __repr__(self) -> str:
        return f"{self.greens}"

start_state = WordState([None, None, None, None, None], [], [])


class Game:
    def __init__(self, word) -> None:
        self.word = word

    def guess(self, state, guess) -> WordState:
        new_greens = [c for c in state.greens]
        new_yellows = [c for c in state.yellows]
        new_grays = [c for c in state.grays]
        for i, c in enumerate(guess):
            if c in self.word:
                new_yellows.append(c)
            else:
                new_grays.append(c)
            if c == self.word[i]:
                new_greens[i] = c
        return WordState(new_greens, new_yellows, new_grays)
            

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


test_game = Game("aloft")
# test_state = test_game.guess(start_state, "slick")
# print(test_state)
# filtered_words = test_state.filter_list(solutions)
# print(filtered_words)
# print(most_likely(filtered_words))
cur_state = start_state
cur_words = solutions
for turn in range(6):
    cur_state, cur_words, guessed = do_turn(test_game, cur_state, cur_words)
    print(f"Turn {turn+1}: Guessed '{guessed}'. State: {cur_state}, Remaining: {cur_words}")
    if len(cur_words) == 1:
        break
