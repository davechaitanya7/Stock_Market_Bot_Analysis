# Code Reviewer Subagent

## Purpose
Review code changes for quality, security, maintainability, and adherence to best practices before merging.

## When to Invoke
- Before creating a PR
- After significant refactoring
- When adding new features
- Security-sensitive changes (auth, API keys, user input handling)

## Prompt Template

```
Review the following code changes for:

1. **Security Issues**
   - SQL injection, XSS, CSRF vulnerabilities
   - Hardcoded secrets or API keys
   - Insecure authentication/authorization
   - Input validation gaps

2. **Code Quality**
   - Function complexity (should be < 50 lines)
   - Duplicate code patterns
   - Missing error handling
   - Inconsistent naming conventions

3. **Maintainability**
   - Missing docstrings for public functions
   - Unclear variable/function names
   - Magic numbers without constants
   - Tight coupling between modules

4. **Performance**
   - N+1 queries
   - Unnecessary loops
   - Missing caching opportunities
   - Memory leaks

5. **Testing Gaps**
   - Untested edge cases
   - Missing unit tests for new functions
   - Integration test coverage

## Context
- File(s) changed: [list files or use git diff]
- Type of change: [bugfix/feature/refactor]
- Risk level: [low/medium/high]

## Output Format
- CRITICAL: Must fix before merge (security bugs, breaking changes)
- WARNING: Should fix (code quality, potential issues)
- SUGGESTION: Nice to have (optimizations, style)

Provide specific line numbers and suggested fixes.
```

## Files to Focus On
- `backend/main.py` - API endpoints, input validation
- `backend/data/fetcher.py` - External API calls, error handling
- `backend/analysis/indicators.py` - Calculation accuracy
- `frontend/src/App.jsx` - User input handling, API calls
- `frontend/src/api/client.js` - Error handling, request validation

## Example Invocation
```
Agent(subagent_type="Code_Reviewer", prompt="Review backend/main.py for security issues in the order creation and approval endpoints. Focus on input validation and potential injection vulnerabilities.")
```
