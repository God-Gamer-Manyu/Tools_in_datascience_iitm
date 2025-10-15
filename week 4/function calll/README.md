TechNova Assistant - Function Call Mapper

This small FastAPI app exposes a GET endpoint `/execute?q=...` which maps templatized user queries to one of the pre-defined backend functions and returns the function name and JSON-encoded arguments.

Supported mappings (examples):

- "What is the status of ticket 83742?" -> get_ticket_status(ticket_id=83742)
- "Schedule a meeting on 2025-02-15 at 14:00 in Room A." -> schedule_meeting(date="2025-02-15", time="14:00", meeting_room="Room A")
- "Show my expense balance for employee 10056." -> get_expense_balance(employee_id=10056)
- "Calculate performance bonus for employee 10056 for 2025." -> calculate_performance_bonus(employee_id=10056, current_year=2025)
- "Report office issue 45321 for the Facilities department." -> report_office_issue(issue_code=45321, department="Facilities")

Run locally (example):

# Create a virtualenv and install
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run the server
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

Then visit:

http://localhost:8000/execute?q=What%20is%20the%20status%20of%20ticket%2083742%3F

AI-backed endpoint
-------------------

This project includes an AI-backed endpoint that uses OpenAI function calling to choose which function to call and return the arguments. The endpoint is:

GET /execute_ai?q=...&required=false

Behavior:
- If `OPENAI_API_KEY` environment variable is set, the server calls the OpenAI Chat Completions API with function definitions and returns the model's selected function name and arguments.
- If `OPENAI_API_KEY` is missing or the API call fails, the endpoint falls back to local regex parsing (same behavior as `/execute`).

Example (requires OPENAI_API_KEY):

http://localhost:8000/execute_ai?q=Schedule%20a%20meeting%20on%202025-02-15%20at%2014:00%20in%20Room%20A.&required=true

Notes:
- Set your API key in Windows cmd:

```powershell
set OPENAI_API_KEY=your_api_key_here
```

or in cmd:

```
setx OPENAI_API_KEY "your_api_key_here"
```

Security: do not commit your API key into source control.
