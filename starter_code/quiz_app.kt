/*
Project:    Student Quiz App
Difficulty: Beginner
Skills:     Kotlin, JSON parsing, File I/O
Time:       Medium (a weekend)

What you will build:
    A console-based quiz application that loads questions from a JSON
    file, tracks the user's score, and shows a final result with
    correct answers revealed at the end.

How to run:
    kotlinc quiz_app.kt -include-runtime -d quiz_app.jar
    java -jar quiz_app.jar

Learning goals:
    - Defining and using Kotlin data classes
    - Reading and parsing a JSON file
    - Using control flow and loops in Kotlin
    - Tracking state across multiple quiz questions

Roadmap:
    Step 1:  Project is already set up — run it and explore the output
    Step 2:  Complete loadQuestions() to read questions from questions.json
    Step 3:  Complete displayQuestion() to print a question with choices
    Step 4:  Complete checkAnswer() to validate the user's answer
    Step 5:  Complete runQuiz() to loop through all questions
    Step 6:  Complete showResults() to display final score and answers
    Step 7:  Test with at least 5 sample questions in questions.json
*/

// ---------------------------------------------------------------------------
// Data classes
// ---------------------------------------------------------------------------

// Represents a single quiz question with multiple choice options
data class Question(
    val text: String,
    val options: List<String>,
    val correctIndex: Int,
    val explanation: String = ""
)

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// Path to the JSON file containing quiz questions
const val QUESTIONS_FILE = "questions.json"

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/**
 * Load questions from the JSON file and return them as a list.
 *
 * TODO:
 * 1. Read the file contents using File(QUESTIONS_FILE).readText()
 * 2. Parse the JSON manually or use a simple split approach
 * 3. Create Question objects from the parsed data
 * 4. Return the list of Question objects
 * 5. Return an empty list if the file does not exist
 */
fun loadQuestions(): List<Question> {
    val questions = mutableListOf<Question>()

    // --- Write your file loading code here ---

    return questions
}

/**
 * Display a single question with its options to the console.
 *
 * TODO:
 * 1. Print the question number and question text
 * 2. Loop through options and print each with a letter label
 *    Example: A. Paris   B. London   C. Berlin
 * 3. Prompt the user to enter their answer letter
 */
fun displayQuestion(question: Question, number: Int) {

    // --- Write your display code here ---

}

/**
 * Check if the user's answer matches the correct answer.
 *
 * Args:
 *   question: The Question object being answered
 *   answer: The user's input as a single letter (A, B, C, D)
 *
 * Returns true if the answer is correct, false otherwise
 *
 * TODO:
 * 1. Convert the answer letter to an index (A=0, B=1, C=2, D=3)
 * 2. Compare with question.correctIndex
 * 3. Return true if they match, false otherwise
 * 4. Handle invalid input gracefully
 */
fun checkAnswer(question: Question, answer: String): Boolean {

    // --- Write your answer checking code here ---

    return false
}

/**
 * Run the full quiz by looping through all questions.
 *
 * Returns the number of correct answers as an Int.
 *
 * TODO:
 * 1. Loop through each question with its index
 * 2. Call displayQuestion() to show the question
 * 3. Read the user's input from the console
 * 4. Call checkAnswer() to check if it is correct
 * 5. Print "Correct!" or "Wrong!" after each answer
 * 6. Keep a running score counter
 * 7. Return the final score
 */
fun runQuiz(questions: List<Question>): Int {
    var score = 0

    // --- Write your quiz loop here ---

    return score
}

/**
 * Display the final results after the quiz ends.
 *
 * TODO:
 * 1. Print the total score out of total questions
 * 2. Calculate and print the percentage score
 * 3. Loop through all questions and show the correct answer for each
 * 4. Print the explanation if one exists
 */
fun showResults(questions: List<Question>, score: Int) {

    // --- Write your results display code here ---

}

// ---------------------------------------------------------------------------
// Entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

fun main() {
    println("=================================")
    println("       Student Quiz App")
    println("=================================\n")

    val questions = loadQuestions()

    if (questions.isEmpty()) {
        println("No questions found. Please check $QUESTIONS_FILE")
        return
    }

    println("Loaded ${questions.size} questions. Let's begin!\n")

    val score = runQuiz(questions)
    showResults(questions, score)
}