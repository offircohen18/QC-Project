from typing import Dict
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.qasm3 import loads as qasm3_loads

DEFAULT_SHOTS = 1024


def deserialize_circuit(qc_serialized: str) -> QuantumCircuit:
    """
    Deserialize a QASM 3 string back into a QuantumCircuit.
    """
    return qasm3_loads(qc_serialized)


def execute_circuit(qc_serialized: str, shots: int = DEFAULT_SHOTS) -> Dict[str, int]:
    """
    Execute a serialized quantum circuit on a simulator.
    Returns a dict like {"00": 512, "11": 512}.
    """
    qc = deserialize_circuit(qc_serialized)
    simulator = AerSimulator()
    result = simulator.run(qc, shots=shots).result()
    counts = result.get_counts(qc)
    return dict(counts)
