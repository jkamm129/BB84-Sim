from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np

def analyze_result_sets(result_sets, alice_bases_sets, bob_bases_sets, alice_bits_sets, args):
    # Analyze the results of the simulation and generate relevant graphs and statistics
    n = len(alice_bases_sets[0])
    num_simulations = len(result_sets)

    from sim import key_checking

    if args.eve_discovery_variance is not None:
        eve_error_rates = {}
        eve_fractions = np.arange(*args.eve_discovery_variance)
        for i in range(num_simulations):
            observed_qubits = int(n * eve_fractions[i % len(eve_fractions)])
            print(f"Analyzing simulation {i + 1}/{num_simulations} with Eve observing {observed_qubits} qubits")
            error_rate, _ = key_checking(
                alice_bases_sets[i],
                bob_bases_sets[i],
                alice_bits_sets[i],
                result_sets[i],
                pass_back_fraction=1.0,
                eve_confidence=0.25
            )

            eve_error_rates.setdefault(observed_qubits, []).append(error_rate)

        observed_qubit_counts = sorted(eve_error_rates)
        average_error_rates = [np.mean(eve_error_rates[count]) for count in observed_qubit_counts]
        plt.plot(observed_qubit_counts, average_error_rates, marker="o")
        plt.xlabel("Number of qubits observed by Eve")
        plt.ylabel("Average error rate")
        plt.title("Average Error Rate vs. Qubits Observed by Eve")
        plt.xticks(observed_qubit_counts)
        output_filename = "error_rate_vs_eve_observed_qubits_"
    else:
        eve_detection_rates = {}
        for i in range(num_simulations):
            # Assemble bit error information for correct bases.
            steps = 10
            for j in range(steps):
                pass_back_fraction = (1.0 * (j + 1)) / steps
                print(f"Analyzing simulation {i + 1}/{num_simulations} with pass-back fraction {pass_back_fraction:.2f}")
                error_rate, eve_detection_rate = key_checking(
                    alice_bases_sets[i],
                    bob_bases_sets[i],
                    alice_bits_sets[i],
                    result_sets[i],
                    pass_back_fraction=pass_back_fraction,
                    eve_confidence=0.25
                )

                # Store the eve detection rate for this pass-back fraction
                if pass_back_fraction not in eve_detection_rates:
                    eve_detection_rates[pass_back_fraction] = []
                eve_detection_rates[pass_back_fraction].append(eve_detection_rate)

        # Calculate the average eve detection rate for each pass-back fraction
        avg_eve_detection_rates = {k: np.mean(v) for k, v in eve_detection_rates.items()}
        pass_back_fractions = sorted(avg_eve_detection_rates)
        detection_rates = [avg_eve_detection_rates[fraction] for fraction in pass_back_fractions]

        x_confidence = np.array(pass_back_fractions)
        y_rates = np.array(detection_rates)

        plt.plot(x_confidence, y_rates, marker="o")
        plt.xlabel("Pass-back fraction")
        plt.ylabel("Eve detection rate")
        plt.title("Eve Detection Rate vs. Pass-back Fraction")
        plt.xticks(x_confidence)
        output_filename = "eve_confidence_vs_pass_back_"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    plt.savefig(args.o + output_filename + str(timestamp) + ".png")
    plt.clf()
    plt.close()
