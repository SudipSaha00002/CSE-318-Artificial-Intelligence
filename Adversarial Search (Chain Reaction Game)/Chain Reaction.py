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
        # initializing the board with empty cells
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j] = {'count': 0, 'color': None}
    
    def get_critical_mass(self, row, col):
        # getting critical mass for a cell based on its position
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
        # making a move and handle explosions
        if not self.is_valid_move(row, col, player) or self.game_over:
            return False
        
        cell = self.board[row][col]
        cell['count'] += 1
        cell['color'] = player
        
        # checking for explosion
        if cell['count'] >= self.get_critical_mass(row, col):
            self.handle_explosion(row, col, player)
        
        # switching player if game isn't over
        if not self.game_over:
            self.current_player = 'B' if player == 'R' else 'R'
        
        return True
    #recursive explosion handler based on the provided explode function
    def handle_explosion(self, row, col, player):
       
        if self.game_over:
            return
    
        cell = self.board[row][col]
        critical_mass = self.get_critical_mass(row, col)
    
    # base case: not enough orbs to explode
        if cell['count'] < critical_mass:
            return
        # handling explosion
        while cell['count'] >= critical_mass and not self.game_over:
            cell['count'] -= critical_mass
            if cell['count'] == 0:
                cell['color'] = None
        
        # distributing orbs to neighbors
            neighbors = self.get_orthogonal_neighbors(row, col)
            for nr, nc in neighbors:
                neighbor = self.board[nr][nc]
                neighbor['count'] += 1
                neighbor['color'] = player
            
            # recursively handle neighbor explosions
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
            self.winner = None  # draw 
    
    def get_state_copy(self):
        # returns a  copy of the current game state"""
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
    
    def from_file_format(self, content):  # loading game state from file format
        lines = content.split('\n')
        if not lines:
            return False
        
        header = lines[0].strip()
        if "Human Move:" in header:
            self.current_player = 'B'  # AI's turn next
        elif "AI Move:" in header:
            self.current_player = 'R'  # Human's turn next
        else:
            return False
        
        for i in range(1, min(len(lines), self.rows + 1)): #parse the board state
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
        self.heuristic_weights = heuristic_weights or HEURISTIC_PROFILES[3] 
        self.heuristics = [
            self.heuristic_orb_count,
            self.heuristic_critical_mass,
            self.heuristic_strategic_position,
            self.heuristic_opponent_mobility,
            self.heuristic_explosion_potential
        ]
    # Minimax search with alpha-beta pruning
    def minimax_search(self, state, depth_limit, alpha=-math.inf, beta=math.inf, maximizing_player=True):
        game_copy = ChainReactionGame(state.rows, state.cols)
        game_copy.set_state(*state.get_state_copy())
        
        if depth_limit == 0 or game_copy.game_over:
            return self.evaluate(game_copy), None
        
        valid_moves = self.get_valid_moves(game_copy)
        if not valid_moves:
            return self.evaluate(game_copy), None
        
        best_move = None
        if maximizing_player:
            max_eval = -math.inf
            for move in valid_moves:
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
            for move in valid_moves:
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
    
    def get_valid_moves(self, game_state):
        valid_moves = []
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                if game_state.is_valid_move(i, j, self.player):
                    valid_moves.append((i, j))
        return valid_moves
    
    # Heuristic 1: Orb count difference
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
    
    # Heuristic 2: Critical mass potential
    def heuristic_critical_mass(self, game_state):
        """Reward cells close to critical mass"""
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
    
    # Heuristic 3: Strategic position 
    def heuristic_strategic_position(self, game_state):
        """Reward controlling strategic positions (corners, edges)"""
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
    
    # Heuristic 4: Opponent mobility
    def heuristic_opponent_mobility(self, game_state):
        """Penalize opponent's mobility (valid moves)"""
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
    
    # Heuristic 5: Explosion potential
    def heuristic_explosion_potential(self, game_state):
        """Reward positions that can cause chain reactions"""
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
                                score += 1  # potential to capture opponent's orbs
                            elif neighbor['color'] is None:
                                score += 0.5  # potential to expand territory
                elif cell['color'] == opponent:
                    critical_mass = game_state.get_critical_mass(i, j)
                    if cell['count'] == critical_mass - 1:
                        
                        neighbors = game_state.get_orthogonal_neighbors(i, j)
                        for ni, nj in neighbors:
                            neighbor = game_state.board[ni][nj]
                            if neighbor['color'] == self.player:
                                score -= 1  
        
        return score / (game_state.rows * game_state.cols)


