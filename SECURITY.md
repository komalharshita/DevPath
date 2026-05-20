# Security Policy

## Supported Versions

DevPath is currently in active development. Security fixes are applied to
the latest version on the `main` branch only.

| Version | Supported |
|---------|-----------|
| Latest (`main`) | Yes |
| Older branches  | No  |

---

## Reporting a Vulnerability

If you discover a security vulnerability in DevPath, **do not open a public
GitHub Issue**. Public disclosure before a fix is available puts all users
of the project at risk.

**How to report:**

1. Open a [GitHub Security Advisory](https://github.com/komalharshita/devpath/security/advisories/new)
   on this repository (private by default).
2. Include a clear description of the vulnerability, steps to reproduce it,
   and your assessment of its impact.
3. You will receive an acknowledgement within 48 hours.

**What to expect:**

- Acknowledgement within 48 hours of your report
- An assessment of severity and impact within 5 business days
- A fix or mitigation plan shared with you before public disclosure
- Credit in the changelog if you wish to be named

---

## Scope

The following are in scope for security reports:

- Path traversal or file disclosure in the starter code serving routes
- Injection vulnerabilities in the recommendation API
- Information disclosure through error messages
- Dependencies with known CVEs that affect the application

The following are out of scope:

- Vulnerabilities in development-mode Flask debug server (never use in production)
- Self-XSS or issues requiring physical access to the machine
- Denial of service via intentional resource exhaustion

---

## Known Security Considerations

### Development server

`python app.py` starts Flask in debug mode. The debug server must never be
exposed to the public internet. For production deployment, use a WSGI server
such as Gunicorn behind a reverse proxy.

### Path traversal mitigation

The `utils/file_server.py` module resolves `starter_code` paths only inside the
`starter_code/` directory (including one level of subfolders such as
`realtime_chat/app.py`). It rejects `..` segments and uses `os.path.commonpath`
with the real resolved paths so a crafted `starter_code` value in
`projects.json` cannot read arbitrary files outside that folder.

### No user input is stored

DevPath does not persist user input. The recommendation API reads inputs from
the request body, processes them in memory, and returns a response. No session
data, no database, no user-submitted content is written to disk.

---

## Dependency Security

Dependencies are pinned in `requirements.txt`. Contributors should not upgrade
dependencies without a review of the changelog for that package. If you
discover that a pinned dependency has a known CVE, please report it using the
process above.
