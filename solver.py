# coding: utf-8
"""Wordle solving utilities using frequency and entropy strategies."""
from collections import Counter, defaultdict
import math
import random


def load_words(path="words.txt"):
    """Load five-letter candidate words from a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip() for w in f if len(w.strip()) == 5]


def _feedback(guess: str, answer: str) -> str:
    """Return Wordle style feedback pattern for guess against answer.
    'G' for green, 'Y' for yellow, 'B' for gray (black).
    """
    feedback = ['B'] * 5
    answer_remaining = list(answer)

    # First pass for greens
    for i, g_char in enumerate(guess):
        if g_char == answer[i]:
            feedback[i] = 'G'
            answer_remaining[i] = None  # Mark letter used

    # Second pass for yellows
    for i, g_char in enumerate(guess):
        if feedback[i] == 'B' and g_char in answer_remaining:
            feedback[i] = 'Y'
            answer_remaining[answer_remaining.index(g_char)] = None

    return ''.join(feedback)


def select_initial_word(candidates):
    """Select the best initial guess based on position frequencies."""
    position_counts = [Counter() for _ in range(5)]
    overall_counts = Counter()
    for word in candidates:
        for i, ch in enumerate(word):
            position_counts[i][ch] += 1
        overall_counts.update(set(word))  # count unique letters overall

    scores = {}
    total_candidates = len(candidates)
    for word in candidates:
        score = 0.0
        used_letters = set()
        for i, ch in enumerate(word):
            freq_pos = position_counts[i][ch] / total_candidates
            score += freq_pos
            if ch not in used_letters:
                # probability that letter appears elsewhere
                elsewhere = (overall_counts[ch] - position_counts[i][ch]) / total_candidates
                score += 0.5 * elsewhere
                used_letters.add(ch)
        scores[word] = score
    return max(scores, key=scores.get)


def calculate_entropy(guess, candidates):
    """Calculate the entropy of a guess given remaining candidates."""
    pattern_counts = defaultdict(int)
    for word in candidates:
        pattern = _feedback(guess, word)
        pattern_counts[pattern] += 1
    entropy = 0.0
    total = len(candidates)
    for count in pattern_counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def select_best_entropy_word(candidates):
    """Select the candidate with the highest entropy."""
    entropies = {word: calculate_entropy(word, candidates) for word in candidates}
    return max(entropies, key=entropies.get)


def solve_wordle(candidates, correct_word):
    """Iteratively guess words until the correct word is found."""
    remaining = candidates[:]
    attempts = []

    while True:
        if not attempts:
            guess = select_initial_word(remaining)
        else:
            guess = select_best_entropy_word(remaining)
        attempts.append(guess)
        feedback = _feedback(guess, correct_word)
        remaining = [w for w in remaining if _feedback(guess, w) == feedback]
        print(
            f"Attempt {len(attempts)}: {guess} -> {feedback} (remaining: {len(remaining)})"
        )
        if guess == correct_word or not remaining:
            break
    return attempts


if __name__ == "__main__":
    words = load_words()
    answer = random.choice(words)
    print(f"Randomly selected correct word: {answer}")
    solve_wordle(words, correct_word=answer)
