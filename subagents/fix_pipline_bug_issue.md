# Fix Pipeline Bug/Issue Subagent

## Purpose
Diagnose and fix CI/CD pipeline failures, build errors, and deployment issues.

## When to Invoke
- CI/CD pipeline fails (GitHub Actions, GitLab CI, etc.)
- Build errors in production/staging
- Deployment rollback scenarios
- Docker container failures
- Dependency conflicts

## Prompt Template

```
Diagnose and fix the following pipeline issue:

1. **Issue Details**
   - Pipeline name/stage: [build/test/deploy]
   - Error message: [paste full error]
   - When it started: [commit hash or timestamp]
   - Recent changes: [list commits or PRs]

2. **Environment**
   - CI platform: [GitHub Actions/GitLab CI/Jenkins/etc.]
   - Python version: [3.12]
   - Node version: [if applicable]
   - Docker image: [if applicable]

3. **Debugging Steps**
   - Check pipeline logs for root cause
   - Identify failing step (install/build/test/deploy)
   - Verify dependency versions
   - Check environment variables/secrets

4. **Fix Categories**
   - Dependency issues: Update requirements.txt or package.json
   - Configuration issues: Fix CI YAML or environment config
   - Code issues: Revert or fix breaking changes
   - Resource issues: Increase timeouts or memory limits

## Common Issues for This Project

**Backend:**
- `pip install` fails: Check requirements.txt syntax, version conflicts
- `uvicorn` import error: Verify fastapi and uvicorn are installed
- yfinance rate limiting: Add retry logic or caching

**Frontend:**
- `npm install` fails: Check Node version, delete node_modules
- Vite build errors: Check import paths, missing dependencies
- CORS errors: Verify backend CORS configuration

**Pipeline:**
- Python version mismatch: Ensure CI uses Python 3.12
- Missing venv: Create virtual environment before pip install
- Port already in use: Change port or kill existing process

## Output Format
- ROOT CAUSE: [one sentence description]
- AFFECTED: [which part of pipeline]
- FIX: [specific steps or code changes]
- PREVENTION: [how to avoid recurrence]
- VERIFICATION: [how to confirm fix works]

## Example Invocation
```
Agent(subagent_type="fix_pipline_bug_issue", prompt="GitHub Actions build is failing at 'pip install -r requirements.txt' with error 'No matching distribution found for pandas-ta>=0.4.47b0'. Fix the requirements.txt or suggest alternative installation method.")
```

## Files to Check
- `.github/workflows/` - CI/CD configuration
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `docker-compose.yml` - Container configuration
- `.env` or environment files - Configuration
