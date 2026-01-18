import time
import json
from shared.database import get_connection
from worker.executor import execute_circuit


def check_for_tasks():
    """
    Polls the database for 'submitted' tasks, executes them,
    and updates their status to 'completed' or 'failed'.
    """
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT id, circuit FROM tasks WHERE status = 'submitted' LIMIT 1")
        task = cur.fetchone()

        if task:
            task_id = task['id']
            print(f"Starting task {task_id}...")

            try:
                cur.execute("UPDATE tasks SET status = 'pending' WHERE id = ?", (task_id,))
                conn.commit()

                result_counts = execute_circuit(task['circuit'])

                cur.execute(
                    "UPDATE tasks SET status = 'completed', result = ? WHERE id = ?",
                    (json.dumps(result_counts), task_id)
                )
                print(f"Task {task_id} completed successfully.")

            except Exception as e:
                error_msg = str(e) if str(e) else repr(e)
                print(f"Error processing task {task_id}: {error_msg}")

                cur.execute(
                    "UPDATE tasks SET status = 'failed', error = ?, result = NULL WHERE id = ?",
                    (error_msg, task_id)
                )

            conn.commit()


def main():
    """Main loop for the worker process."""
    print("--- Quantum Worker started and polling ---")
    try:
        while True:
            check_for_tasks()
            # Wait for 5 seconds before checking the DB again to save CPU/IO
            time.sleep(5)
    except KeyboardInterrupt:
        print("--- Worker stopped by user ---")


if __name__ == "__main__":
    main()
