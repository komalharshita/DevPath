/*
Project:    Memory Card Game
Difficulty: Beginner
Skills:     TypeScript, HTML, CSS, DOM API
Time:       Medium (a weekend)

What you will build:
    A browser-based memory card matching game where players flip
    cards to find matching pairs. Tracks attempts and shows a
    win message when all pairs are matched.

How to run:
    npx tsc memory_game.ts
    Open index.html in your browser

Learning goals:
    - Defining TypeScript interfaces
    - Manipulating the DOM with TypeScript
    - Implementing game logic with state management
    - Handling click events and timeouts

Roadmap:
    Step 1:  Project is already set up — open index.html in browser
    Step 2:  Complete createCards() to generate and shuffle the deck
    Step 3:  Complete renderBoard() to display cards in the DOM
    Step 4:  Complete handleCardClick() to manage flip logic
    Step 5:  Complete checkMatch() to compare two flipped cards
    Step 6:  Complete checkWin() to detect when the game is complete
    Step 7:  Test with different grid sizes and edge cases
*/

// ---------------------------------------------------------------------------
// Interfaces
// ---------------------------------------------------------------------------

// Represents a single card in the game
interface Card {
    id: number;
    value: string;
    isFlipped: boolean;
    isMatched: boolean;
}

// ---------------------------------------------------------------------------
// Game state
// ---------------------------------------------------------------------------

// All cards in the current game
let cards: Card[] = [];

// Cards currently face up (max 2 at a time)
let flippedCards: Card[] = [];

// Total number of attempts made
let attempts: number = 0;

// Whether the board is temporarily locked (during mismatch check)
let isLocked: boolean = false;

// The emoji pairs used as card values
const CARD_VALUES: string[] = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"];

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/**
 * Create a shuffled deck of cards with matching pairs.
 *
 * TODO:
 * 1. Create two cards for each value in CARD_VALUES (pairs)
 * 2. Each card needs a unique id, value, isFlipped: false, isMatched: false
 * 3. Shuffle the cards array using Fisher-Yates shuffle algorithm
 * 4. Assign the shuffled array to the cards variable
 */
function createCards(): void {

    // --- Write your card creation and shuffling code here ---

}

/**
 * Render all cards to the game board in the DOM.
 *
 * TODO:
 * 1. Get the game board element by id "game-board"
 * 2. Clear its innerHTML
 * 3. Loop through cards and create a div for each one
 * 4. Add class "card" and "flipped" if card.isFlipped or card.isMatched
 * 5. Show the emoji value only if the card is flipped or matched
 * 6. Add a click event listener calling handleCardClick(card.id)
 * 7. Append each card div to the board
 */
function renderBoard(): void {

    // --- Write your board rendering code here ---

}

/**
 * Handle a card being clicked by the player.
 *
 * @param cardId - The id of the clicked card
 *
 * TODO:
 * 1. If isLocked is true return early (board is locked)
 * 2. Find the card with matching id in the cards array
 * 3. If card is already flipped or matched return early
 * 4. Set card.isFlipped to true
 * 5. Add the card to flippedCards array
 * 6. Call renderBoard() to update the display
 * 7. If flippedCards has 2 cards call checkMatch()
 */
function handleCardClick(cardId: number): void {

    // --- Write your click handling code here ---

}

/**
 * Check if the two flipped cards are a matching pair.
 *
 * TODO:
 * 1. Increment the attempts counter and update display
 * 2. Get both cards from the flippedCards array
 * 3. If their values match set both isMatched to true
 * 4. If they do not match lock the board and set a timeout
 *    to flip them back after 1 second then unlock the board
 * 5. Clear the flippedCards array after checking
 * 6. Call renderBoard() to update the display
 * 7. Call checkWin() to see if the game is complete
 */
function checkMatch(): void {

    // --- Write your match checking code here ---

}

/**
 * Check if all cards have been matched to detect a win.
 *
 * TODO:
 * 1. Check if every card in cards has isMatched set to true
 * 2. If all matched show a win message with the attempt count
 * 3. The win message can be an alert or a DOM element update
 */
function checkWin(): void {

    // --- Write your win detection code here ---

}

// ---------------------------------------------------------------------------
// Initialisation — already complete, no changes needed here
// ---------------------------------------------------------------------------

function startGame(): void {
    attempts = 0;
    flippedCards = [];
    isLocked = false;

    const attemptsDisplay = document.getElementById("attempts");
    if (attemptsDisplay) attemptsDisplay.textContent = "0";

    createCards();
    renderBoard();
}

document.addEventListener("DOMContentLoaded", () => {
    startGame();

    const restartBtn = document.getElementById("restart-btn");
    restartBtn?.addEventListener("click", startGame);
});