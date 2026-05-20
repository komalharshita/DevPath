/*
Project:    Simple Calculator
Difficulty: Beginner
Skills:     C++, iostream, cmath
Time:       Low (a few hours)

What you will build:
    A console-based calculator that performs basic arithmetic
    operations. Handles division by zero and loops for multiple
    calculations.

How to run:
    g++ simple_calculator.cpp -o calculator
    ./calculator

Learning goals:
    - Writing functions in C++
    - Using switch statements for menu selection
    - Handling user input with cin
    - Basic error handling for invalid operations

Roadmap:
    Step 1:  Project is already set up — run it and explore the menu
    Step 2:  Complete add() to return the sum of two numbers
    Step 3:  Complete subtract() to return the difference
    Step 4:  Complete multiply() to return the product
    Step 5:  Complete divide() to handle division including by zero
    Step 6:  Complete displayResult() to print formatted output
    Step 7:  Test with positive, negative, and decimal numbers
*/

#include <iostream>
#include <cmath>

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/**
 * Return the sum of two numbers.
 *
 * TODO:
 * 1. Add a and b together
 * 2. Return the result
 */
double add(double a, double b) {

    // --- Write your addition code here ---

    return 0.0;
}

/**
 * Return the difference of two numbers.
 *
 * TODO:
 * 1. Subtract b from a
 * 2. Return the result
 */
double subtract(double a, double b) {

    // --- Write your subtraction code here ---

    return 0.0;
}

/**
 * Return the product of two numbers.
 *
 * TODO:
 * 1. Multiply a and b
 * 2. Return the result
 */
double multiply(double a, double b) {

    // --- Write your multiplication code here ---

    return 0.0;
}

/**
 * Divide a by b and return the result.
 * Prints an error and returns 0 if b is zero.
 *
 * TODO:
 * 1. Check if b is equal to zero
 * 2. If zero print "Error: Division by zero is not allowed."
 * 3. If zero return 0.0
 * 4. Otherwise return a divided by b
 */
double divide(double a, double b) {

    // --- Write your division code here ---

    return 0.0;
}

/**
 * Display the calculation and its result in a formatted way.
 *
 * @param a        First number
 * @param b        Second number
 * @param op       The operator character (+, -, *, /)
 * @param result   The calculated result
 *
 * TODO:
 * 1. Print the calculation in this format: 5.00 + 3.00 = 8.00
 * 2. Use std::fixed and std::setprecision(2) for formatting
 * 3. Print a blank line after the result for readability
 */
void displayResult(double a, double b, char op, double result) {

    // --- Write your display code here ---

}

/**
 * Show the calculator menu and return the user's choice.
 *
 * TODO:
 * 1. Print the menu options clearly
 * 2. Read the user's choice as an integer
 * 3. Return the choice
 */
int showMenu() {
    int choice;

    // --- Write your menu display and input code here ---

    return choice;
}

// ---------------------------------------------------------------------------
// Entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

int main() {
    std::cout << "=================================" << std::endl;
    std::cout << "       Simple Calculator" << std::endl;
    std::cout << "=================================" << std::endl;

    while (true) {
        int choice = showMenu();

        if (choice == 5) {
            std::cout << "\nGoodbye!\n" << std::endl;
            break;
        }

        if (choice < 1 || choice > 4) {
            std::cout << "Invalid choice. Please enter 1-5." << std::endl;
            continue;
        }

        double a, b;
        std::cout << "Enter first number: ";
        std::cin >> a;
        std::cout << "Enter second number: ";
        std::cin >> b;

        double result = 0.0;
        char op;

        switch (choice) {
            case 1: result = add(a, b);      op = '+'; break;
            case 2: result = subtract(a, b); op = '-'; break;
            case 3: result = multiply(a, b); op = '*'; break;
            case 4: result = divide(a, b);   op = '/'; break;
        }

        displayResult(a, b, op, result);
    }

    return 0;
}