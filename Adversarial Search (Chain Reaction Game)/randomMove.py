import numpy as np
import os
import time
import math
from copy import deepcopy
import random
import json
from datetime import datetime

state_file = os.path.abspath('gamestate.txt') 

HEURISTIC_PROFILES = [
    {'name': 'Orb Count Only', 'weights': [1.0, 0, 0, 0, 0]},
    {'name': 'Critical Mass Only', 'weights': [0, 1.0, 0, 0, 0]},
    {'name': 'Strategic Position Only', 'weights': [0, 0, 1.0, 0, 0]},
    {'name': 'Opponent Mobility', 'weights': [0.3, 0.2, 0.2, 0.15, 0.15]},
    {'name': 'Explosion Potential', 'weights': [0.5, 0.3, 0.1, 0.05, 0.05]}
]

class ChainReactionGame:
    def __init__(self, rows=9, cols=6):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=object)
        self.current_player = 'B'
        self.game_over = False
        self.winner = None
        self.initialize_board()
        
    def initialize_board(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j] = {'count': 0, 'color': None}
    
    def get_critical_mass(self, row, col):
        if (row == 0 or row == self.rows-1) and (col == 0 or col == self.cols-1):
            return 2  # Corner
        elif row == 0 or row == self.rows-1 or col == 0 or col == self.cols-1:
            return 3  # Edge
        else:
            return 4  # Middle
    
    def is_valid_move(self, row, col, player):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        
        cell = self.board[row][col]
        return cell['count'] == 0 or cell['color'] == player
    
    def make_move(self, row, col, player):
        if not self.is_valid_move(row, col, player) or self.game_over:
            return False
        
        cell = self.board[row][col]
        cell['count'] += 1
        cell['color'] = player
        
        if cell['count'] >= self.get_critical_mass(row, col):
            self.handle_explosion(row, col, player)
        
        if not self.game_over:
            self.current_player = 'B' if player == 'R' else 'R'
        
        return True
    
    def handle_explosion(self, row, col, player):
        if self.game_over:
            return
    
        cell = self.board[row][col]
        critical_mass = self.get_critical_mass(row, col)
    
        if cell['count'] < critical_mass:
            return
        
        while cell['count'] >= critical_mass and not self.game_over:
            cell['count'] -= critical_mass
            if cell['count'] == 0:
                cell['color'] = None
        
            neighbors = self.get_orthogonal_neighbors(row, col)
            for nr, nc in neighbors:
                neighbor = self.board[nr][nc]
                neighbor['count'] += 1
                neighbor['color'] = player
                self.handle_explosion(nr, nc, player)
        
            self.check_game_over()
    
    def get_orthogonal_neighbors(self, row, col):
        neighbors = []
        if row > 0:
            neighbors.append((row-1, col))
        if row < self.rows-1:
            neighbors.append((row+1, col))
        if col > 0:
            neighbors.append((row, col-1))
        if col < self.cols-1:
            neighbors.append((row, col+1))
        return neighbors
    
    def check_game_over(self):
        red_count = 0
        blue_count = 0
        
        for i in range(self.rows):
            for j in range(self.cols):
                cell = self.board[i][j]
                if cell['color'] == 'R':
                    red_count += cell['count']
                elif cell['color'] == 'B':
                    blue_count += cell['count']
        
        if red_count == 0 and blue_count > 0:
            self.game_over = True
            self.winner = 'B'
        elif blue_count == 0 and red_count > 0:
            self.game_over = True
            self.winner = 'R'
        elif red_count == 0 and blue_count == 0:
            self.game_over = True
            self.winner = None
    
    def get_state_copy(self):
        return deepcopy(self.board), self.current_player, self.game_over, self.winner
    
    def set_state(self, board, current_player, game_over, winner):
        self.board = deepcopy(board)
        self.current_player = current_player
        self.game_over = game_over
        self.winner = winner
    
    def to_file_format(self, player_moved):
        lines = []
        lines.append(f"{player_moved} Move:\n")
        
        for row in self.board:
            line = []
            for cell in row:
                if cell['count'] == 0:
                    line.append("0")
                else:
                    line.append(f"{cell['count']}{cell['color']}")
            lines.append(" ".join(line) + "\n")
        
        return "".join(lines)
    
    def from_file_format(self, content):
        lines = content.split('\n')
        if not lines:
            return False
        
        header = lines[0].strip()
        if "Human Move:" in header:
            self.current_player = 'B'
        elif "AI Move:" in header:
            self.current_player = 'R'
        else:
            return False
        
        for i in range(1, min(len(lines), self.rows + 1)):
            line = lines[i].strip()
            if not line:
                continue
                
            cells = line.split()
            for j in range(min(len(cells), self.cols)):
                cell_str = cells[j]
                if cell_str == "0":
                    self.board[i-1][j] = {'count': 0, 'color': None}
                else:
                    count = int(cell_str[:-1])
                    color = cell_str[-1]
                    self.board[i-1][j] = {'count': count, 'color': color}
        
        self.check_game_over()
        return True


