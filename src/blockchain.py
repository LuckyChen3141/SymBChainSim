import io
import sys
from datetime import datetime
from Chain.Manager import Manager
import random, numpy
import Chain.Consensus.BigFoot.BigFoot as BigFoot
import Chain.Consensus.PBFT.PBFT as PBFT
from Chain.Metrics import SimulationState, Metrics

# Set the seed for random number generation
seed = 5
random.seed(seed)
numpy.random.seed(seed)

def run():
    # Create a Manager object and set up the simulation
    manager = Manager()
    manager.set_up()

    # Start the simulation and measure the runtime
    t = datetime.now()
    print("Simulation started...")
    manager.run()
    runtime = datetime.now() - t
    print("Simulation finished.")

    # Open a text file for writing the report
    with open('simulation_report.txt', 'w') as report_file:
        print("Writing report...")

        # Write the simulation timestamp and runtime to the report
        report_file.write(f"Simulation Timestamp: {datetime.now()}\n")
        report_file.write(f"Simulation Execution Time: {runtime}\n\n")

        # Write information about each node to the report
        for n in manager.sim.nodes:
            report_file.write(f"Node: {n}\n")
            report_file.write(f"Validator: {n.validator}\n")
            report_file.write(f"Total Blocks: {n.blockchain_length()}\n")
            report_file.write(f"PBFT Blocks: {len([x for x in n.blockchain if x.consensus == PBFT])}\n")
            report_file.write(f"BigFoot Blocks: {len([x for x in n.blockchain if x.consensus == BigFoot])}\n")
            report_file.write(f'Node {n} is at location {n.location} and has {len(n.neighbours)} neighbours at locations \n {[neighbour.location for neighbour in n.neighbours]}\n')
        # Store the simulation state and measure the metrics
        SimulationState.store_state(manager.sim)
        Metrics.measure_all(SimulationState.blockchain_state)

        # Redirect stdout to a string buffer, print the metrics, and then reset stdout
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        Metrics.print_metrics()
        sys.stdout = old_stdout

        # Write the metrics to the report
        report_file.write("\nMetrics:\n")
        report_file.write(buffer.getvalue())

    print("Report written to simulation_report.txt")

run()


