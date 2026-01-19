from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import sqlite3

from api_server.worker_client import submit_task_to_queue, get_task_info

router = APIRouter()


class TaskRequest(BaseModel):
    """Schema for incoming task requests."""
    circuit: str


@router.post("/tasks", status_code=201)
async def submit_task(request: TaskRequest):
    """
    Submit a new quantum circuit for asynchronous execution.
    Returns a task ID immediately.
    """
    if not request.circuit.strip():
        raise HTTPException(status_code=400, detail="Circuit cannot be empty")

    try:
        return submit_task_to_queue(request.circuit)

    except sqlite3.Error as e:
        print(f"Database error while creating task: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error while creating task"
        )

    except Exception as e:
        print(f"Unexpected error while creating task: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/tasks/{task_id}")
async def get_status(task_id: str):
    """
    Retrieve the status and result of a task by its ID.
    """
    try:
        info = get_task_info(task_id)

    except sqlite3.Error as e:
        print(f"Database error while fetching task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching task"
        )

    except Exception as e:
        print(f"Unexpected error while fetching task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    if info is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return info
