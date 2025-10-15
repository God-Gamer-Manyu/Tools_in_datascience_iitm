from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, cast
import re
import json
import os
import openai
import dotenv

# Load optional .env for local development (no hard fail here; function will check at call time)
dotenv.load_dotenv("../.env")

app = FastAPI(title="TechNova Assistant - Function Mapper")

# Allow CORS from anywhere for GET requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Pre-compiled regex templates for each supported question (local fallback)
patterns = [
    {
        "name": "get_ticket_status",
        "regex": re.compile(r"status of ticket\s+(?P<ticket_id>\d+)", re.IGNORECASE),
        "extract": lambda m: {"ticket_id": int(m.group('ticket_id'))}
    },
    {
        "name": "schedule_meeting",
        "regex": re.compile(r"schedule a meeting on\s+(?P<date>\d{4}-\d{2}-\d{2})\s+at\s+(?P<time>\d{1,2}:\d{2})\s+in\s+(?P<meeting_room>.+)\.?$", re.IGNORECASE),
        "extract": lambda m: {"date": m.group('date'), "time": m.group('time'), "meeting_room": m.group('meeting_room').strip()}
    },
    {
        "name": "get_expense_balance",
        "regex": re.compile(r"expense balance for employee\s+(?P<employee_id>\d+)", re.IGNORECASE),
        "extract": lambda m: {"employee_id": int(m.group('employee_id'))}
    },
    {
        "name": "calculate_performance_bonus",
        "regex": re.compile(r"performance bonus for employee\s+(?P<employee_id>\d+)\s+for\s+(?P<year>\d{4})", re.IGNORECASE),
        "extract": lambda m: {"employee_id": int(m.group('employee_id')), "current_year": int(m.group('year'))}
    },
    {
        "name": "report_office_issue",
        "regex": re.compile(r"report office issue\s+(?P<issue_code>\d+)\s+for the\s+(?P<department>.+)\s+department\.?", re.IGNORECASE),
        "extract": lambda m: {"issue_code": int(m.group('issue_code')), "department": m.group('department').strip()}
    }
]


@app.get('/execute')
def execute(q: str = Query(..., description="Templatized user query")) -> Dict[str, str]:
    """Local parsing endpoint: analyze the incoming query text and map it to one of the pre-defined functions.

    Returns:
        {"name": function_name, "arguments": json_encoded_string}
    """
    text = q.strip()

    for p in patterns:
        m = p['regex'].search(text)
        if m:
            args = p['extract'](m)
            return {
                "name": p['name'],
                "arguments": json.dumps(args)
            }

    # If no pattern matches, return a helpful error-like structure
    return {
        "name": "unknown",
        "arguments": json.dumps({"query": text})
    }


# -------------------- OpenAI function-calling integration --------------------

# Function schemas (tools) to send to the model. These match the predefined backend functions.
FUNCTION_TOOLS = [
    {
        "name": "get_ticket_status",
        "description": "Get the status of an IT support ticket",
        "parameters": {
            "type": "object",
            "properties": {"ticket_id": {"type": "integer", "description": "Numeric ticket id"}},
            "required": ["ticket_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "schedule_meeting",
        "description": "Schedule a meeting room for a specific date and time",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "description": "HH:MM"},
                "meeting_room": {"type": "string", "description": "Meeting room name"},
            },
            "required": ["date", "time", "meeting_room"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_expense_balance",
        "description": "Get expense balance for an employee",
        "parameters": {
            "type": "object",
            "properties": {"employee_id": {"type": "integer", "description": "Employee ID"}},
            "required": ["employee_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "calculate_performance_bonus",
        "description": "Calculate yearly performance bonus for an employee",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {"type": "integer", "description": "Employee ID"},
                "current_year": {"type": "integer", "description": "Year to calculate bonus for"},
            },
            "required": ["employee_id", "current_year"],
            "additionalProperties": False,
        },
    },
    {
        "name": "report_office_issue",
        "description": "Report an office issue for a department",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_code": {"type": "integer", "description": "Issue code number"},
                "department": {"type": "string", "description": "Department name"},
            },
            "required": ["issue_code", "department"],
            "additionalProperties": False,
        },
    },
]


