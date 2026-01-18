from shared.database import create_task, get_task_by_id
import json


def submit_task_to_queue(circuit: str) -> dict:
    """
    Submits a new circuit to the database.
    Returns a dictionary containing the generated task_id and initial status.
    """
    task_id = create_task(circuit)
    return {
        "task_id": task_id,
        "status": "submitted"
    }


def get_task_info(task_id: str) -> dict | None:
    """
    Retrieves task details from the database by ID.
    Formats the 'result' field from JSON string back to a dictionary if applicable.
    Returns None if the task is not found.
    """
    task = get_task_by_id(task_id)
    if not task:
        return None

    response = {"status": task["status"]}

    if task.get("error"):
        response["error"] = task["error"]

    if task.get("result"):
        try:
            response["result"] = json.loads(task["result"])
        except (json.JSONDecodeError, TypeError):
            response["result"] = task["result"]

    return response
