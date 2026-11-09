import argparse
import analysis
from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import random

qbit_lookup_table = [
    #bases = 0
    ["0", "1"],
    #bases = 1
    ["+", "-"]
]

basis_lookup_table = [
    "X", "Z"
]

def generateAlice(n: int, circuit, transmission):
    # Create a random list of bits and bases for Alice
    bases = [random.randint(0, 1) for _ in range(n)]
    bits = [random.randint(0, 1) for _ in range(n)]

    # Set the qubits in the transmission to be sent based on the random bits and bases
    for i in range(n):
        qbit = qbit_lookup_table[bases[i]][bits[i]]
        #if qbit == "0": do nothing
        if qbit == "1":
            circuit.x(transmission[i])
        elif qbit == "+":
            circuit.h(transmission[i])
        elif qbit == "-":
            circuit.h(transmission[i])
            circuit.x(transmission[i])
    circuit.barrier()  # Add a barrier to separate Alice's operations from Bob's or Eve's operations

    return bases, bits  # Return the bases and bits used by Alice for potential analysis

def generateBob(n: int, circuit, transmission, bob):
    bases = [random.randint(0, 1) for _ in range(n)]

    for i in range(n):
        basis = basis_lookup_table[bases[i]]

        if basis == "Z":
            circuit.h(transmission[i])
    for i in range(n):
        circuit.measure(transmission[i], bob[i])  # Measure the qubit in the chosen basis and store the result in Bob's register

    return bases  # Return the bases used by Bob for potential analysis

def generateEve(n: int, circuit, transmission, fraction, eve):
    bases = [random.randint(0, 1) for _ in range(n)]
    num_not_eavesdropped = int(n * (1-fraction))

    for i in range(num_not_eavesdropped):
        #randomly select a qubit to not eavesdrop on
        qubit_index = random.randint(0, n - 1)
        # Mark this qubit as not eavesdropped
        bases[qubit_index] = -1  # Use -1 to indicate this qubit is not to be eavesdropped

    for i in range(n):
        if bases[i] == -1:
            continue  # Skip this qubit as it is not to be eavesdropped
        
        basis = basis_lookup_table[bases[i]]
        if basis == "X":
            circuit.h(transmission[i])
            circuit.measure(transmission[i], eve[i])
            circuit.h(transmission[i])
        elif basis == "Z":
            circuit.measure(transmission[i], eve[i])

    circuit.barrier()  # Add a barrier to separate Eve's operations from Bob's
    return bases  # Return the bases used by Eve for potential analysis

def run_simulation(n: int, do_eavesdropping: bool = False, eve_fraction: float = 0.5, debug: bool = False):
    transmission = QuantumRegister(n, "transmission")
    bob = ClassicalRegister(n, "bob")
    eve = ClassicalRegister(n, "eve") if do_eavesdropping else None
    circuit = QuantumCircuit(transmission, bob, eve) if do_eavesdropping else QuantumCircuit(transmission, bob)

    alice_bases, alice_bits = generateAlice(n, circuit, transmission)
    eve_bases = generateEve(n, circuit, transmission, eve_fraction, eve) if do_eavesdropping else None
    bob_bases = generateBob(n, circuit, transmission, bob)

    backend = AerSimulator()
    compile = transpile(circuit, backend)
    result = backend.run(compile, shots=1, memory=True).result()

    bob_bits = [int(result.get_memory()[0].split()[0][::-1][i]) for i in range(n)]  # Reverse the string to match the order of qubits
    eve_bits = [int(result.get_memory()[0].split()[1][::-1][i]) if do_eavesdropping else None for i in range(n)]

    # Count the errors between Alice's and Bob's bases
    error_count = 0
    for i in range(n):
        if alice_bases[i] != bob_bases[i]:
            error_count += 1

    if debug:
        print("Alice's Bases:   ", [basis_lookup_table[alice_bases[i]] for i in range(n)])
        print("Bob's Bases:     ", [basis_lookup_table[bob_bases[i]] for i in range(n)])
        print("Eve's Bases:     ", [basis_lookup_table[eve_bases[i]] if eve_bases[i] != -1 else "N" for i in range(n)]) if do_eavesdropping else None
        print("Alice's Bits:    ", alice_bits)
        print("Bob's Bits:      ", bob_bits)
        print("Eve's Bits:      ", eve_bits) if do_eavesdropping else None
        print("Error rate between Alice and Bob: {:.2f}%".format((error_count / n) * 100))
        print(circuit.draw())
        
    return alice_bases, alice_bits, bob_bases, eve_bases

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sizing = parser.add_mutually_exclusive_group(required=True)
    sizing.add_argument("-n", type=int, help="number of bits per simulation")
    sizing.add_argument(
        "-simulation-range",
        type=int,
        nargs=3,
        metavar=("START", "STOP", "STEP"),
        help="run once per bit count from START through STOP by STEP",
    )
    parser.add_argument("-s", type=int, help="number of simulations to run with -n")
    parser.add_argument("-o", type=str, default="output", help="output directory for plots")
    parser.add_argument("--eve-dropper", action="store_true", help="simulate Eve eavesdropping on the qubits")
    parser.add_argument("-eve-fraction", type=float, default=0.5, help="fraction of qubits that Eve will eavesdrop on (between 0 and 1)")
    parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode for detailed output")
    args = parser.parse_args()

    if args.n is not None and args.n <= 0:
        parser.error("-n must be a positive integer")
    if args.s is not None and args.s <= 0:
        parser.error("-s must be a positive integer")
    if args.eve_fraction <= 0 or args.eve_fraction > 1:
        parser.error("-eve-fraction must be between 0 and 1")

    if args.simulation_range is not None:
        if args.s is not None:
            parser.error("-s cannot be combined with -simulation-range")
        start, stop, step = args.simulation_range
        if start <= 0 or stop <= 0 or step <= 0:
            parser.error("-simulation-range values must be positive integers")
        if start > stop:
            parser.error("the START value for -simulation-range must not exceed STOP")
        bit_counts = range(start, stop + 1, step)
    else:
        bit_counts = [args.n] * (args.s if args.s is not None else 1)

    output_dir = args.o
    do_eavesdropping = args.eve_dropper
    eve_fraction = args.eve_fraction
    debug = args.debug

    print("Running Simulations...")
    for i, n in enumerate(bit_counts):
        print(f"Simulation {i + 1}/{len(bit_counts)}: n = {n}")
        run_simulation(n, do_eavesdropping=do_eavesdropping, eve_fraction=eve_fraction, debug=debug)
    