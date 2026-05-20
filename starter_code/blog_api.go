/*
Project:    Personal Blog REST API
Difficulty: Beginner
Skills:     Go, net/http package, encoding/json package
Time:       Medium (a weekend)

What you will build:
    A simple REST API in Go that handles blog posts. Users can create,
    read, update, and delete blog posts through HTTP endpoints.

How to run:
    go run blog_api.go
    API available at http://localhost:8080

Learning goals:
    - Setting up an HTTP server in Go
    - Defining structs and working with JSON
    - Handling different HTTP methods
    - Building and testing REST endpoints

Roadmap:
    Step 1:  Project is already set up — run it and test with curl
    Step 2:  Complete getAllPosts() to return all posts as JSON
    Step 3:  Complete getPostByID() to return a single post
    Step 4:  Complete createPost() to add a new post
    Step 5:  Complete deletePost() to remove a post by ID
    Step 6:  Complete the router to connect handlers to routes
    Step 7:  Test all endpoints using curl or Postman
*/

package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
)

// ---------------------------------------------------------------------------
// Data structures
// ---------------------------------------------------------------------------

// BlogPost represents a single blog post entry
type BlogPost struct {
	ID      int    `json:"id"`
	Title   string `json:"title"`
	Content string `json:"content"`
	Author  string `json:"author"`
}

// ---------------------------------------------------------------------------
// In-memory storage
// ---------------------------------------------------------------------------

// posts stores all blog posts in memory
var posts = map[int]BlogPost{}

// nextID tracks the next available post ID
var nextID = 1

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

// getAllPosts returns all blog posts as a JSON array.
//
// TODO:
//  1. Convert the posts map values into a slice
//  2. Encode the slice as JSON using json.NewEncoder
//  3. Set the Content-Type header to "application/json"
//  4. Write the JSON response with status 200
func getAllPosts(w http.ResponseWriter, r *http.Request) {

	// --- Write your get all posts code here ---

}

// getPostByID returns a single post matching the given ID.
//
// TODO:
//  1. Extract the ID from the URL path (last segment)
//  2. Convert it to an integer using strconv.Atoi
//  3. Look up the post in the posts map
//  4. If not found return a 404 JSON error response
//  5. If found encode and return the post as JSON
func getPostByID(w http.ResponseWriter, r *http.Request, id int) {

	// --- Write your get single post code here ---

}

// createPost reads a JSON body and adds a new post to the map.
//
// TODO:
//  1. Decode the request body into a BlogPost struct
//  2. Validate that title and content are not empty
//  3. Assign the nextID to the new post and increment nextID
//  4. Store the new post in the posts map
//  5. Return the created post as JSON with status 201
func createPost(w http.ResponseWriter, r *http.Request) {

	// --- Write your create post code here ---

}

// deletePost removes a post by ID from the map.
//
// TODO:
//  1. Extract and parse the ID from the URL path
//  2. Check if the post exists in the map
//  3. If not found return a 404 JSON error
//  4. Delete the post using delete(posts, id)
//  5. Return a success message with status 200
func deletePost(w http.ResponseWriter, r *http.Request, id int) {

	// --- Write your delete post code here ---

}

// ---------------------------------------------------------------------------
// Router and entry point — already complete, no changes needed here
// ---------------------------------------------------------------------------

func router(w http.ResponseWriter, r *http.Request) {
	path := strings.TrimPrefix(r.URL.Path, "/posts")
	path = strings.TrimSuffix(path, "/")

	if path == "" {
		switch r.Method {
		case http.MethodGet:
			getAllPosts(w, r)
		case http.MethodPost:
			createPost(w, r)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
		return
	}

	idStr := strings.TrimPrefix(path, "/")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, "Invalid post ID", http.StatusBadRequest)
		return
	}

	switch r.Method {
	case http.MethodGet:
		getPostByID(w, r, id)
	case http.MethodDelete:
		deletePost(w, r, id)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func main() {
	http.HandleFunc("/posts", router)
	http.HandleFunc("/posts/", router)

	fmt.Println("Blog API running at http://localhost:8080")
	fmt.Println("Endpoints:")
	fmt.Println("  GET    /posts       — list all posts")
	fmt.Println("  POST   /posts       — create a post")
	fmt.Println("  GET    /posts/{id}  — get one post")
	fmt.Println("  DELETE /posts/{id}  — delete a post")

	http.ListenAndServe(":8080", nil)
}