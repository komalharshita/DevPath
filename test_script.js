const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const html = fs.readFileSync('templates/index.html', 'utf8');
const dom = new JSDOM(html, { runScripts: "dangerously", resources: "usable" });

const scriptContent = fs.readFileSync('static/script.js', 'utf8');
const scriptEl = dom.window.document.createElement("script");
scriptEl.textContent = scriptContent;

dom.window.onerror = function(msg, url, line, col, error) {
    console.error(`JSDOM Error: ${msg} at line ${line}`);
};

try {
    dom.window.document.body.appendChild(scriptEl);
    console.log("Script executed without throwing uncaught exceptions!");
} catch (e) {
    console.error("Caught exception:", e);
}
