"""
This module provides functionality for generating cryptographic keys
using simulated quantum randomness. The quantum randomness is obtained
through a simulated quantum circuit, which utilizes quantum operations
such as superposition, entanglement, and phase rotation.

For more information about this script, read the article at
https://medium.com/@graveybeard/randomness-in-python-from-random-to-real-random-part-2-ee325d748fb3

Functions:
    generate_quantum_key: Generates a cryptographic key based on quantum randomness.
"""

import hashlib
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def generate_quantum_key(key_length_bits=256):
    """Generate a cryptographic key using simulated quantum randomness."""
    num_qubits = 16
    qc = QuantumCircuit(num_qubits, num_qubits)

    # Superposition + phase rotations
    for i in range(num_qubits):
        qc.h(i)
        qc.rz(np.pi / (i + 1), i)

    # Entanglement
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)

    qc.measure(range(num_qubits), range(num_qubits))

    # just simulate for now, but you can swap out for a real backend!
    simulator = AerSimulator()
    shots_needed = (key_length_bits + num_qubits - 1) // num_qubits

    job = simulator.run(qc, shots=shots_needed)
    result = job.result()
    counts = result.get_counts()

    quantum_bits = []
    for bitstring, count in counts.items():
        bits = [int(b) for b in bitstring[::-1]]  # reverse if you want qubit[0] first
        quantum_bits.extend(bits * count)

    quantum_bits = quantum_bits[:key_length_bits]

    if len(quantum_bits) < key_length_bits:
        raise RuntimeError(f"Only generated {len(quantum_bits)} bits, needed {key_length_bits}")

    # Convert to bytes
    key_bytes = bytearray()
    for i in range(0, len(quantum_bits), 8):
        byte_bits = quantum_bits[i:i+8]
        if len(byte_bits) == 8:
            byte_value = sum(bit << (7-j) for j, bit in enumerate(byte_bits))
            key_bytes.append(byte_value)

    # Final hash for uniform cryptographic key
    return hashlib.sha256(bytes(key_bytes)).digest()
