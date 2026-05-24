# password_checker.py
# Starter code template for DevPath Password Strength Checker project.
#
# Your task is to implement a password complexity checker.
# Follow the comments and function signature below.

import re
import getpass

def check_password_strength(password):
    """
    Evaluate the strength of a password based on several rules:
      - Length: at least 8 characters
      - Contain at least one uppercase letter
      - Contain at least one lowercase letter
      - Contain at least one number
      - Contain at least one special character (e.g. !, @, #, $, %, etc.)
    
    Returns:
      dict: {
        'strength': 'Weak' | 'Medium' | 'Strong',
        'score': int (0 to 5),
        'suggestions': list of str (improvements)
      }
    """
    suggestions = []
    score = 0

    # TODO: Implement length check (score +1 if length >= 8, otherwise add suggestion)
    
    # TODO: Implement uppercase check (score +1 if contains uppercase, otherwise add suggestion)
    
    # TODO: Implement lowercase check (score +1 if contains lowercase, otherwise add suggestion)
    
    # TODO: Implement digit check (score +1 if contains number, otherwise add suggestion)
    
    # TODO: Implement special character check (score +1 if contains symbol, otherwise add suggestion)

    # Determine qualitative strength based on total score:
    #   - Score < 3: 'Weak'
    #   - Score 3 or 4: 'Medium'
    #   - Score 5: 'Strong'
    strength = 'Weak'
    
    return {
        'strength': strength,
        'score': score,
        'suggestions': suggestions
    }

if __name__ == '__main__':
    print("--- Password Strength Checker CLI ---")
    user_pass = getpass.getpass("Enter a password to test: ")
    result = check_password_strength(user_pass)
    print(f"Strength: {result['strength']} (Score: {result['score']}/5)")
    if result['suggestions']:
        print("Suggestions for improvement:")
        for s in result['suggestions']:
            print(f" - {s}")
