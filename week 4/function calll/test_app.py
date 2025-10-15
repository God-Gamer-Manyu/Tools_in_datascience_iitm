from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)

def call(q):
    r = client.get('/execute', params={'q': q})
    assert r.status_code == 200
    return r.json()


def test_get_ticket_status():
    res = call('What is the status of ticket 83742?')
    assert res['name'] == 'get_ticket_status'
    args = json.loads(res['arguments'])
    assert args == {'ticket_id': 83742}


def test_schedule_meeting():
    res = call('Schedule a meeting on 2025-02-15 at 14:00 in Room A.')
    assert res['name'] == 'schedule_meeting'
    args = json.loads(res['arguments'])
    assert args == {'date': '2025-02-15', 'time': '14:00', 'meeting_room': 'Room A'}


def test_get_expense_balance():
    res = call('Show my expense balance for employee 10056.')
    assert res['name'] == 'get_expense_balance'
    args = json.loads(res['arguments'])
    assert args == {'employee_id': 10056}


def test_calculate_performance_bonus():
    res = call('Calculate performance bonus for employee 10056 for 2025.')
    assert res['name'] == 'calculate_performance_bonus'
    args = json.loads(res['arguments'])
    assert args == {'employee_id': 10056, 'current_year': 2025}


def test_report_office_issue():
    res = call('Report office issue 45321 for the Facilities department.')
    assert res['name'] == 'report_office_issue'
    args = json.loads(res['arguments'])
    assert args == {'issue_code': 45321, 'department': 'Facilities'}
