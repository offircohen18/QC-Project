from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from api_server.worker_client import submit_task_to_queue, get_task_info

router = APIRouter()


class TaskRequest(BaseModel):
    """Schema for incoming task requests."""
    circuit: str


@router.post("/tasks/", status_code=201)
async def submit_task(request: TaskRequest):
    """
    Endpoint to submit a new quantum circuit for execution.
    Validates input and returns the unique task ID and initial status.
    """
    if not request.circuit.strip():
        # Raise 400 if the circuit string is empty or just whitespace
        raise HTTPException(status_code=400, detail="Circuit cannot be empty")

    # Delegate task creation to the worker client
    result = submit_task_to_queue(request.circuit)
    return result


@router.get("/tasks/{task_id}")
async def get_status(task_id: str):
    """
    Endpoint to retrieve the status and results of a specific task.
    Returns 404 if the task ID does not exist in the database.
    """
    info = get_task_info(task_id)

    if info is None:
        # Task not found in the database
        raise HTTPException(status_code=404, detail="Task not found")

    return info
