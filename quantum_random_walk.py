"""
Simulation of a discrete-time quantum walk using a statevector approach.

This module provides a function to simulate a discrete-time quantum walk
over a one-dimensional lattice. The walk uses a Hadamard coin operator
and performs a sequence of coin operations and position updates. The resulting
probability distribution over positions after the specified number of steps
can be obtained as the output.

The function supports parameterization of lattice size, initial position, and
initial coin state.

Functionality:
- Perform discrete-time quantum walks.
- Support custom lattice sizes, initial positions, and initial coin states.
- Reflect at boundaries with coin-state flipping behavior.
- Output the final probability distribution across lattice positions.

For more information about this script, read the article at
https://medium.com/@graveybeard/randomness-in-python-from-random-to-real-random-part-2-ee325d748fb3

Functions:
    dtqw_statevector: performs a random quantum walk algorithm

"""

import numpy as np


def dtqw_statevector(steps=10, positions=11, start_pos=None, coin_state=None):
    """
    Discrete-time quantum walk (statevector simulation).
    - steps: number of walk steps (coin + shift each step)
    - positions: number of lattice sites (must be >=1; odd recommended so there's a center)
    - start_pos: initial position index (0..positions-1). If None, uses center = positions//2
    - coin_state: initial 2-vector for the coin. If None, defaults to |0>.

    Returns: probability distribution over positions (numpy array of length `positions`)
    """
    if positions < 1:
        raise ValueError("positions must be >= 1")

    N = positions
    dim = 2 * N  # coin ⊗ position

    # initial position
    if start_pos is None:
        start_pos = N // 2
    if not (0 <= start_pos < N):
        raise ValueError("start_pos out of range")

    # initial coin state
    if coin_state is None:
        coin_state = np.array([1.0, 0.0], dtype=complex)  # |0>
    else:
        coin_state = np.asarray(coin_state, dtype=complex)
        coin_state = coin_state / np.linalg.norm(coin_state)

    # build initial statevector: |coin> ⊗ |position>
    psi = np.zeros(dim, dtype=complex)
    # ordering: index = 2*pos + coin
    for c in range(2):
        psi[2 * start_pos + c] = coin_state[c]

    # coin operator: Hadamard on coin, identity on position
    H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
    # Build the shift operator S (2N x 2N): S maps
    # |pos,0> -> |pos-1,0>  (move left)
    # |pos,1> -> |pos+1,1>  (move right)
    # reflecting boundaries: attempts to move off edge flip the coin and stay
    S = np.zeros((dim, dim), dtype=complex)
    for pos in range(N):
        # coin = 0 : move left
        if pos > 0:
            target = 2 * (pos-1) + 0
            S[target, 2 * pos + 0] = 1.0
        else:
            # reflect: stay in pos 0 but flip coin to 1
            target = 2 * pos + 1
            S[target, 2 * pos + 0] = 1.0
        # coin = 1 : move right
        if pos < N - 1:
            target = 2 * (pos + 1) + 1
            S[target, 2 * pos + 1] = 1.0
        else:
            # reflect at right edge: stay and flip coin to 0
            target = 2 * pos + 0
            S[target, 2 * pos + 1] = 1.0

    # apply coin (H on coin for each position)
    def apply_coin(state):
        new = np.zeros_like(state)
        for pos in range(N):
            vec = state[2 * pos:2 * pos + 2]
            new[2 * pos:2 * pos + 2] = H.dot(vec)
        return new

    def apply_shift(state):
        return S.dot(state)

    # Evolution: repeat (coin then shift)
    for _ in range(steps):
        psi = apply_coin(psi)
        psi = apply_shift(psi)

    # Compute position probabilities by summing coin-state probabilities at each position
    pos_probs = np.zeros(N)
    for pos in range(N):
        amp0 = psi[2 * pos + 0]
        amp1 = psi[2 * pos + 1]
        pos_probs[pos] = (abs(amp0) ** 2 + abs(amp1) ** 2).real

    # normalize and return
    pos_probs = pos_probs / pos_probs.sum()
    return pos_probs


# Example usage
positions = 11
steps = 5
probs = dtqw_statevector(steps=steps, positions=positions)
counts = (probs * 1000).round().astype(int)  # pseudo-shot scaling for display
print(f"Discrete-time quantum walk (Hadamard coin), steps={steps}, positions={positions}\n")
for pos in range(positions):
    bar = "█" * (counts[pos] // 10)
    print(f"Position {pos:2}: {counts[pos]:3} {bar}")

print("\n(position probabilities):")
print(np.array2string(probs, precision=4, separator=", "))
