from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.sampler import SamplerV2 as Sampler


def get_service():
    return AerSimulator()


def execute(service, circuit, shots=1000):
    sampler = Sampler(service)
    job = sampler.run([circuit], shots=shots)
    print(job.result()[0].data.meas.get_counts())


# Step 1: Create a 1-qubit circuit
qc = QuantumCircuit(1)

# Step 2: Put the qubit into superposition
qc.h(range(1)) # Hadamard gate

# Step 3: Measure it
qc.measure_all()

# Step 4: Simulate
execute(get_service(), qc, shots=1000)