class AIPlayer:
    def __init__(self, game, player='B', depth=3, heuristic_weights=None):
        self.game = game
        self.player = player
        self.depth = depth
        self.heuristic_weights = heuristic_weights or HEURISTIC_PROFILES[0]
        self.heuristics = [
            self.heuristic_orb_count,
            self.heuristic_critical_mass,
            self.heuristic_strategic_position,
            self.heuristic_opponent_mobility,
            self.heuristic_explosion_potential
        ]
        
    def get_priority_moves(self, game_state):
        valid_moves = []
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                if game_state.is_valid_move(i, j, self.player):
                    cell = game_state.board[i][j]
                    # Priority: existing orbs > center positions
                    orb_score = cell['count'] * 1000 if cell['color'] == self.player else 0
                    row_score = (game_state.rows - abs(i - game_state.rows//2)) * 100
                    col_score = (game_state.cols - abs(j - game_state.cols//2))
                    priority_score = orb_score + row_score + col_score
                    valid_moves.append((i, j, priority_score))
        
        valid_moves.sort(key=lambda x: x[2], reverse=True)
        return [move[:2] for move in valid_moves]
    
    def minimax_search(self, state, depth_limit, alpha=-math.inf, beta=math.inf, maximizing_player=True):
        priority_moves = self.get_priority_moves(state)
        
        game_copy = ChainReactionGame(state.rows, state.cols)
        game_copy.set_state(*state.get_state_copy())
        
        if depth_limit == 0 or game_copy.game_over:
            return self.evaluate(game_copy), None
        
        if not priority_moves:
            return self.evaluate(game_copy), None
        
        best_move = None
        if maximizing_player:
            max_eval = -math.inf
            for move in priority_moves:
                row, col = move
                temp_game = ChainReactionGame(game_copy.rows, game_copy.cols)
                temp_game.set_state(*game_copy.get_state_copy())
                temp_game.make_move(row, col, self.player)
                
                current_eval, _ = self.minimax_search(temp_game, depth_limit-1, alpha, beta, False)
                
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = move
                
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        else:
            min_eval = math.inf
            opponent = 'R' if self.player == 'B' else 'B'
            for move in priority_moves:
                row, col = move
                temp_game = ChainReactionGame(game_copy.rows, game_copy.cols)
                temp_game.set_state(*game_copy.get_state_copy())
                temp_game.make_move(row, col, opponent)
                
                current_eval, _ = self.minimax_search(temp_game, depth_limit-1, alpha, beta, True)
                
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_move = move
                
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
            
            return min_eval, best_move
    
    def evaluate(self, game_state):
        score = 0
        
        for i, heuristic in enumerate(self.heuristics):
            score += self.heuristic_weights[i] * heuristic(game_state)
        
        return score
    
    def heuristic_orb_count(self, game_state):
        player_count = 0
        opponent_count = 0
        opponent = 'R' if self.player == 'B' else 'B'
        
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                cell = game_state.board[i][j]
                if cell['color'] == self.player:
                    player_count += cell['count']
                elif cell['color'] == opponent:
                    opponent_count += cell['count']
        
        if player_count + opponent_count == 0:
            return 0
        return (player_count - opponent_count) / (player_count + opponent_count)
    
    def heuristic_critical_mass(self, game_state):
        score = 0
        opponent = 'R' if self.player == 'B' else 'B'
        
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                cell = game_state.board[i][j]
                if cell['color'] == self.player:
                    critical_mass = game_state.get_critical_mass(i, j)
                    ratio = cell['count'] / critical_mass
                    score += ratio
                elif cell['color'] == opponent:
                    critical_mass = game_state.get_critical_mass(i, j)
                    ratio = cell['count'] / critical_mass
                    score -= ratio
        
        return score / (game_state.rows * game_state.cols)
    
    def heuristic_strategic_position(self, game_state):
        score = 0
        opponent = 'R' if self.player == 'B' else 'B'
        
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                cell = game_state.board[i][j]
                critical_mass = game_state.get_critical_mass(i, j)
                position_value = 1 / critical_mass 
                
                if cell['color'] == self.player:
                    score += position_value * cell['count']
                elif cell['color'] == opponent:
                    score -= position_value * cell['count']
        
        return score
    
    def heuristic_opponent_mobility(self, game_state):
        opponent = 'R' if self.player == 'B' else 'B'
        opponent_moves = 0
        player_moves = 0
        
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                if game_state.is_valid_move(i, j, self.player):
                    player_moves += 1
                if game_state.is_valid_move(i, j, opponent):
                    opponent_moves += 1
        
        if player_moves + opponent_moves == 0:
            return 0
        return (player_moves - opponent_moves) / (player_moves + opponent_moves)
    
    def heuristic_explosion_potential(self, game_state):
        score = 0
        opponent = 'R' if self.player == 'B' else 'B'
        
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                cell = game_state.board[i][j]
                if cell['color'] == self.player:
                    critical_mass = game_state.get_critical_mass(i, j)
                    if cell['count'] == critical_mass - 1:
                        neighbors = game_state.get_orthogonal_neighbors(i, j)
                        for ni, nj in neighbors:
                            neighbor = game_state.board[ni][nj]
                            if neighbor['color'] == opponent:
                                score += 1
                            elif neighbor['color'] is None:
                                score += 0.5
                elif cell['color'] == opponent:
                    critical_mass = game_state.get_critical_mass(i, j)
                    if cell['count'] == critical_mass - 1:
                        neighbors = game_state.get_orthogonal_neighbors(i, j)
                        for ni, nj in neighbors:
                            neighbor = game_state.board[ni][nj]
                            if neighbor['color'] == self.player:
                                score -= 1
        
        return score / (game_state.rows * game_state.cols)


class PriorityRandomAgent:
    def __init__(self, game, player='R'):
        self.game = game
        self.player = player
    
    def get_move(self, game_state):
        valid_moves = []
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                if game_state.is_valid_move(i, j, self.player):
                    cell = game_state.board[i][j]
                    # Priority: existing orbs > center positions
                    orb_score = cell['count'] * 1000 if cell['color'] == self.player else 0
                    row_score = (game_state.rows - abs(i - game_state.rows//2)) * 100
                    col_score = (game_state.cols - abs(j - game_state.cols//2))
                    priority_score = orb_score + row_score + col_score
                    valid_moves.append((i, j, priority_score))
        
        if valid_moves:
            valid_moves.sort(key=lambda x: x[2], reverse=True)
            return valid_moves[0][:2]  # Return the highest priority move
        return None


class GameUI:
    def __init__(self, game, ai_player=None, state_file='gamestate.txt'):
        self.game = game
        self.ai_player = ai_player
        self.state_file = state_file
        self.ai_vs_ai = False
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_board(self):
        self.clear_screen()
        print("Chain Reaction Game\n")
        print(f"Current Player: {'Red (R)' if self.game.current_player == 'R' else 'Blue (B)'}\n")
        
        print("   " + " ".join(f"{i:2}" for i in range(self.game.cols)))
        
        for i in range(self.game.rows):
            print(f"{i:2} ", end="")
            
            for j in range(self.game.cols):
                cell = self.game.board[i][j]
                if cell['count'] == 0:
                    print(" . ", end="")
                else:
                    color_code = "\033[91m" if cell['color'] == 'R' else "\033[94m"
                    print(f"{color_code}{cell['count']}{cell['color']}\033[0m ", end="")
            print()
        
        print()
    
    def play_random_vs_ai(self):
        """Play a game between a random agent and an AI"""
        random_agent = PriorityRandomAgent(self.game, 'R')
        self.game.current_player = 'R'  # Random agent goes first
        
        move_count = 0
        start_time = time.time()
        
        while not self.game.game_over:
            self.display_board()
            print(f"Move {move_count + 1}")
            
            if self.game.current_player == 'R':
                print("Random Agent (Red) is thinking...")
                move = random_agent.get_move(self.game)
                player = "Random (Red)"
            else:
                print("AI (Blue) is thinking...")
                _, move = self.ai_player.minimax_search(self.game, self.ai_player.depth)
                player = "AI (Blue)"
            
            if move:
                row, col = move
                print(f"{player} moves to ({row}, {col})")
                self.game.make_move(row, col, self.game.current_player)
                move_count += 1
            else:
                print(f"{player} has no valid moves!")
                self.game.current_player = 'B' if self.game.current_player == 'R' else 'R'
            
            time.sleep(1)  # Pause to observe the game
        
        end_time = time.time()
        self.display_board()
        
        if self.game.winner == 'R':
            print(f"Random Agent (Red) wins in {move_count} moves! Time: {end_time-start_time:.2f}s")
        else:
            print(f"AI (Blue) wins in {move_count} moves! Time: {end_time-start_time:.2f}s")
        
        return self.game.winner, move_count, end_time - start_time


def select_heuristic_profile():
    print("\nSelect AI Heuristic Profile:")
    print("1. Orb Count Only")
    print("2. Critical Mass Only")
    print("3. Strategic Position Only")
    print("4. Opponent Mobility (Default)")
    print("5. Explosion Potential")
    
    heuristic_choice = input("Enter choice (1-5, default 4): ").strip()
    try:
        heuristic_choice = int(heuristic_choice) - 1
        if heuristic_choice < 0 or heuristic_choice > 4:
            heuristic_choice = 3
    except ValueError:
        heuristic_choice = 3
    
    heuristic_profiles = [
        {'name': 'Orb Count', 'weights': [1.0, 0, 0, 0, 0]},
        {'name': 'Critical Mass', 'weights': [0, 1.0, 0, 0, 0]},
        {'name': 'Strategic Position', 'weights': [0, 0, 1.0, 0, 0]},
        {'name': 'Opponent Mobility', 'weights': [0.3, 0.2, 0.2, 0.15, 0.15]},
        {'name': 'Explosion Potential', 'weights': [0.5, 0.3, 0.1, 0.05, 0.05]}
    ]
    
    selected = heuristic_profiles[heuristic_choice]
    print(f"Selected heuristic: {selected['name']}")
    return selected['weights']


def main():
    print("Chain Reaction Game - Random vs AI")
    print("=================================")
    
    game = ChainReactionGame()
    
    # Select AI settings
    heuristic_weights = select_heuristic_profile()
    depth = input("Enter AI depth level (1-5, default 3): ").strip()
    try:
        depth = int(depth)
        if depth < 1 or depth > 5:
            depth = 3
    except ValueError:
        depth = 3
    
    # Create AI player
    ai_player = AIPlayer(game, 'B', depth, heuristic_weights)
    ui = GameUI(game, ai_player)
    
    # Play the game
    ui.play_random_vs_ai()


if __name__ == "__main__":
    main()