import time
import pytest
from fastapi.testclient import TestClient
from api_server.main import app

client = TestClient(app)


def test_submit_and_get_task():
    """
    Test the successful path: Submit a valid Bell State circuit,
    poll for completion, and verify the results.
    """
    bell_circuit = """
    OPENQASM 3;
    include "stdgates.inc";
    qubit[2] q;
    bit[2] c;
    h q[0];
    cx q[0], q[1];
    c = measure q;
    """

    response = client.post("/tasks/", json={"circuit": bell_circuit})
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    max_retries = 10
    completed = False

    for _ in range(max_retries):
        status_resp = client.get(f"/tasks/{task_id}")
        assert status_resp.status_code == 200
        status_data = status_resp.json()

        if status_data["status"] == "completed":
            assert "result" in status_data
            assert isinstance(status_data["result"], dict)
            completed = True
            break
        elif status_data["status"] == "failed":
            pytest.fail(f"Task failed with error: {status_data.get('error')}")

        time.sleep(1)  # Wait for worker to process

    assert completed, "Task did not complete in time"


def test_submit_empty_circuit():
    """Test that submitting an empty circuit string returns a 400 error."""
    response = client.post("/tasks/", json={"circuit": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Circuit cannot be empty"


def test_get_non_existent_task():
    """Test that requesting a random UUID returns a 404 error."""
    response = client.get("/tasks/this-id-does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_invalid_circuit_fails_gracefully():
    """
    Test that an invalid QASM circuit (syntax error)
    is caught by the worker and results in a 'failed' status.
    """
    invalid_circuit = "NOT A VALID QASM CIRCUIT"

    response = client.post("/tasks/", json={"circuit": invalid_circuit})
    assert response.status_code == 201
    task_id = response.json()["task_id"]

    max_retries = 10
    failed = False

    for _ in range(max_retries):
        status_resp = client.get(f"/tasks/{task_id}")
        status_data = status_resp.json()

        if status_data["status"] == "failed":
            assert "error" in status_data
            failed = True
            break

        time.sleep(1)

    assert failed, "Task should have marked as 'failed' but did not"
