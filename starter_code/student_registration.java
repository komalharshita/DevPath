/*
Project:    Student Registration System
Difficulty: Intermediate
Skills:     Java, Spring Boot, REST API, Maven
Time:       High (several days)

What you will build:
    A Spring Boot REST API that allows students to register, view,
    and delete their profiles. Teaches Spring Boot annotations,
    REST controllers, and basic input validation.

How to run:
    mvn spring-boot:run
    API available at http://localhost:8080

Learning goals:
    - Setting up a Spring Boot project
    - Using @RestController and @RequestMapping annotations
    - Building REST endpoints with @GetMapping and @PostMapping
    - Validating input using @Valid and @NotBlank

Roadmap:
    Step 1:  Create project at https://start.spring.io
    Step 2:  Complete the Student model class
    Step 3:  Complete getAllStudents() endpoint
    Step 4:  Complete registerStudent() endpoint with validation
    Step 5:  Complete deleteStudent() endpoint
    Step 6:  Add proper error handling for duplicate emails
    Step 7:  Test all endpoints using Postman
*/

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

// ---------------------------------------------------------------------------
// Application entry point
// ---------------------------------------------------------------------------

@SpringBootApplication
public class student_registration {
    public static void main(String[] args) {
        SpringApplication.run(student_registration.class, args);
    }
}

// ---------------------------------------------------------------------------
// Student model
// ---------------------------------------------------------------------------

class Student {
    private int id;
    private String name;
    private String email;
    private String course;

    // TODO:
    // 1. Add a constructor that takes name, email, and course
    // 2. Add getters for all fields
    // 3. Add setters for name, email, and course
    // 4. Add a toString() method for easy printing

    // --- Write your constructor, getters, and setters here ---
}

// ---------------------------------------------------------------------------
// REST Controller — complete the TODOs to make each endpoint work
// ---------------------------------------------------------------------------

@RestController
@RequestMapping("/students")
class StudentController {

    // In-memory list to store all registered students
    private List<Student> students = new ArrayList<>();

    // Counter for generating unique student IDs
    private AtomicInteger idCounter = new AtomicInteger(1);

    /**
     * GET /students — Return all registered students as JSON.
     *
     * TODO:
     * 1. Add @GetMapping annotation to this method
     * 2. Return the students list wrapped in ResponseEntity.ok()
     * 3. If the list is empty return an empty list not a 404
     */
    public ResponseEntity<List<Student>> getAllStudents() {

        // --- Write your get all students code here ---

        return ResponseEntity.ok(students);
    }

    /**
     * POST /students — Register a new student.
     *
     * @param student The student object from the request body
     *
     * TODO:
     * 1. Add @PostMapping and @RequestBody annotations
     * 2. Validate that name and email are not empty
     * 3. Check if email already exists to prevent duplicates
     * 4. Assign a new ID using idCounter.getAndIncrement()
     * 5. Add to the students list
     * 6. Return the created student with status 201 CREATED
     */
    public ResponseEntity<?> registerStudent(Student student) {

        // --- Write your registration code here ---

        return ResponseEntity.status(HttpStatus.CREATED).body(student);
    }

    /**
     * DELETE /students/{id} — Delete a student by ID.
     *
     * @param id The ID of the student to delete
     *
     * TODO:
     * 1. Add @DeleteMapping("/{id}") and @PathVariable annotations
     * 2. Find the student with matching ID in the list
     * 3. If not found return 404 with an error message
     * 4. Remove the student from the list
     * 5. Return 200 with a success message
     */
    public ResponseEntity<?> deleteStudent(int id) {

        // --- Write your delete code here ---

        return ResponseEntity.ok("Student deleted successfully");
    }
}