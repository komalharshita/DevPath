const users = [];

function joinChat(username) {
    users.push(username);
    console.log(`${username} joined the chat`);
}

function sendMessage(username, message) {
    console.log(`${username}: ${message}`);
}

joinChat("Vikas");
sendMessage("Vikas", "Hello World!");