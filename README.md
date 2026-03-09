# MILP Sports League Optimizer

## Overview
This repository contains the Python implementation of the third project for the Analysis and Synthesis of Algorithms (ASA) course. 

The project solves an optimization problem within a sports league context using Mixed-Integer Linear Programming (MILP). In a tournament where every team plays against each other exactly twice, the objective is to determine the absolute minimum number of future wins a specific team needs to secure first place (or tie for first), given the results of matches that have already been played. If it is mathematically impossible for a team to finish first, the algorithm detects it.

## Architecture and Algorithms
To model and solve this complex sports scenario, the solution utilizes mathematical programming rather than traditional graph algorithms:

* **Mixed-Integer Linear Programming (MILP)**: The problem is formulated as a MILP model and solved using the `pulp` library with the CBC solver (`PULP_CBC_CMD`).
* **Variables**: For every remaining match between a pair of teams `(i, j)`, integer variables are defined to represent the number of wins (`w_i_j`) and draws (`d_i_j`).
* **Constraints**: 
  * The sum of wins and draws for any pair cannot exceed the number of unplayed matches between them.
  * For the target team evaluated, strict constraints enforce that the final points of *all other teams* in the league must be less than or equal to the target team's final points.
* **Objective Function**: The solver minimizes the total number of wins assigned to the target team.
* **Iterative Evaluation**: The program loops through all registered teams, generating and solving a fresh LP model for each one to find their individual minimum required wins. 

## Data Format

### Input
The program reads from *standard input* in the following format:
1. Two integers representing the total number of teams (`n_teams`) and the number of matches already played (`n_played`).
2. Following this, `n_played` lines describe the historic matches with three integers: `team1 team2 result`. 
   * A result of `0` indicates a draw (1 point each).
   * A result equal to `team1 + 1` indicates team 1 won (3 points).
   * A result equal to `team2 + 1` indicates team 2 won (3 points).

### Output
For each team sequentially (from team 1 to `n_teams`), the program prints to *standard output*:
* An integer representing the minimum number of wins that team needs to be the champion. 
* If it is impossible for the team to reach first place regardless of future outcomes, the output is `-1`.

## Installation and Execution

### Prerequisites
* Python 3.x installed.
* `pulp` optimization library.

You can install the required dependency via pip:
```bash
pip install pulp
