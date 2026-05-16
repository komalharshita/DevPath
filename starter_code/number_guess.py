"""
number_guess.py
===============
Project:    Number Guessing Game
Difficulty: Beginner
Skills:     Python, random module
Time:       Low (a few hours)

What you will build:
    A command-line guessing game where the computer picks a secret number and
    the player has a limited number of attempts to guess it. After each guess
    the player receives a "too high" or "too low" hint. A score is shown at
    the end based on how efficiently the player guessed.

How to run:
    python number_guess.py

Learning goals:
    - Generating random integers with random.randint()
    - Validating user input inside a while loop
    - Using if/elif/else to compare values and give feedback
    - Tracking game state (attempts used, score) with simple variables
    - Structuring a replayable game with a play-again loop

Roadmap:
    Step 1:  Run the script and read the constants and function skeletons
    Step 2:  Complete generate_secret() to return a random number in range
    Step 3:  Complete get_valid_guess() to prompt and validate player input
    Step 4:  Complete check_guess() to return "correct", "too_high", or "too_low"
    Step 5:  Complete calculate_score() based on attempts used vs maximum allowed
    Step 6:  Complete play_game() to wire all helpers into one complete round
    Step 7:  Test every path: win on first guess, win on last, run out of guesses
"""

import random


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MIN_NUMBER = 1       # Lowest possible secret number
MAX_NUMBER = 100     # Highest possible secret number
MAX_ATTEMPTS = 7     # Number of guesses allowed per round


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs to make each one work
# ---------------------------------------------------------------------------

def generate_secret(min_num, max_num):
    """
    Pick and return a random integer between min_num and max_num, inclusive.

    Args:
        min_num (int): The lower bound of the range.
        max_num (int): The upper bound of the range.

    Returns:
        int: A random integer in [min_num, max_num].

    TODO:
        Use random.randint(min_num, max_num) to generate and return the number.
    """
    # --- Write your code here ---

    return 0


def get_valid_guess(min_num, max_num):
    """
    Prompt the player for a guess and keep asking until valid input is given.

    A valid guess is an integer in the range [min_num, max_num].
    Non-integer input and out-of-range values each trigger a specific error
    message, and the prompt repeats.

    Args:
        min_num (int): Minimum acceptable guess value.
        max_num (int): Maximum acceptable guess value.

    Returns:
        int: A validated integer guess from the player.

    TODO:
        1. Use a while True loop.
        2. Call input() to get the player's raw input.
        3. Try converting it to int. Catch ValueError for non-integer input
           and print: "Please enter a whole number."
        4. Check that the integer is between min_num and max_num inclusive.
           If out of range, print: f"Please enter a number between {min_num} and {max_num}."
           Then continue the loop.
        5. If valid, return the integer — this exits the loop.
    """
    # --- Write your code here ---

    return 0


def check_guess(guess, secret):
    """
    Compare the player's guess to the secret number.

    Args:
        guess (int):  The player's guess.
        secret (int): The secret number to match.

    Returns:
        str: "correct"  if guess == secret
             "too_high" if guess > secret
             "too_low"  if guess < secret

    TODO:
        Use if/elif/else to compare guess and secret and return the correct string.
    """
    # --- Write your code here ---

    return ""


def calculate_score(attempts_used, max_attempts):
    """
    Return a score from 0 to 100 based on how efficiently the player guessed.

    Formula:
        score = round(((max_attempts - attempts_used) / max_attempts) * 100)

    A player who guesses correctly on the first try scores the maximum.
    A player who uses all their attempts scores 0.

    Args:
        attempts_used (int): How many guesses the player made.
        max_attempts (int):  The maximum guesses allowed per round.

    Returns:
        int: A score in the range [0, 100].

    TODO:
        Implement the formula above and return the result as a rounded integer.
    """
    # --- Write your code here ---

    return 0


def play_game():
    """
    Run one complete round of the guessing game.

    The round ends when the player guesses correctly or exhausts all attempts.
    Prints feedback after each guess and a final result message.

    Returns:
        bool: True if the player guessed correctly, False if they ran out.

    TODO:
        1. Call generate_secret(MIN_NUMBER, MAX_NUMBER) to get the secret.
        2. Set attempts_used = 0.
        3. Loop while attempts_used < MAX_ATTEMPTS:
               a. Print remaining attempts:
                      remaining = MAX_ATTEMPTS - attempts_used
                      print(f"Attempts remaining: {remaining}")
               b. Call get_valid_guess(MIN_NUMBER, MAX_NUMBER) to get a guess.
               c. Increment attempts_used by 1.
               d. Call check_guess(guess, secret) to get the result string.
               e. If result == "correct":
                      - Print a congratulations message showing attempts_used.
                      - Call calculate_score(attempts_used, MAX_ATTEMPTS).
                      - Print the score.
                      - Return True.
               f. If result == "too_high", print "Too high! Try lower."
               g. If result == "too_low",  print "Too low! Try higher."
        4. After the loop (no correct guess): reveal the secret, print a
           "better luck next time" message, and return False.
    """
    print(f"\nI'm thinking of a number between {MIN_NUMBER} and {MAX_NUMBER}.")
    print(f"You have {MAX_ATTEMPTS} attempts. Good luck!\n")

    # --- Write your game loop here ---

    return False


# ---------------------------------------------------------------------------
# Entry point — already complete, no changes needed here
# ---------------------------------------------------------------------------

def main():
    """Run the game and offer a play-again prompt after each round."""
    print("\n" + "=" * 35)
    print("     Number Guessing Game")
    print("=" * 35)

    while True:
        play_game()
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("\nThanks for playing. Goodbye!\n")
            break


if __name__ == "__main__":
    main()
