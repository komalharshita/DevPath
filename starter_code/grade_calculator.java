/*
Project:    Student Grade Calculator
Difficulty: Beginner
Skills:     Java, Scanner class, Arrays
Time:       Low (a few hours)

What you will build:
    A Java console app that takes student marks as input, calculates
    the average score, and assigns a letter grade automatically.

How to run:
    javac grade_calculator.java
    java grade_calculator

Learning goals:
    - Defining classes and methods in Java
    - Using the Scanner class for user input
    - Working with arrays to store multiple values
    - Implementing grade calculation logic

Roadmap:
    Step 1:  Project is already set up — run it and explore the output
    Step 2:  Complete inputMarks() to read marks from the user
    Step 3:  Complete calculateAverage() to compute the mean score
    Step 4:  Complete assignGrade() to return the correct letter grade
    Step 5:  Complete printResult() to display the full summary
    Step 6:  Test with different sets of marks including edge cases
    Step 7:  Add input validation to reject marks outside 0-100
*/

import java.util.Scanner;

public class grade_calculator {

    // -----------------------------------------------------------------------
    // Configuration
    // -----------------------------------------------------------------------

    // Number of subjects to enter marks for
    static final int SUBJECT_COUNT = 5;

    // Subject names shown to the user
    static final String[] SUBJECTS = {
        "Mathematics", "Science", "English", "History", "Computer Science"
    };

    // -----------------------------------------------------------------------
    // Core methods — complete the TODOs to make each one work
    // -----------------------------------------------------------------------

    /**
     * Read marks for each subject from the user.
     *
     * @param scanner The Scanner object for reading input
     * @return An array of marks as doubles
     *
     * TODO:
     * 1. Create a double array of size SUBJECT_COUNT
     * 2. Loop through SUBJECTS and prompt the user for each mark
     * 3. Read the mark using scanner.nextDouble()
     * 4. Store each mark in the array
     * 5. Return the completed array
     */
    static double[] inputMarks(Scanner scanner) {
        double[] marks = new double[SUBJECT_COUNT];

        // --- Write your input code here ---

        return marks;
    }

    /**
     * Calculate the average of all marks in the array.
     *
     * @param marks Array of subject marks
     * @return The average as a double
     *
     * TODO:
     * 1. Create a sum variable starting at 0
     * 2. Loop through the marks array and add each value to sum
     * 3. Divide sum by marks.length to get the average
     * 4. Return the average
     */
    static double calculateAverage(double[] marks) {

        // --- Write your average calculation here ---

        return 0.0;
    }

    /**
     * Assign a letter grade based on the average score.
     *
     * @param average The calculated average mark
     * @return A letter grade as a String
     *
     * Grading scale:
     *   90 and above  -> "A"
     *   80 to 89      -> "B"
     *   70 to 79      -> "C"
     *   60 to 69      -> "D"
     *   Below 60      -> "F"
     *
     * TODO:
     * 1. Use if/else if statements to check the average against the scale
     * 2. Return the correct letter grade string
     */
    static String assignGrade(double average) {

        // --- Write your grade assignment code here ---

        return "F";
    }

    /**
     * Print the full result summary for the student.
     *
     * @param name    The student's name
     * @param marks   Array of subject marks
     * @param average The calculated average
     * @param grade   The assigned letter grade
     *
     * TODO:
     * 1. Print a formatted header with the student name
     * 2. Loop through SUBJECTS and print each subject with its mark
     * 3. Print the average score rounded to 2 decimal places
     * 4. Print the final letter grade
     * 5. Print a pass or fail message based on the grade
     */
    static void printResult(String name, double[] marks, double average, String grade) {

        // --- Write your result printing code here ---

    }

    // -----------------------------------------------------------------------
    // Entry point — already complete, no changes needed here
    // -----------------------------------------------------------------------

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=================================");
        System.out.println("    Student Grade Calculator");
        System.out.println("=================================\n");

        System.out.print("Enter student name: ");
        String name = scanner.nextLine().trim();

        double[] marks = inputMarks(scanner);
        double average = calculateAverage(marks);
        String grade = assignGrade(average);

        printResult(name, marks, average, grade);

        scanner.close();
    }
}