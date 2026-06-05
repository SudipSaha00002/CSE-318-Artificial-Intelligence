# CSE 318: Artificial Intelligence Sessional

This repository contains the assignments and projects completed as part of the **CSE 318 (Artificial Intelligence)** course. The implementations cover fundamental search algorithms, heuristic optimization, adversarial search, and machine learning models from scratch.

---

## 📂 Repository Structure

The repository is organized into four main sections, each corresponding to a specific assignment/project:

```
CSE-318-Artificial-Intelligence/
│
├── 🧩 N_Puzzle/                                    # Assignment 1: A* Search
│   ├── N_Puzzle.cpp                                # A* Solver implementation (C++)
│   ├── N_Puzzle_testcases/                         # Sample testcases for puzzle states
│   └── CSE318-Offline1-Spec.pdf                    # Assignment specification
│
├── 🕸️ Max-Cut/                                     # Assignment 2: Heuristic Optimization (GRASP)
│   ├── Max_Cut.cpp                                 # GRASP & Local Search solver (C++)
│   ├── plot.py                                     # Python script for plotting results
│   ├── 2105152.csv                                 # Generated performance comparison data
│   ├── Report.pdf                                  # Analysis & results report
│   ├── set1/                                       # Graph datasets (G1 to G54)
│   └── Offline_02_CSE318.pdf                       # Assignment specification
│
├── ⚔️ Adversarial Search (Chain Reaction Game)/      # Assignment 3: Adversarial Search & Minimax
│   ├── Chain Reaction.py                           # Core game logic and AI implementation (Python)
│   ├── humanVsAi.py                                # Script for playing against the AI (Python)
│   ├── randomMove.py                               # Random move agent script (Python)
│   ├── gamestate.txt                               # Tracks the current state of the board
│   ├── CSE 318 Assignment-03.pdf                   # Assignment specification
│   └── 2105152_Report.pdf                          # Analysis of heuristic profiles
│
└── 🌲 Decision Tree/                               # Assignment 4: Machine Learning from Scratch
    ├── Decision Tree.cpp                           # ID3 Decision Tree algorithm (C++)
    ├── Datasets/                                   # Preprocessed dataset files (Iris.csv, adult.data)
    ├── Report.pdf                                  # Evaluation report
    └── CSE318_Offline 4.pdf                        # Assignment specification
```

---

## 🧩 1. N-Puzzle Solver (A* Search)

An implementation of the **A\* search algorithm** to solve the $N^2-1$ puzzle (e.g., 8-puzzle, 15-puzzle) on a grid of size $N \times N$.

### Features
*   **Solvability Check:** Computes the number of inversions and blank tile position to determine if a puzzle configuration is solvable before running the search.
*   **Multiple Heuristics:**
    1.  **Hamming Distance:** Number of misplaced tiles.
    2.  **Manhattan Distance:** Sum of vertical and horizontal distances from tiles to their goal positions.
    3.  **Euclidean Distance:** Straight line distance from tiles to goal positions.
    4.  **Linear Conflict:** Manhattan distance plus a penalty of $2$ for tiles in the same row/column that are in each other's way.
*   **Search Statistics:** Reports the minimum number of moves, nodes explored, and nodes expanded.

---

## 🕸️ 2. Max-Cut Problem Solver (GRASP)

An implementation of the **Greedy Randomized Adaptive Search Procedure (GRASP)** meta-heuristic to find the Maximum Cut in undirected graphs.

### Features
*   **Constructive Heuristics:**
    *   *Simple Randomized Algorithm* (creates cuts by random vertex partitioning).
    *   *Greedy Constructive Algorithm* (builds the cut vertex-by-vertex based on maximum weight additions).
    *   *Semi-Greedy (RCL-based) Algorithm* (selects vertex randomly from a Restricted Candidate List).
*   **Local Search Improvement:** Iteratively shifts vertices between partition sets $X$ and $Y$ if the movement improves the total cut weight.
*   **Comparison Framework:** Automatically runs all methods over several benchmarks (`rud` graph format) and outputs performance metrics (best value, average local search iterations, execution time, etc.) into a CSV file.

---

## ⚔️ 3. Adversarial Search (Chain Reaction Game)

An intelligent agent designed to play the **Chain Reaction** game using **Adversarial Search**.

### Features
*   **AI Engine:** **Minimax algorithm** with **Alpha-Beta Pruning** to explore the game tree efficiently.
*   **Heuristic Profiles:** Incorporates five weighted heuristics to evaluate board states:
    1.  **Orb Count:** The difference in total orbs between the AI and the opponent.
    2.  **Critical Mass Potential:** Rewards placing orbs in cells close to exploding.
    3.  **Strategic Positions:** Assigns higher value to corners and edges which have lower critical mass thresholds.
    4.  **Opponent Mobility:** Penalizes states where the opponent has many valid moves.
    5.  **Explosion Potential:** Predicts chain reactions and potential opponent orb captures.
*   **Multiple Modes:** Supports *Human vs Human*, *Human vs AI*, and *AI vs AI* matches.

---

## 🌲 4. Decision Tree Classifier from Scratch

An implementation of the **ID3 Decision Tree induction algorithm** built entirely from scratch in C++.

### Features
*   **Splitting Criteria:**
    *   **Information Gain (IG)** (based on Shannon Entropy).
    *   **Information Gain Ratio (IGR)** (penalizes multi-valued attributes).
    *   **Normalized Weighted Information Gain (NWIG)** (handles attributes with many values using a custom penalty factor).
*   **Dataset Support:** Standard preprocessing pipelines for both the **Iris Dataset** (discrete binning of numeric attributes) and the **Adult Dataset** (handling continuous variables, missing data handling, and binning).
*   **Evaluation:** Evaluates accuracy, node count, and maximum tree depth using $80/20$ train-test splits averaged over $20$ runs.

---

## 🚀 Running the Projects

### C++ Projects (N-Puzzle, Max-Cut, Decision Tree)
Compile the source files using a modern C++ compiler supporting `C++17` or higher (e.g., `g++`):

```bash
# N-Puzzle Solver
g++ -O3 N_Puzzle/N_Puzzle.cpp -o n_puzzle_solver
./n_puzzle_solver

# Max-Cut Solver
g++ -O3 Max-Cut/Max_Cut.cpp -o max_cut_solver
./max_cut_solver

# Decision Tree Classifier (Arguments: <criterion [IG/IGR/NWIG]> <maxDepth [0 for no limit]>)
g++ -O3 "Decision Tree/Decision Tree.cpp" -o decision_tree
./decision_tree IG 10
```

### Python Projects (Chain Reaction Game)
Ensure you have `numpy` installed:
```bash
pip install numpy
```
Run the interactive console game:
```bash
python "Adversarial Search (Chain Reaction Game)/humanVsAi.py"
```

---
*Created as part of CSE 318 (Artificial Intelligence Sessional) course curriculum.*