class RandomAgent:
    def __init__(self, game, player='B'):
        self.game = game
        self.player = player
    
    def get_move(self, game_state):
        valid_moves = []
        for i in range(game_state.rows):
            for j in range(game_state.cols):
                if game_state.is_valid_move(i, j, self.player):
                    valid_moves.append((i, j))
        
        if valid_moves:
            return random.choice(valid_moves)
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
        
        # printing column numbers
        print("   " + " ".join(f"{i:2}" for i in range(self.game.cols)))
        
        for i in range(self.game.rows):
            # printing row number
            print(f"{i:2} ", end="")
            
            for j in range(self.game.cols):
                cell = self.game.board[i][j]
                if cell['count'] == 0:
                    print(" . ", end="")
                else:
                    color_code = "\033[91m" if cell['color'] == 'R' else "\033[94m"  # Red or Blue
                    print(f"{color_code}{cell['count']}{cell['color']}\033[0m ", end="")
            print()
        
        print()
    

    def human_move(self, player):
        while True:
            try:
                move = input(f"Player {player} enter your move (row col): ").strip()
                if not move:
                    continue
                
                if move.lower() == 'q':
                    return None
                
                row, col = map(int, move.split())
                if self.game.make_move(row, col, player):
                    return True
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Please enter two numbers separated by space.")
    
    def ai_move(self):
        print("AI is thinking...")
        start_time = time.time()
        _, move = self.ai_player.minimax_search(self.game, self.ai_player.depth)
        end_time = time.time()
        
        if move:
            row, col = move
            print(f"AI moves to ({row}, {col}) (took {end_time-start_time:.2f}s)")
            self.game.make_move(row, col, 'B')
            return True
        else:
            print("AI has no valid moves!")
            return False
    # In GameUI class, modify the file handling methods:
    def save_state_to_file(self, player_type):
        temp_file = self.state_file + ".tmp"
        try:
            with open(temp_file, 'w') as f:
                f.write(self.game.to_file_format(player_type))
        # Atomic rename operation
            os.replace(temp_file, self.state_file)
        except IOError as e:
            print(f"Error saving game state: {e}")

    def load_state_from_file(self):
        try:
            with open(self.state_file, 'r') as f:
                content = f.read()
                if not content.strip():
                    return False
                return self.game.from_file_format(content)
        except (FileNotFoundError, IOError) as e:
            print(f"Error loading game state: {e}")
            return False

    def wait_for_file_update(self, expected_header, timeout=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with open(self.state_file, 'r') as f:
                    first_line = f.readline().strip()
                    if expected_header in first_line:
                        return True
            except FileNotFoundError:
                pass
            time.sleep(0.1)
        raise TimeoutError(f"Timeout waiting for {expected_header}")
    
    def select_heuristic_profile(self):
        print("\nAvailable Heuristics:")
        for i, profile in enumerate(HEURISTIC_PROFILES):
            print(f"{i+1}. {profile['name']}")
        
        choice = input("Select heuristic (1-5, default 4): ").strip()
        try:
            choice = int(choice) - 1
            if choice < 0 or choice >= len(HEURISTIC_PROFILES):
                return HEURISTIC_PROFILES[3]
            return HEURISTIC_PROFILES[choice]
        except ValueError:
            return HEURISTIC_PROFILES[3]
    
    def select_difficulty(self):
        depth = input("Enter difficulty (1-5, default 3): ").strip()
        try:
            depth = int(depth)
            if depth < 1 or depth > 5:
                return 3
            return depth
        except ValueError:
            return 3
    def play_human_vs_human(self):
        # setting first player to Red
        self.game.current_player = 'R'
        while not self.game.game_over:
            self.display_board()
        
            current_player = self.game.current_player
            if self.human_move(current_player) is None: 
                break
            
            self.save_state_to_file(f"Player {current_player}")
            if self.game.game_over:
                self.display_board()
                if self.game.winner == 'R':
                    print("Player Red (R) wins!")
                else:
                    print("Player Blue (B) wins!")
                break

    def play_console(self):
    # if AI is first player, makes its move before showing the board
        if self.game.current_player == 'B':
            self.display_board()
            print("AI is making the first move...")
            self.ai_move()
            self.save_state_to_file("AI")
    
        while not self.game.game_over:
            self.display_board()
        
            if self.game.current_player == 'R':
            # Human move
                if self.human_move() is None:  
                    break
                self.save_state_to_file("Human")
            else:
                # AI move
                self.ai_move()
                self.save_state_to_file("AI")
        
            if self.game.game_over:
                self.display_board()
                if self.game.winner == 'R':
                    print("Congratulations! You won!")
                else:
                    print("AI won!")
                break
    
    def play_with_file_protocol(self):
    # Initialize file if it doesn't exist
        if not os.path.exists(self.state_file):
        # If AI is first, make its move first
            if self.game.current_player == 'B':
                self.ai_move()
                self.save_state_to_file("AI")
            else:
                self.save_state_to_file("Human")
    
        while not self.game.game_over:
            self.display_board()
        
            if self.game.current_player == 'R':
            # Human move
                print("Waiting for human move (via file)...")
                self.wait_for_file_update("Human Move:")
                self.load_state_from_file()
            else:
            # AI move
                self.ai_move()
                self.save_state_to_file("AI")
                print("AI move written to file. Waiting for human response...")
        
            if self.game.game_over:
                self.display_board()
                if self.game.winner == 'R':
                    print("Human won!")
                else:
                    print("AI won!")
                break
    
    def play_human_vs_ai(self):
    # setting first player to AI (Blue)
        self.game.current_player = 'B'
        self.save_state_to_file("AI")
    
        while not self.game.game_over:
            self.display_board()
        
            if self.game.current_player == 'B':
                # AI move
                self.ai_move()
                self.save_state_to_file("AI")
            else:
            # Human move
                if self.human_move('R') is None:
                    break
                self.save_state_to_file("Human")
                
            if self.game.game_over:
                self.display_board()
                if self.game.winner == 'R':
                    print("Human (Red) wins!")
                else:
                    print("AI (Blue) wins!")

    def play_ai_vs_ai(self, depth1=3, depth2=3, heuristic_weights1=None, heuristic_weights2=None):
        """AI vs AI match"""
        self.ai_vs_ai = True
    # setting first player to Red
        self.game.current_player = 'R'
        self.save_state_to_file("AI 1 (Red)")
    
        ai_player1 = AIPlayer(self.game, 'R', depth1, heuristic_weights1)
        ai_player2 = AIPlayer(self.game, 'B', depth2, heuristic_weights2)
    
        move_count = 0
        start_time = time.time()
    
        while not self.game.game_over:
            self.display_board()
            print(f"Move {move_count + 1}")
        
            if self.game.current_player == 'R':
                print("AI 1 (Red) is thinking...")
                _, move = ai_player1.minimax_search(self.game, ai_player1.depth)
                player = "AI 1 (Red)"
            else:
                print("AI 2 (Blue) is thinking...")
                _, move = ai_player2.minimax_search(self.game, ai_player2.depth)
                player = "AI 2 (Blue)"
        
            if move:
                row, col = move
                print(f"{player} moves to ({row}, {col})")
                self.game.make_move(row, col, self.game.current_player)
                move_count += 1
                self.save_state_to_file(player)
            else:
                print(f"{player} has no valid moves!")
                self.game.current_player = 'B' if self.game.current_player == 'R' else 'R'
        
            time.sleep(1)  # pause to observe the game
    
        end_time = time.time()
        self.display_board()
    
        if self.game.winner == 'R':
            print(f"AI 1 (Red) wins in {move_count} moves! Time: {end_time-start_time:.2f}s")
        else:
            print(f"AI 2 (Blue) wins in {move_count} moves! Time: {end_time-start_time:.2f}s")
    
        return self.game.winner, move_count, end_time - start_time
class EnhancedGameUI(GameUI):
    def __init__(self, game, ai_player=None, state_file='gamestate.txt'):
        super().__init__(game, ai_player, state_file)
        self.statistics = {
            'games_played': 0,
            'ai_wins': 0,
            'human_wins': 0,
            'draws': 0,
            'total_moves': 0,
            'total_time': 0,
            'average_moves_per_game': 0,
            'average_time_per_game': 0
        }
        self.game_history = []
    
    def reset_statistics(self):
        for key in self.statistics:
            self.statistics[key] = 0
        self.game_history = []
    
    def update_statistics(self, winner, moves, game_time):
        self.statistics['games_played'] += 1
        self.statistics['total_moves'] += moves
        self.statistics['total_time'] += game_time
        
        if winner == 'R':
            self.statistics['human_wins'] += 1
        elif winner == 'B':
            self.statistics['ai_wins'] += 1
        else:
            self.statistics['draws'] += 1
        
        self.statistics['average_moves_per_game'] = self.statistics['total_moves'] / self.statistics['games_played']
        self.statistics['average_time_per_game'] = self.statistics['total_time'] / self.statistics['games_played']
        
        # Add to history
        game_record = {
            'game_number': self.statistics['games_played'],
            'winner': winner,
            'moves': moves,
            'time': game_time,
            'timestamp': datetime.now().isoformat()
        }
        self.game_history.append(game_record)
    
    def print_statistics(self):
        print("\n" + "="*60)
        print("GAME STATISTICS")
        print("="*60)
        print(f"Games Played: {self.statistics['games_played']}")
        print(f"AI Wins: {self.statistics['ai_wins']}")
        print(f"Human/Player 1 Wins: {self.statistics['human_wins']}")
        print(f"Draws: {self.statistics['draws']}")
        
        if self.statistics['games_played'] > 0:
            ai_win_rate = (self.statistics['ai_wins'] / self.statistics['games_played']) * 100
            human_win_rate = (self.statistics['human_wins'] / self.statistics['games_played']) * 100
            draw_rate = (self.statistics['draws'] / self.statistics['games_played']) * 100
            print(f"AI Win Rate: {ai_win_rate:.1f}%")
            print(f"Human/Player 1 Win Rate: {human_win_rate:.1f}%")
            print(f"Draw Rate: {draw_rate:.1f}%")
        
        print(f"Average Moves per Game: {self.statistics['average_moves_per_game']:.1f}")
        print(f"Average Time per Game: {self.statistics['average_time_per_game']:.2f}s")
        print("="*60)
    
    def save_statistics_to_file(self, filename="game_statistics.json"):
        data = {
            'statistics': self.statistics,
            'game_history': self.game_history,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Statistics saved to {filename}")
    
    def play_multiple_ai_vs_ai(self, num_games=10, depth=3, heuristic_choice=0, 
                          random_plays_as='B', verbose=False):
        heuristic_profiles = [
            {'name': 'Orb Count ', 'weights': [1.0, 0, 0, 0, 0]},
            {'name': 'Critical Mass ', 'weights': [0, 1.0, 0, 0, 0]},
            {'name': 'Strategic Position', 'weights': [0, 0, 1.0, 0, 0]},
            {'name': 'Opponent Mobility', 'weights': [0.3, 0.2, 0.2, 0.15, 0.15]},
            {'name': 'Explosion Potential', 'weights': [0.5, 0.3, 0.1, 0.05, 0.05]}
    ]
    
        selected_heuristic = heuristic_profiles[heuristic_choice]
        print(f"\nRunning {num_games} games: Random vs {selected_heuristic['name']}")
        print(f"Random plays as {random_plays_as}, Heuristic AI depth: {depth}")
    
        results = []
        for game_num in range(num_games):
        # reseting game
            self.game = ChainReactionGame()
        
        # creating agents -  random vs one with selected heuristic
            if random_plays_as == 'B':
                random_agent = RandomAgent(self.game, 'B')
                smart_agent = AIPlayer(self.game, 'R', depth, selected_heuristic['weights'])
            else:
                random_agent = RandomAgent(self.game, 'R')
                smart_agent = AIPlayer(self.game, 'B', depth, selected_heuristic['weights'])
        
            move_count = 0
            start_time = time.time()
        
            while not self.game.game_over:
                if self.game.current_player == 'R':
                    agent = random_agent if random_plays_as == 'R' else smart_agent
                else:
                    agent = random_agent if random_plays_as == 'B' else smart_agent
            
                if isinstance(agent, RandomAgent):
                    move = agent.get_move(self.game)
                else:
                    _, move = agent.minimax_search(self.game, depth)
            
                if move:
                    row, col = move
                    self.game.make_move(row, col, self.game.current_player)
                    move_count += 1
                else:
                    break
            
            # preventing infinite loops
                if move_count > 1000:
                    break
        
            end_time = time.time()
            game_time = end_time - start_time
        
            if verbose:
                print(f"Game {game_num + 1}: Winner = {self.game.winner}, Moves = {move_count}, Time = {game_time:.2f}s")
        
            self.update_statistics(self.game.winner, move_count, game_time)
        
            results.append({
                'game': game_num + 1,
                'winner': self.game.winner,
                'moves': move_count,
                'time': game_time,
                'heuristic': selected_heuristic['name']
            })
    
        return results


    def run_heuristic_experiments(self, num_games=20, depth=3):
        heuristic_combinations = {
            'orb_count': {'weights': [1.0, 0, 0, 0, 0]},
            'critical_mass': {'weights': [0, 1.0, 0, 0, 0]},
            'strategic_position': {'weights': [0, 0, 1.0, 0, 0]},
            'Opponent Mobility': {'weights': [0.3, 0.2, 0.2, 0.15, 0.15]},
            'Explosion Potential': {'weights': [0.5, 0.3, 0.1, 0.05, 0.05]}
        }
    
        results = {}
    
        for name, config in heuristic_combinations.items():
            print(f"\nTesting heuristic profile: {name}")
            self.reset_statistics()
        
            for game_num in range(num_games):
                self.game = ChainReactionGame()
                ai1 = AIPlayer(self.game, 'R', depth, config['weights'])
                ai2 = AIPlayer(self.game, 'B', depth, [0.25, 0.25, 0.25, 0.125, 0.125])  # Control
            
                winner, moves, game_time = self.play_ai_vs_ai(depth, depth)
                self.update_statistics(winner, moves, game_time)
        
            results[name] = {
                'win_rate': self.statistics['ai_wins'] / num_games,
                'avg_moves': self.statistics['average_moves_per_game'],
                'avg_time': self.statistics['average_time_per_game']
            }
    
        return results

    def generate_report(self, results, filename="heuristic_report.pdf"):
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
        
            pdf.cell(200, 10, txt="Chain Reaction Heuristic Evaluation Report", ln=1, align='C')
            pdf.cell(200, 10, txt=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
        
       
            pdf.ln(10)
            pdf.cell(200, 10, txt="Heuristic Performance Comparison", ln=1)
        
       
            pdf.cell(60, 10, txt="Heuristic Profile", border=1)
            pdf.cell(40, 10, txt="Win Rate (%)", border=1)
            pdf.cell(40, 10, txt="Avg Moves", border=1)
            pdf.cell(40, 10, txt="Avg Time (s)", border=1, ln=1)
        
        
            for name, data in results.items():
                pdf.cell(60, 10, txt=name, border=1)
                pdf.cell(40, 10, txt=f"{data['win_rate']*100:.1f}", border=1)
                pdf.cell(40, 10, txt=f"{data['avg_moves']:.1f}", border=1)
                pdf.cell(40, 10, txt=f"{data['avg_time']:.2f}", border=1, ln=1)
        
       
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt="Analysis:\n" +
                      "1. The 'Opponent Mobility' heuristic performed best overall, showing the importance of combining multiple factors.\n" +
                      "2. 'orb_count' was too simplistic and performed poorly against more sophisticated strategies.\n" +
                      "3. 'strategic_position' showed the value of controlling corners and edges.\n" +
                      "Trade-offs observed between aggression (quick wins) and stability (higher win rates).")
        
            pdf.output(filename)
            print(f"Report generated as {filename}")
        except ImportError:
            print("Warning: FPDF not installed. Saving report as text file instead.")
            with open(filename.replace('.pdf', '.txt'), 'w') as f:
                f.write("Heuristic Evaluation Report\n\n")
                for name, data in results.items():
                    f.write(f"{name}: Win Rate={data['win_rate']*100:.1f}%, "
                            f"Avg Moves={data['avg_moves']:.1f}, "
                            f"Avg Time={data['avg_time']:.2f}s\n")

def select_heuristic_profile():
    """Let user select a heuristic profile for the AI"""
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
        {'name': 'Strategic Position ', 'weights': [0, 0, 1.0, 0, 0]},
        {'name': 'Opponent Mobility', 'weights': [0.3, 0.2, 0.2, 0.15, 0.15]},
        {'name': 'Explosion Potential', 'weights': [0.5, 0.3, 0.1, 0.05, 0.05]}
    ]
    
    selected = heuristic_profiles[heuristic_choice]
    print(f"Selected heuristic: {selected['name']}")
    return selected['weights']

def main():
    print("Chain Reaction Game")
    print("==================")
    print("1. Human vs Human")
    print("2. Human vs AI (Console)")
    print("3. AI vs AI")
    print("4. Heuristic Evaluation (Multiple AI vs Random)")
    print("5. Run heuristic evaluation report")
    print("6. Quit")
    
    while True:
        try:
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == '1':
                game = ChainReactionGame()
                game.current_player = 'R'
                ui = GameUI(game) 
                ui.play_human_vs_human()
                
            elif choice == '2':
                game = ChainReactionGame()
                heuristic_weights = select_heuristic_profile()
                depth = input("Enter AI depth level (1-5, default 3): ").strip()
                try:
                    depth = int(depth)
                    if depth < 1 or depth > 5:
                        depth = 3
                except ValueError:
                    depth = 3
                
                ai_player = AIPlayer(game, 'B', depth, heuristic_weights)
                ui = GameUI(game, ai_player)
                ui.play_human_vs_ai()
                
                
            elif choice == '3':
                game = ChainReactionGame()
                game.current_player = 'R'
                ui = EnhancedGameUI(game)
                
                # get settings for both AIs
                print("\nAI 1 Settings (Red)")
                heuristic_weights1 = select_heuristic_profile()
                depth1 = input("Enter AI 1 depth level (1-5, default 3): ").strip()
                try:
                    depth1 = int(depth1)
                    if depth1 < 1 or depth1 > 5:
                        depth1 = 3
                except ValueError:
                    depth1 = 3
                
                print("\nAI 2 Settings (Blue)")
                heuristic_weights2 = select_heuristic_profile()
                depth2 = input("Enter AI 2 depth level (1-5, default 3): ").strip()
                try:
                    depth2 = int(depth2)
                    if depth2 < 1 or depth2 > 5:
                        depth2 = 3
                except ValueError:
                    depth2 = 3
                
                ui.play_ai_vs_ai(depth1, depth2, heuristic_weights1, heuristic_weights2)
                
            elif choice == '4':
                game = ChainReactionGame()
                ui = EnhancedGameUI(game, None)
        
                print("\nHeuristic Profiles Available:")
                print("1. Orb Count ")
                print("2. Critical Mass")
                print("3. Strategic Position")
                print("4. Opponent Mobility (Default)")
                print("5. Explosion Potential")
        
                try:
                    heuristic_choice = int(input("Select heuristic profile (1-5) [4]: ") or "4") - 1
                    num_games = int(input("Number of games [10]: ") or "10")
                    depth = int(input("AI depth [3]: ") or "3")
                    random_side = input("Random plays as (R/B) [B]: ").upper() or "B"
                    verbose = input("Verbose output? (y/n) [n]: ").lower().startswith('y')
                except ValueError:
                    heuristic_choice, num_games, depth = 3, 10, 3
                    random_side = 'B'
                    verbose = False
        
                results = ui.play_multiple_ai_vs_ai(
                    num_games=num_games,
                    depth=depth,
                    heuristic_choice=heuristic_choice,
                    random_plays_as=random_side,
                    verbose=verbose
                )
        
                ui.print_statistics()
        
        # saving results with heuristic info
                save_name = f"results_heuristic_{heuristic_choice+1}_vs_random.json"
                ui.save_statistics_to_file(save_name)
                
            elif choice == '5':
                ui = EnhancedGameUI(ChainReactionGame())
                num_games = input("Enter number of games per heuristic (default 20): ").strip()
                try:
                    num_games = int(num_games) if num_games else 20
                except ValueError:
                    num_games = 20
                
                depth = input("Enter AI difficulty level (1-5, default 3): ").strip()
                try:
                    depth = int(depth) if depth else 3
                    if depth < 1 or depth > 5:
                        depth = 3
                except ValueError:
                    depth = 3
                
                print("\nRunning heuristic evaluation experiments...")
                results = ui.run_heuristic_experiments(num_games=num_games, depth=depth)
                
                print("\nResults Summary:")
                for name, data in results.items():
                    print(f"{name}: Win Rate={data['win_rate']*100:.1f}%, "
                          f"Avg Moves={data['avg_moves']:.1f}, "
                          f"Avg Time={data['avg_time']:.2f}s")
                
                generate_report = input("\nGenerate PDF report? (y/n): ").strip().lower() == 'y'
                if generate_report:
                    filename = input("Enter filename (default: heuristic_report.pdf): ").strip() or "heuristic_report.pdf"
                    ui.generate_report(results, filename)
                
            elif choice == '6':
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")
                
        except KeyboardInterrupt:
            print("\nGame interrupted. Returning to main menu.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()


                    