def call_openai_for_function_call(query: str, required: bool = False) -> Dict[str, Any]:
    """Call OpenAI's chat completions endpoint with function definitions and return the model's tool call info.

    Note: Requires env var OPENAI_API_KEY to be set. If not present, raises a RuntimeError.
    """
    api_key = os.getenv('OPENAI_API_KEY', "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjMwMDEzODNAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.Wbn0uOC5oRD-WaZ0e_G1nDpjKBlXLIC8_-OrjPm7lt8")
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment')

    # Configure OpenAI SDK key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise RuntimeError('OPENAI_API_KEY not set in environment')

    # Use the modern OpenAI client
    from openai import OpenAI as OpenAIClient
    # The client reads configuration (API key, base url) from environment by default.
    client = OpenAIClient()

    # Build request using the new client
    function_call_param = "auto"
    if required:
        # When required=True, prefer that the model returns a function call.
        function_call_param = "auto"

    # The SDK typing expects Function objects; cast to Any to pass our dict-based schemas.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        functions=cast(Any, FUNCTION_TOOLS),
        function_call=function_call_param,
    )

    # Normalize response into a plain dict with 'choices' as a list of dicts
    data = None
    if hasattr(response, 'to_dict'):
        try:
            data = response.to_dict()
        except Exception:
            data = None

    if data is None:
        if isinstance(response, dict):
            data = response
        else:
            # Try to extract choices attribute and convert each to dict
            try:
                raw_choices = getattr(response, 'choices', None)
                if raw_choices is None:
                    raw_choices = response.get('choices') if isinstance(response, dict) else []
                normalized = []
                for c in raw_choices or []:
                    if hasattr(c, 'to_dict'):
                        try:
                            normalized.append(c.to_dict())
                        except Exception:
                            normalized.append({})
                    elif isinstance(c, dict):
                        normalized.append(c)
                    else:
                        # Last resort: use __dict__ or empty
                        normalized.append(getattr(c, '__dict__', {}))
                data = {'choices': normalized}
            except Exception:
                data = {'choices': []}

    # The model message may contain either 'tool_calls' (list) or 'tool_call' (single). Normalize.
    choices = data.get('choices') or []
    if not isinstance(choices, list) or len(choices) == 0:
        raise RuntimeError('No choices returned from OpenAI')

    # Safely extract the first choice as a dict-like
    first_choice = choices[0] if isinstance(choices[0], dict) else getattr(choices[0], '__dict__', {})
    message = first_choice.get('message') or {}

    # SDK-style function_call lives under message['function_call'] or first_choice['function_call']
    function_call = None
    if isinstance(message, dict):
        function_call = message.get('function_call')
    if not function_call:
        function_call = first_choice.get('function_call')

    # Legacy/tool-based structure
    tool_calls = None
    if isinstance(message, dict):
        tool_calls = message.get('tool_calls') or message.get('tool_call')
    if not tool_calls:
        tool_calls = first_choice.get('tool_calls') or first_choice.get('tool_call')

    if function_call:
        first = function_call
        func_name = first.get('name') or first.get('function')
        func_args = first.get('arguments') or first.get('args') or {}
        # function_call.arguments is commonly a JSON-string from the model
        if isinstance(func_args, str):
            arguments_payload = func_args
        else:
            arguments_payload = json.dumps(func_args)
        return {"name": func_name, "arguments": arguments_payload}

    if tool_calls is None:
        # No tool call was chosen
        return {"name": "none", "arguments": json.dumps({"query": query})}

    if isinstance(tool_calls, dict):
        tool_calls = [tool_calls]

    first = tool_calls[0]
    func_name = first.get('function') or first.get('name') or first.get('tool')
    func_args = first.get('arguments') or first.get('args') or {}
    if isinstance(func_args, str):
        arguments_payload = func_args
    else:
        arguments_payload = json.dumps(func_args)
    return {"name": func_name, "arguments": arguments_payload}


@app.get('/execute_ai')
def execute_ai(q: str = Query(..., description="User query"), required: Optional[bool] = Query(False, description="Require a tool call")) -> Dict[str, str]:
    """Use OpenAI function calling to determine which backend function and arguments to call.

    If OPENAI_API_KEY is not set, fall back to local parsing.
    """
    try:
        # Ensure required is a bool (Query can pass None)
        return call_openai_for_function_call(q, required=bool(required))
    except RuntimeError as e:
        # Fallback to local parser if API key missing or other runtime issue
        text = q.strip()
        for p in patterns:
            m = p['regex'].search(text)
            if m:
                args = p['extract'](m)
                return {"name": p['name'], "arguments": json.dumps(args)}

        return {"name": "unknown", "arguments": json.dumps({"query": text, "error": str(e)})}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
