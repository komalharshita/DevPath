const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const html = fs.readFileSync('templates/index.html', 'utf8');
const dom = new JSDOM(html, { runScripts: "dangerously", resources: "usable" });

dom.window.requestAnimationFrame = function(callback) { setTimeout(callback, 16); };

let logs = [];
dom.window.console.log = function(...args) { logs.push(args.join(" ")); };

const scriptContent = fs.readFileSync('/tmp/backup_script.js', 'utf8');
const scriptEl = dom.window.document.createElement("script");
scriptEl.textContent = scriptContent;

dom.window.onerror = function(msg, url, line, col, error) {
    console.error(`JSDOM Error: ${msg} at line ${line}`);
};

try {
    dom.window.document.body.appendChild(scriptEl);
    console.log("JSDOM execution finished");
    console.log("Logs:", logs);
} catch (e) {
    console.error("Caught exception:", e);
}
