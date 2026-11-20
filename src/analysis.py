from matplotlib import pyplot as plt
import numpy as np

def analyze_result_sets(result_sets, alice_bases_sets, bob_bases_sets, alice_bits_sets, output_dir):
    # Analyze the results of the simulation and generate relevant graphs and statistics
    n = len(alice_bases_sets[0])
    num_simulations = len(result_sets)

    # Assemble information across each simulation
    eve_detection_rates = {} # The dictionary to hold the eve detection rates as values and the pass-back fraction as keys
    from sim import key_checking

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
    x_confidence = np.array(avg_eve_detection_rates.keys)
    y_rates = np.array(avg_eve_detection_rates.values)

    plt.plot(x_confidence, y_rates)
    plt.show()