# Security Considerations for GitHub Export Feature

The GitHub Repository Export feature (Issue #1180) expands the application's GitHub OAuth scope to include `public_repo`. This allows DevPath to create new repositories on the user's behalf to easily distribute starter code.

## OAuth Scope & Token Handling

1. **Scope Limitation**: We request only the `public_repo` scope, which grants read/write access to public repositories. We **do not** request `repo` (which would grant access to private repositories) or any organization administrative scopes.
2. **Token Storage**: The OAuth access token is stored **temporarily** in the user's Flask session cookie. 
3. **Session Security**: 
   - The Flask session is cryptographically signed using the application's `SECRET_KEY`, preventing end-users from tampering with or extracting the raw token.
   - The token is **never persisted to the database**. When the user logs out or the session expires, the token is destroyed.
4. **Failure Handling**:
   - If the GitHub API returns a `401 Unauthorized` (e.g., if the user revokes the token from their GitHub settings), the application will immediately pop the token from the session and redirect the user to log in again.

## Protection against CSRF

The POST route for exporting a repository (`/project/<id>/export_github`) is protected against Cross-Site Request Forgery (CSRF).
- The `Flask-WTF` CSRF token is included in the export form.
- The `CSRFProtect(app)` middleware globally validates this token before the export logic is reached.
- This prevents malicious external sites from silently forcing authenticated DevPath users to create unwanted repositories.

## API Resilience and Rate Limiting

- **Graceful Degradation**: The export function safely catches GitHub API errors (`403 Rate Limit Exceeded`, `422 Unprocessable Entity` for naming conflicts, etc.) and uses Flask's `flash` mechanism to present human-readable error messages to the user without crashing the application.
- If a repository name conflict occurs (e.g., the user tries to export the same project twice), the application will catch the `422` error during repository creation but proceed to attempt updating the file inside the existing repository (or gently warn the user if it fails).
