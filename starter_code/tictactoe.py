"""
tictactoe.py
============
Project:    Tic-Tac-Toe CLI
Difficulty: Beginner
Skills:     Python
Time:       Medium (a weekend)

What you will build:
    A two-player Tic-Tac-Toe game that runs entirely in the terminal. Players
    take turns entering a cell number (1-9) to place their mark. The board is
    printed after every move. The game automatically detects wins across all
    rows, columns, and diagonals, and correctly identifies a draw when the
    board is full with no winner.

How to run:
    python tictactoe.py

Board layout — players type the number for their chosen cell:

     1 | 2 | 3
    ---+---+---
     4 | 5 | 6
    ---+---+---
     7 | 8 | 9

Learning goals:
    - Representing a 3x3 grid as a flat Python list of 9 elements
    - Using list indexing to read and update grid cells
    - Detecting patterns in a list (win conditions)
    - Writing clean, single-responsibility helper functions
    - Structuring an alternating-turn game loop

Roadmap:
    Step 1:  Run the script and study the board layout and WIN_PATTERNS above
    Step 2:  Complete display_board() to print the current 3x3 grid
    Step 3:  Complete get_player_move() to prompt and validate a cell choice
    Step 4:  Complete check_winner() to detect all eight win patterns
    Step 5:  Complete check_draw() to detect a full board with no winner
    Step 6:  Complete play_game() to run the full alternating-turn game loop
    Step 7:  Test every win direction (3 rows, 3 columns, 2 diagonals) and draw
"""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The two players, in turn order — X always goes first
PLAYERS = ["X", "O"]

# Each inner list is a set of board indices that form a winning line.
# The board is a flat list of 9 elements mapped like this:
#   index 0 | index 1 | index 2
#   ---------+---------+---------
#   index 3 | index 4 | index 5
#   ---------+---------+---------
#   index 6 | index 7 | index 8
WIN_PATTERNS = [
    [0, 1, 2],  # top row
    [3, 4, 5],  # middle row
    [6, 7, 8],  # bottom row
    [0, 3, 6],  # left column
    [1, 4, 7],  # middle column
    [2, 5, 8],  # right column
    [0, 4, 8],  # diagonal: top-left to bottom-right
    [2, 4, 6],  # diagonal: top-right to bottom-left
]


# ---------------------------------------------------------------------------
# Core functions — complete the TODOs to make each one work
# ---------------------------------------------------------------------------

def create_board():
    """
    Return a fresh 9-element list representing an empty board.

    Each cell starts as its position number as a string ("1" through "9")
    so players can see which number to type before any marks are placed.

    Returns:
        list[str]: ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    TODO:
        Return a list of the strings "1" through "9".
        Tip: [str(i) for i in range(1, 10)]
    """
    # --- Write your code here ---

    return []


def display_board(board):
    """
    Print the current board state as a formatted 3x3 grid.

    Args:
        board (list[str]): The 9-element board list.

    Expected output (with X in cell 5, O in cell 1):

         O | 2 | 3
        ---+---+---
         4 | X | 6
        ---+---+---
         7 | 8 | 9

    TODO:
        1. Print a blank line before the board for readability.
        2. Print row 1 using indices 0, 1, 2:
               f" {board[0]} | {board[1]} | {board[2]}"
        3. Print the separator: "---+---+---"
        4. Print row 2 using indices 3, 4, 5.
        5. Print the separator again.
        6. Print row 3 using indices 6, 7, 8.
        7. Print a blank line after the board.
    """
    # --- Write your code here ---

    pass


def get_player_move(board, player):
    """
    Prompt the current player to choose a cell and validate their input.

    A move is valid when:
    - The input converts to an integer between 1 and 9.
    - The chosen cell has not already been taken (i.e., board[index] is
      not "X" or "O").

    Args:
        board (list[str]): The current board state.
        player (str):      "X" or "O" — shown in the prompt so each player
                           knows whose turn it is.

    Returns:
        int: A 0-based index (0-8) for the chosen cell.

    TODO:
        1. Use a while True loop.
        2. Prompt: f"Player {player}, choose a cell (1-9): "
        3. Try converting input to int. On ValueError print:
               "Please enter a number between 1 and 9."
           and continue.
        4. Check the value is between 1 and 9. If not, print the same message
           and continue.
        5. Convert to 0-based index: index = choice - 1
        6. Check board[index] is not "X" or "O". If taken, print:
               "That cell is already taken. Choose another."
           and continue.
        7. Return index when all checks pass.
    """
    # --- Write your code here ---

    return 0


def check_winner(board, player):
    """
    Return True if the given player has completed any winning line.

    Args:
        board (list[str]): The current board state.
        player (str):      "X" or "O" — the player to check.

    Returns:
        bool: True if player occupies all three cells in at least one
              entry from WIN_PATTERNS. False otherwise.

    TODO:
        Loop through WIN_PATTERNS. For each pattern [a, b, c], check:
            board[a] == board[b] == board[c] == player
        Return True as soon as a matching pattern is found.
        Return False after the loop if no pattern matched.
    """
    # --- Write your code here ---

    return False


def check_draw(board):
    """
    Return True if the board is completely filled with no empty cells left.

    An empty cell still holds a digit string ("1" through "9").
    A taken cell holds "X" or "O".

    Args:
        board (list[str]): The current board state.

    Returns:
        bool: True if every cell in board is "X" or "O" (no digits remain).

    TODO:
        Check whether any cell in board is still a digit (use cell.isdigit()).
        If any cell is a digit the board is not full — return False.
        If no cell is a digit the board is full — return True.
    """
    # --- Write your code here ---

    return False


def play_game():
    """
    Run one complete game of Tic-Tac-Toe.

    Alternates turns between "X" and "O" until one player wins or the board
    is full with no winner (a draw).

    Returns:
        str | None: The winning player ("X" or "O"), or None for a draw.

    TODO:
        1. Call create_board() to get a fresh board.
        2. Loop with a turn counter from 0 to 8 (range(9) covers all cells):
               a. Determine the current player: PLAYERS[turn % 2]
                  (turn 0, 2, 4 ... -> "X";  turn 1, 3, 5 ... -> "O")
               b. Call display_board(board) to show the current state.
               c. Call get_player_move(board, player) to get the chosen index.
               d. Place the mark: board[index] = player
               e. Call check_winner(board, player). If True:
                      - Call display_board(board) one final time.
                      - Print: f"Player {player} wins!"
                      - Return player.
               f. Call check_draw(board). If True:
                      - Call display_board(board) one final time.
                      - Print: "It's a draw!"
                      - Return None.
    """
    # --- Write your game loop here ---

    return None


# ---------------------------------------------------------------------------
# Entry point — already complete, no changes needed here
# ---------------------------------------------------------------------------

def main():
    """Run the game and offer a play-again prompt after each round."""
    print("\n" + "=" * 35)
    print("         Tic-Tac-Toe")
    print("=" * 35)
    print("\nCell layout:")
    print(" 1 | 2 | 3")
    print("---+---+---")
    print(" 4 | 5 | 6")
    print("---+---+---")
    print(" 7 | 8 | 9")

    while True:
        play_game()
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("\nThanks for playing!\n")
            break


if __name__ == "__main__":
    main()
