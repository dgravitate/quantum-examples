"""
A module for preparing, optimizing, and executing quantum circuits on the IBM Quantum
platform using Qiskit Runtime.

The module provides functions to save the IBM Quantum Runtime API credentials, optimize
quantum circuits using a preset pass manager, and execute them on the least busy backend
available while handling data simulation efficiently.

This module demonstrates creating a basic 1-qubit quantum circuit, applying
a Hadamard gate to the qubit to achieve a superposition state, and measuring
the circuit's output

Functions:
    get_service: Saves and retrieves the Qiskit Runtime service instance configured
        with IBM Quantum API credentials.
    execute: Optimizes, compiles, and runs the provided Quantum Circuit on the least
        busy quantum backend. Outputs the measurement results.
"""

from qiskit import QuantumCircuit
from qiskit_ibm_runtime.sampler import SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService


def get_service():
    QiskitRuntimeService.save_account(
        channel="ibm_quantum_platform",
        token="YOUR_API_TOKEN",
        instance="YOUR_CLOUD_CRN",
        set_as_default=True,
        overwrite=True,
    )
    service = QiskitRuntimeService()
    return service


def execute(service, circuit, shots=1000):
    backend = service.least_busy(operational=True, simulator=False)

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(circuit)
    sampler = Sampler(mode=backend)
    job = sampler.run([isa_circuit], shots=shots)
    print(job.result()[0].data.meas.get_counts())


# Step 1: Create a 1-qubit circuit
qc = QuantumCircuit(1)

# Step 2: Put the qubit into superposition
qc.h(range(1)) # Hadamard gate

# Step 3: Measure it
qc.measure_all()

# Step 4: Simulate
execute(get_service(), qc, shots=1000)
