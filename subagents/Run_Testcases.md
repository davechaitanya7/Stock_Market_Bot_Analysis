# Run Testcases Subagent

## Purpose
Execute and analyze test suites for the Stock Trading Bot project.

## When to Invoke
- After code changes
- Before merging PRs
- When debugging failing tests
- For regression testing

## Test Structure

**Backend Tests** (if created):
- Location: `backend/tests/`
- Framework: pytest
- Run: `cd backend && source venv/bin/activate && pytest`

**Frontend Tests** (if created):
- Location: `frontend/src/__tests__/`
- Framework: Vitest or Jest
- Run: `cd frontend && npm test`

## Prompt Template

```
Run all testcases and provide a detailed report:

1. **Test Execution**
   - Run backend tests: pytest backend/tests/ -v
   - Run frontend tests: npm test -- --coverage
   - Note any test environment setup required

2. **Results Summary**
   - Total tests run
   - Passed/Failed/Skipped count
   - Code coverage percentage

3. **Failure Analysis**
   For each failing test:
   - Test name and file location
   - Expected vs actual behavior
   - Error message and stack trace
   - Likely root cause

4. **Recommendations**
   - Which tests need fixing
   - Whether failures are test bugs or code bugs
   - Priority order for fixes

## Context
- Recent changes: [describe commits or file changes]
- Known issues: [any expected failures]
- Branch name: [for git context]

## Output Format
- PASSING: [count] tests
- FAILING: [count] tests ([list names])
- SKIPPED: [count] tests
- COVERAGE: [percentage]%
- ACTION REQUIRED: [yes/no with details]
```

## API Testing (Manual)
If no automated tests exist, verify these endpoints:

```bash
# Health check
curl http://localhost:8000/

# Stock search
curl "http://localhost:8000/api/stocks/search?q=RELIANCE"

# Stock data
curl http://localhost:8000/api/stocks/RELIANCE.NS/data

# Stock analysis
curl http://localhost:8000/api/stocks/RELIANCE.NS/analysis

# Market indices
curl http://localhost:8000/api/market/indices

# Orders (create, list, approve, reject)
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"symbol":"RELIANCE.NS","action":"BUY","quantity":10,"order_type":"MARKET"}'
```

## Example Invocation
```
Agent(subagent_type="Run_Testcases", prompt="Run all backend tests and report failures. Focus on the analysis module tests after the indicator calculation changes.")
```
