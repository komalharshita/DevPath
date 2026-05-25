# Starter code: Number Guessing Game
import random

def play_game():
    """Main game function."""
    number = random.randint(1, 100)
    attempts = 0

    print("Welcome to the Number Guessing Game!")
    print("I am thinking of a number between 1 and 100.")

    # TODO: Write a loop to take user input
    # TODO: Compare guess with number
    # TODO: Give hints: too high or too low
    # TODO: Count attempts
    # TODO: Display win message

if __name__ == "__main__":
    play_game()