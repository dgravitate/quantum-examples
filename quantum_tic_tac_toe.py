"""
Copyright (c) 2025 David Graves

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


class QuantumTicTacToe:
    """
    Represents a quantum-enhanced version of the classic Tic Tac Toe game.

    This class simulates a game of Tic Tac Toe with quantum mechanics elements.
    Players can make deterministic moves as in the classical game or push cells
    into quantum superposition. The game can simulate quantum measurement for
    collapsing superpositions into deterministic states. The class supports all
    necessary gameplay mechanics, including tracking the board, switching players,
    checking for winners, and managing quantum states.
    """
    def __init__(self):
        self.board = [{'state': 'empty', 'owner': None} for _ in range(9)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.move_history = []

    def display_board(self):
        """
        Displays the current state of the board along with a legend explaining the symbols. The
        board is shown as a 3x3 grid where each cell displays a visual representation of its
        current quantum or classical game state. Various states such as "empty", "deterministic",
        and "quantum superposition" are represented using specific symbols for clarity.

        Legend:
            - X/O: Deterministically owned by a player.
            - ?: In quantum superposition.
            - (empty): Cell is available for selection.

        Raises
        ------
            None
        """
        print("\nCurrent Board:")
        print("   0   1   2")
        for i in range(3):
            row = ""
            for j in range(3):
                cell_idx = i * 3 + j
                cell = self.board[cell_idx]

                if cell['state'] == 'empty':
                    symbol = ' '
                elif cell['state'] == 'deterministic':
                    symbol = cell['owner']
                elif cell['state'] == 'superposition':
                    symbol = '?'  # Quantum superposition
                else:
                    symbol = ' '

                row += f" {symbol} "
                if j < 2:
                    row += "|"

            print(f"{i} {row}")
            if i < 2:
                print("  -----------")

        # Show legend
        print("\nLegend:")
        print("X/O = Deterministically owned")
        print("? = In quantum superposition")
        print("(empty) = Available")

    def get_superposition_cells(self):
        """
        Finds all cells in the board that are in a 'superposition' state.

        Returns
        -------
        list of int
            A list of indices representing cells in the board that have their 'state'
            set to 'superposition'.
        """
        return [i for i, cell in enumerate(self.board) if cell['state'] == 'superposition']

    def collapse_superposition(self):
        """
        Collapses all currently superposed cells in a quantum simulation to a deterministic state
        using independent quantum measurement. The method utilizes a quantum simulator to execute
        simulated measurements for each superposed cell and determines the resulting state.

        Raises
        ------
        No specific exceptions are defined, but runtime errors may occur if necessary resources
        such as the quantum simulator are unavailable or if `self.board` is modified improperly.

        Notes
        -----
        The method relies on Qiskit's AerSimulator for quantum circuit simulation and assumes
        that superposed cells are identified prior to calling this method.
        """
        superposed_indices = self.get_superposition_cells()

        if not superposed_indices:
            return

        print(f"\nCollapsing {len(superposed_indices)} superposed cells using independent quantum measurement...")

        simulator = AerSimulator()

        for cell_idx in superposed_indices:
            # Build a separate circuit for each cell
            qc = QuantumCircuit(1, 1)
            qc.h(0)  # put qubit in superposition
            qc.measure(0, 0)

            # Execute with 100 shots
            compiled_circuit = transpile(qc, simulator)
            job = simulator.run(compiled_circuit, shots=100)
            result = job.result()
            counts = result.get_counts(compiled_circuit)

            measurement = list(counts.keys())[0]
            clean_measurement = measurement.replace(' ', '')

            bit_value = int(clean_measurement)
            owner = 'X' if not bit_value else 'O'
            self.board[cell_idx] = {'state': 'deterministic', 'owner': owner}
            print(f"Cell {cell_idx} collapsed to: {owner}")

    def check_winner(self):
        """
        Evaluates the current game board to check if there is a winner by identifying
        any complete line (row, column, or diagonal) with cells deterministically
        owned by the same player.

        This method looks through all possible winning combinations on the board
        and determines if any of them belong entirely to one specific player. It
        ensures that all cells in the combination are in a 'deterministic' state
        and owned by the same player. If such a combination is found,
        the corresponding player's identifier is returned.

        Returns:
            str or None: The identifier of the winning player if a winning combination
                is detected. Returns None if there is no winner.
        """
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]  # diagonals
        ]

        for combo in winning_combinations:
            cells = [self.board[i] for i in combo]

            # Check if all cells are deterministically owned by the same player
            if all(cell['state'] == 'deterministic' for cell in cells):
                owners = [cell['owner'] for cell in cells]
                if owners[0] == owners[1] == owners[2]:
                    return owners[0]

        return None

    def is_board_full(self):
        """
        Checks if the board is completely filled with deterministic cells.

        Returns
        -------
        bool
            True if all cells in the board have a state of 'deterministic', False otherwise.
        """
        return all(cell['state'] == 'deterministic' for cell in self.board)

    def make_move(self, position):
        """
        Attempts to make a move at the specified position on the game board, updating
        the board state based on specific rules regarding cell ownership and state.
        Handles moves involving empty cells, deterministically owned cells, and cells
        in superposition. Rejects invalid moves or positions outside the allowed range.

        Parameters:
            position (int): The index of the cell on the board where the player wishes
                to make a move, must be between 0 and 8 inclusive.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if position < 0 or position > 8:
            print("Invalid position! Choose 0-8.")
            return False

        cell = self.board[position]

        if cell['state'] == 'empty':
            # First move on empty cell. Player owns deterministically
            self.board[position] = {'state': 'deterministic', 'owner': self.current_player}
            print(f"Player {self.current_player} claimed cell {position} deterministically.")

        elif cell['state'] == 'deterministic':
            # Don't let a player put their own cell into a superposition
            if self.board[position]["owner"] == self.current_player:
                print(f"Cell {position} is already owned by {self.current_player}. Choose another cell.")
                return False

            # Move on already-owned cell → Push into superposition
            self.board[position] = {'state': 'superposition', 'owner': None}
            print(f"Cell {position} pushed into quantum superposition!")

        elif cell['state'] == 'superposition':
            print(f"Cell {position} is already in superposition. Choose another cell.")
            return False

        self.move_history.append((self.current_player, position))
        return True

    def switch_player(self):
        """
        Switches the current player in a two-player game.

        This method toggles the value of the `current_player` attribute between
        'X' and 'O'. It is typically used in games where two players alternately
        take turns.
        """
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def play_turn(self):
        """
        Handles the logic for a single turn in the game. It includes displaying the board, processing user input,
        making a move, collapsing superpositions (if applicable), checking for a winner or tie, and switching
        players. If the game ends due to a win, tie, quit action, or interruption, it updates the game state
        appropriately and returns control to the caller.

        Raises:
            ValueError: If the input is not a valid number between 0-8.
            KeyboardInterrupt: If the player interrupts the game (e.g., with CTRL+C).

        Returns:
            bool: True if the game should proceed to the next turn, or False if the game ends or is exited.
        """
        self.display_board()

        print(f"\nPlayer {self.current_player}'s turn")
        print("Enter position (0-8) or 'q' to quit:")

        try:
            user_input = input("> ").strip().lower()

            if user_input == 'q':
                print("Game ended by player.")
                return False

            position = int(user_input)

            if self.make_move(position):
                # Only collapse after O moves
                if self.current_player == 'O':
                    self.collapse_superposition()

                # Check for winner
                winner = self.check_winner()
                if winner:
                    self.winner = winner
                    self.game_over = True
                    self.display_board()
                    print(f"\n🎉 Player {winner} wins!")
                    return False

                # Check for tie
                if self.is_board_full():
                    self.game_over = True
                    self.display_board()
                    print("\n🤝 It's a tie!")
                    return False

                # Switch players
                self.switch_player()

        except ValueError:
            print("Invalid input! Enter a number 0-8.")
        except KeyboardInterrupt:
            print("\nGame interrupted.")
            return False

        return True

    def play_game(self):
        print("🎲 Welcome to Quantum Tic-Tac-Toe!")
        print("\nRules:")
        print("- First move on empty cell → You own it deterministically")
        print("- Move on owned cell → Cell goes into quantum superposition")
        print("- After each turn → All superposed cells collapse via quantum measurement")
        print("- X gets result=0, O gets result=1")

        while not self.game_over:
            if not self.play_turn():
                break

        print("\nThanks for playing Quantum Tic-Tac-Toe!")


def main():
    """Run the game"""
    game = QuantumTicTacToe()
    game.play_game()


main()
