/*
Project:    Personal Finance Dashboard
Difficulty: Intermediate
Skills:     TypeScript, HTML, CSS, Chart.js
Time:       High (several days)

What you will build:
    A web-based personal finance tracker where users can add income
    and expense entries, view their balance summary, and see a spending
    breakdown chart powered by Chart.js.

How to run:
    npx tsc finance_dashboard.ts
    Open index.html in your browser

Learning goals:
    - Defining TypeScript interfaces and types
    - Manipulating the DOM with TypeScript
    - Working with arrays and array methods
    - Integrating a third-party chart library

Roadmap:
    Step 1:  Project is already set up — open index.html and explore
    Step 2:  Complete addTransaction() to add entries to the list
    Step 3:  Complete deleteTransaction() to remove an entry by id
    Step 4:  Complete calculateBalance() to compute total balance
    Step 5:  Complete renderTransactions() to display the list in DOM
    Step 6:  Complete renderChart() to show the spending pie chart
    Step 7:  Test with multiple income and expense entries
*/

// ---------------------------------------------------------------------------
// Interfaces and types
// ---------------------------------------------------------------------------

// Represents a single financial transaction
interface Transaction {
    id: number;
    description: string;
    amount: number;
    type: "income" | "expense";
    category: string;
    date: string;
}

// ---------------------------------------------------------------------------
// State — the application's data lives here
// ---------------------------------------------------------------------------

// All transactions stored in memory
let transactions: Transaction[] = [];

// Counter used to assign unique IDs to new transactions
let nextId: number = 1;

// ---------------------------------------------------------------------------
// Core functions — complete the TODOs to make each one work
// ---------------------------------------------------------------------------

/**
 * Add a new transaction to the transactions array.
 *
 * @param description - What the transaction is for
 * @param amount - The transaction amount (always positive)
 * @param type - Either "income" or "expense"
 * @param category - Category like "Food", "Salary", "Transport"
 *
 * TODO:
 * 1. Create a new Transaction object using the parameters
 * 2. Use nextId for the id field and increment nextId after
 * 3. Use new Date().toLocaleDateString() for the date
 * 4. Push the new transaction into the transactions array
 * 5. Call renderTransactions() and renderChart() to update the UI
 */
function addTransaction(
    description: string,
    amount: number,
    type: "income" | "expense",
    category: string
): void {

    // --- Write your add transaction code here ---

}

/**
 * Delete a transaction from the array by its id.
 *
 * @param id - The id of the transaction to remove
 *
 * TODO:
 * 1. Use transactions.filter() to remove the transaction with matching id
 * 2. Update the transactions array with the filtered result
 * 3. Call renderTransactions() and renderChart() to update the UI
 */
function deleteTransaction(id: number): void {

    // --- Write your delete code here ---

}

/**
 * Calculate and return the current balance.
 *
 * Returns an object with totalIncome, totalExpenses, and balance.
 *
 * TODO:
 * 1. Loop through transactions and sum all income amounts
 * 2. Loop through transactions and sum all expense amounts
 * 3. Calculate balance as totalIncome minus totalExpenses
 * 4. Return an object with all three values
 */
function calculateBalance(): {
    totalIncome: number;
    totalExpenses: number;
    balance: number;
} {

    // --- Write your balance calculation here ---

    return { totalIncome: 0, totalExpenses: 0, balance: 0 };
}

/**
 * Render all transactions as a list in the DOM.
 *
 * TODO:
 * 1. Get the transaction list element from the DOM by id
 * 2. Clear its current innerHTML
 * 3. If transactions is empty show a "No transactions yet" message
 * 4. Loop through transactions and create a div for each one
 * 5. Show description, amount, category, date, and a delete button
 * 6. Add a click handler on the delete button calling deleteTransaction()
 * 7. Also update the balance summary display using calculateBalance()
 */
function renderTransactions(): void {

    // --- Write your render code here ---

}

/**
 * Render a pie chart showing spending by category using Chart.js.
 *
 * TODO:
 * 1. Filter transactions to get only expenses
 * 2. Group expenses by category and sum amounts per category
 * 3. Get the canvas element from the DOM by id
 * 4. Destroy any existing chart instance before creating a new one
 * 5. Create a new Chart with type "pie"
 * 6. Pass category names as labels and summed amounts as data
 */
function renderChart(): void {

    // --- Write your chart rendering code here ---

}

// ---------------------------------------------------------------------------
// Event listeners — already complete, no changes needed here
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("transaction-form");

    form?.addEventListener("submit", (e) => {
        e.preventDefault();

        const description = (document.getElementById("description") as HTMLInputElement).value.trim();
        const amount = parseFloat((document.getElementById("amount") as HTMLInputElement).value);
        const type = (document.getElementById("type") as HTMLSelectElement).value as "income" | "expense";
        const category = (document.getElementById("category") as HTMLInputElement).value.trim();

        if (!description || isNaN(amount) || amount <= 0 || !category) {
            alert("Please fill in all fields with valid values.");
            return;
        }

        addTransaction(description, amount, type, category);
        (form as HTMLFormElement).reset();
    });

    renderTransactions();
    renderChart();
});