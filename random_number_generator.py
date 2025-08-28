"""
This module provides functionality for generating cryptographically random bytes
using quantum simulation. It utilizes Qiskit's AerSimulator to simulate quantum
randomness by leveraging quantum circuits.

The module includes functions to create a quantum circuit that generates random
bits and to transform these bits into cryptographically random bytes.

For more information about this script, read the article at
https://medium.com/@graveybeard/randomness-in-python-from-random-to-real-random-part-2-ee325d748fb3

Functions:
    create_quantum_random_generator: Constructs a quantum circuit for producing
        random bits using quantum gates.
    quantum_random_bytes: Uses quantum simulation to generate random bytes based
        on the quantum circuit.

"""
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np


def create_quantum_random_generator():
    """Create a quantum circuit for generating random bits"""
    # Create circuit with 8 qubits for 8 random bits at once
    qc = QuantumCircuit(8, 8)
    
    # Put all qubits in superposition
    for i in range(8):
        qc.h(i)  # Hadamard gate creates superposition

    for i in range(8):
        qc.measure(i, i) # Measure all qubits
    return qc


def quantum_random_bytes(num_bytes=32):
    """Generate cryptographically random bytes using quantum simulation"""
    random_bytes = bytearray()

    # Create our quantum random bit generator
    qc = create_quantum_random_generator()
    simulator = AerSimulator()

    # Generate bytes one at a time
    for _ in range(num_bytes):
        # Run the quantum circuit
        job = simulator.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        # Extract the measurement result (8-bit string)
        measurement = list(counts.keys())[0]
        # Convert binary string to byte
        byte_value = int(measurement, 2)
        random_bytes.append(byte_value)

    return bytes(random_bytes)

# Generate quantum random bytes
quantum_bytes = quantum_random_bytes(16)
print(f"Quantum random bytes: {quantum_bytes.hex()}")
