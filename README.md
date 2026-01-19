# Quantum Task Queue System

A robust, asynchronous system for executing Quantum Circuits using FastAPI, SQLite, and Qiskit. This project demonstrates a decoupled architecture where a web server handles client requests and a background worker processes complex quantum simulations.



## Architecture Overview

The system is built with three main components:
1.  **FastAPI Server:** Provides endpoints to submit quantum circuits and poll for their execution status/results.
2.  **SQLite Database:** Acts as the persistent storage and message broker between the API and the Worker.
3.  **Background Worker:** A dedicated process that polls the database, executes the quantum circuits using Qiskit Aer, and updates the results or error messages.



## Features

* **Asynchronous Execution:** Clients receive a `task_id` immediately upon submission.
* **State Tracking:** Tasks progress through four states: `submitted`, `pending`, `completed`, or `failed`.
* **Detailed Error Reporting:** If a circuit is invalid (e.g., syntax error in OpenQASM), the specific error is captured and returned via the API.
* **Clean API Responses:** The system dynamically excludes null fields, providing a clean JSON output for the end-user.

## Installation

1. **Clone the repository** (or navigate to the project folder).
2. **Environment Variables**:
   Create a `.env` file in the root directory and define the following variables:
   ```env
   DATABASE_NAME=tasks.db
   API_HOST=127.0.0.1
   API_PORT=8000
   DEBUG=True
   ```
3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: `sqlite3` and `json` are part of the Python Standard Library).*

## How to Run

### Step 1: Start the API Server
Run the following command in your terminal:
   ```bash
   python -m api_server.main
   ```
The server will be available at `http://127.0.0.1:8000`. You can access the interactive documentation at `http://127.0.0.1:8000/docs`.

### Step 2: Start the Background Worker
Open a **new** terminal and run:
   ```bash
   python -m worker.main
   ```

## API Usage Guide

### 1. Submit a Quantum Circuit
**Endpoint:** `POST /tasks`

**Request Body Example:**
   ```json
   {
     "circuit": "OPENQASM 3;\ninclude \"stdgates.inc\";\nqubit[2] q;\nbit[2] c;\nh q[0];\ncx q[0], q[1];\nc[0] = measure q[0];\nc[1] = measure q[1];"
   }
   ```

### 2. Check Task Status and Get Results
**Endpoint:** `GET /tasks/{task_id}`

**Success Response Example:**
   ```json
   {
     "status": "completed",
     "result": {
       "00": 512,
       "11": 512
     }
   }
   ```

**Error Response Example:**
   ```json
   {
     "status": "failed",
     "error": "QasmError: line 1:8 no viable alternative at input '...'"
   }
   ```
## Testing

The project includes integration tests that validate the complete asynchronous flow:
task submission → background execution → result retrieval.

These tests interact with the real API endpoints and verify that the worker
processes tasks correctly.

### Prerequisites for Testing
Ensure both the **API Server** and the **Worker Service** are running in the background.
Both services must be running simultaneously, as the tests rely on the worker
to execute submitted tasks.

### Running the Tests
1. Install testing dependencies:
   ```bash
   pip install pytest httpx
   ``` 
2. Run the tests using pytest:
   ```bash
      pytest
   ```

The tests will:

* Submit a quantum circuit via the API

* Poll the task status endpoint

* Verify successful completion or failure handling

* Validate edge cases (e.g., empty circuits, non-existent task IDs, and execution failures).

### Notes
* Tests are intentionally written as integration tests, not unit tests,
to reflect real-world asynchronous behavior.

* The database is shared between the API and the worker during testing.

* Persistence across test runs is not required.

## Implementation Details

* **Language:** Python 3.11.4
* **Database:** SQLite (using `sqlite3.Row` for dictionary-like access).
* **Formatting:** All logs and code comments are written in English.
* **Safety:** Connections to the database are safely managed using `try...except...finally` blocks to prevent database locking.
