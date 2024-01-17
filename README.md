# SymBChainSim-Modified

This project is a modification of GiorgDiama's SymBChainSim, which can be found [here](https://github.com/GiorgDiama/SymBChainSim). The main structure of SymBChainSim has been utilized and some modifications have been made to suit the requirements of my simulation.

The simulation code is part of my academic research, where I aim to investigate the Proof of Authority (PoA) blockchain and small-world network structures.

## Running the Simulation

It is recommended to create a new virtual environment using Python version 3.11.0, as this was the version used during development.

You can create a virtual environment using:

- [Conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) (recommended)
- [venv](https://docs.python.org/3/library/venv.html)

Once you have your virtual environment set up, navigate to the cloned project and follow these steps:

1. Run `pip install -r requirements.txt` to install the required Python libraries.
2. Set your desired simulation parameters in `Configs/base.yaml`. If you wish to use a different file, you can do so by editing `env_vars.yaml`. Please note that all configuration files must be located in the `Configs` directory.
3. Run `python blockchain.py` to start the simulation.

Each module is extensively documented with docstring comments. If the simulation runs successfully, you can start using and extending it as necessary for your work.

## Acknowledgements

Special thanks to [GiorgDiama](https://github.com/GiorgDiama) for the original SymBChainSim project, which served as the foundation for this work.