/*
Project:    Number Guessing Game
Difficulty: Beginner
Skills:     Rust, rand crate, std::io
Time:       Low (a few hours)

What you will build:
    A classic number guessing game where the program picks a random
    number and the user guesses until they get it right. The program
    gives higher or lower hints and tracks attempts.

How to run:
    cargo run

Learning goals:
    - Reading user input in Rust
    - Using the rand crate for random number generation
    - Rust ownership and borrowing basics
    - Using match expressions and control flow

Roadmap:
    Step 1:  Project is already set up — run it and explore the output
    Step 2:  Complete generate_number() to pick a random number
    Step 3:  Complete get_user_guess() to read and parse user input
    Step 4:  Complete check_guess() to compare guess with target
    Step 5:  Complete play_game() to run the full game loop
    Step 6:  Complete show_result() to display final attempts count
    Step 7:  Test with different ranges and edge cases
*/

use std::io;
use std::io::Write;

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// The range for the random number (inclusive on both ends)
const MIN_NUMBER: u32 = 1;
const MAX_NUMBER: u32 = 100;

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/// Generate a random number between MIN_NUMBER and MAX_NUMBER inclusive.
///
/// TODO:
/// 1. Add rand = "0.8" to your Cargo.toml dependencies
/// 2. Use rand::Rng trait and thread_rng() to generate the number
/// 3. Use gen_range(MIN_NUMBER..=MAX_NUMBER) to get the value
/// 4. Return the generated number
fn generate_number() -> u32 {

    // --- Write your random number generation code here ---

    0 // replace this with your generated number
}

/// Read a guess from the user and return it as u32.
/// Keep asking until the user enters a valid number.
///
/// TODO:
/// 1. Print a prompt asking the user to enter a guess
/// 2. Read a line from stdin using io::stdin().read_line()
/// 3. Trim the input and parse it to u32
/// 4. If parsing fails, print an error and ask again
/// 5. Return the valid parsed number
fn get_user_guess() -> u32 {

    // --- Write your input reading code here ---

    0 // replace this with the actual user input
}

/// Compare the user's guess with the target number.
/// Returns "correct", "too_high", or "too_low" as a &str.
///
/// TODO:
/// 1. Use a match expression or if/else to compare guess and target
/// 2. Return "correct" if they are equal
/// 3. Return "too_high" if guess is greater than target
/// 4. Return "too_low" if guess is less than target
fn check_guess(guess: u32, target: u32) -> &'static str {

    // --- Write your comparison code here ---

    "too_low" // replace this with your actual result
}

/// Run the full game loop until the user guesses correctly.
/// Returns the number of attempts the user took.
///
/// TODO:
/// 1. Call generate_number() to get the target
/// 2. Print a welcome message with the number range
/// 3. Loop until the user guesses correctly
/// 4. Call get_user_guess() to get each guess
/// 5. Call check_guess() and print a hint based on the result
/// 6. Count each attempt
/// 7. Break the loop when the guess is correct
/// 8. Return the total attempt count
fn play_game() -> u32 {
    let attempts = 0;

    // --- Write your game loop here ---

    attempts
}

/// Display the final result message with the number of attempts.
///
/// TODO:
/// 1. Print a congratulations message
/// 2. Print the number of attempts taken
/// 3. Print a rating based on attempts
///    Example: 1-3 attempts = "Amazing!", 4-6 = "Good job!", 7+ = "Keep practicing!"
fn show_result(attempts: u32) {

    // --- Write your result display code here ---

}

// ---------------------------------------------------------------------------
// Entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

fn main() {
    println!("=================================");
    println!("     Number Guessing Game");
    println!("=================================");
    println!("I'm thinking of a number between {} and {}", MIN_NUMBER, MAX_NUMBER);

    let attempts = play_game();
    show_result(attempts);
}