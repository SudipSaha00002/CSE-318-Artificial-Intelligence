#include <bits/stdc++.h>
using namespace std;

//we check if the current board is the goal state of the puzzle
bool is_goalState(const vector<vector<int>>& tiles) {
    int n = tiles.size();
    if (tiles[n-1][n-1] != 0) {       // we check if the bottom-right corner has 0
        return false;
    }

    int comp = 1;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {   
            if (i == n-1 && j == n-1) {  // we skip the bottom-right cell which should be 0
                continue;
            }
            if (tiles[i][j] != comp) { // Compare current tile with expected value
                return false;
            }
            comp++;
        }
    }
    return true;
}

//here we try to find the blank position of the tiles
pair<int, int> find_blank(const vector<vector<int>>& tiles) {
    int n = tiles.size();
    int total = n * n;

    for (int idx = 0; idx < total; idx++) {
        int row = idx / n;
        int col = idx % n;
        
        if (tiles[row][col] == 0) {
            return {row, col};
        }
    }
    // returns -1, -1 if we can't find the blank tile
    return {-1, -1};
}

vector<vector<vector<int>>> neighbors(const vector<vector<int>>& tiles) {
    const int n = tiles.size();
    vector<vector<vector<int>>> result;
    result.reserve(4); // here we pre-allocate the  potential 4 neighbors
    
    pair<int, int> blank;             // finding the position of the blank title
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (tiles[i][j] == 0) {
                blank = {i, j};
                break;
            }
        }
    }
    
    // we define the possible moves (up, down, left, right)
    const vector<pair<int, int>> directions = {
        {-1, 0}, {1, 0},  {0, -1}, {0, 1}   
    };

    for (const auto& direction : directions) {
        int row = blank.first + direction.first;
        int col = blank.second + direction.second;
        
        if (row >= 0 && row < n && col >= 0 && col < n) {
            vector<vector<int>> new_state = tiles;
            swap(new_state[blank.first][blank.second], new_state[row][col]);// here we swap the blank with the adjacent tile
            result.push_back(new_state);
        }
    }
    return result;
}


string serialize(const vector<vector<int>>& tiles) {
    ostringstream oss;
    for (const auto& row : tiles) {
        for (int val : row) {
            oss << val << ',';
        }
    }
    return oss.str();
}




int manhattan_distance(const vector<vector<int>>& tiles) {
    int dist = 0, n = tiles.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int val = tiles[i][j];
            if (val == 0) continue;
            int x = (val - 1) / n, y = (val - 1) % n;
            dist += abs(x - i) + abs(y - j);
        }
    }
    return dist;
}


int hamming_distance(const vector<vector<int>>& tiles) {
    int dist = 0, val = 1, n = tiles.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++, val++) {
            if (tiles[i][j] && tiles[i][j] != val) {
                dist++;
            }
        }
    }
    return dist;
}
int euclidean_distance(const vector<vector<int>>& tiles) {
    double dist = 0.0;
    int n = tiles.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            int val = tiles[i][j];
            if (val == 0) continue;
            int goal_x = (val - 1) / n;
            int goal_y = (val - 1) % n;
            dist += sqrt(pow(i - goal_x, 2) + pow(j - goal_y, 2));
        }
    }
    return round(dist);
}

int linear_conflict(const vector<vector<int>>& tiles) {
    int n = tiles.size();
    int conflicts = 0;
    
    // here we calculate the row conflicts 
    for (int row = 0; row < n; row++) {
        for (int i = 0; i < n - 1; i++) {
            int val1 = tiles[row][i];
            if (val1 == 0 || (val1 - 1) / n != row)
                continue;  // we check if tile belongs to this row in goal state
            
            for (int j = i + 1; j < n; j++) {
                int val2 = tiles[row][j];
                if (val2 == 0 || (val2 - 1) / n != row) 
                    continue;  // we check if second tile belongs to this row in goal state
                
                if ((val1 - 1) % n > (val2 - 1) % n) {   // we check if tiles are in conflict (natural order is reversed)
                    conflicts += 2;
                }
            }
        }
    }
    
    //we calculate the column conflicts
    for (int col = 0; col < n; col++) {
        for (int i = 0; i < n - 1; i++) {
            int val1 = tiles[i][col];
            if (val1 == 0 || (val1 - 1) % n != col)  // we check if tile belongs to this column in goal state
                continue;
            for (int j = i + 1; j < n; j++) {
                int val2 = tiles[j][col];
                if (val2 == 0 || (val2 - 1) % n != col) // we check if second tile belongs to this column in goal state
                    continue;
                if ((val1 - 1) / n > (val2 - 1) / n) { // we check if tiles are in conflict (natural order is reversed)
                    conflicts += 2;
                }
            }
        }
    }
    return manhattan_distance(tiles) + conflicts;
}

bool is_solvable(const vector<vector<int>>& tiles) {
    int n = tiles.size();
    int inversions = 0;
    int blank_row = -1;
    vector<int> flat;
    flat.reserve(n * n - 1); 

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int val = tiles[i][j];
            if (val == 0) {
                blank_row = i;
            } else {
                for (int k = 0; k < flat.size(); ++k) {
                    if (flat[k] > val) ++inversions;
                }
                flat.push_back(val);
            }
        }
    }

    if (n % 2 == 1)
        return inversions % 2 == 0;
    
    int row_from_bottom = n - blank_row;
    return (row_from_bottom + inversions) % 2 == 1;
}



struct Node {
    vector<vector<int>> tiles;
    int g, h;
    vector<vector<vector<int>>> path;
    int f() const { return g + h; }
    bool operator>(const Node& other) const {
        return f() > other.f();
    }
};

void A_Star_Search(const vector<vector<int>>& start_tiles, int choice, ofstream& out_file) {
    if (!is_solvable(start_tiles)) {
        out_file << "Unsolvable puzzle\n";
        return;
    }

    int nodes_expanded = 0;
    int nodes_explored = 1;
    function<int(const vector<vector<int>>&)> heuristic;
    switch (choice) {
        case 1: heuristic = manhattan_distance; 
            break;
        case 2: heuristic = hamming_distance; 
            break;
        case 3: heuristic = euclidean_distance; 
            break;
        case 4: heuristic = linear_conflict; 
            break;
        
    }

    // here we done the min heap priority
    priority_queue<Node, vector<Node>, greater<Node>> pq;  // Min-heap priority queue based on f = g + h
    unordered_set<string> visited;

    int h0 = heuristic(start_tiles);
    pq.push({start_tiles, 0, h0, {start_tiles}});

    while (!pq.empty()) {
        Node curr = pq.top(); pq.pop();
        string curr_id = serialize(curr.tiles);

        if (visited.count(curr_id)) continue;
        visited.insert(curr_id);
        nodes_expanded++;

        if (is_goalState(curr.tiles)) {
            out_file << "Minimum number of moves = " << curr.g << "\n";
            for (const auto& board : curr.path) {
                for (const auto& row : board) {
                    for (int val : row) out_file << val << " ";
                    out_file << "\n";
                }
                out_file << "\n";
            }
            out_file << "Nodes explored: " << nodes_explored << "\n";
            out_file << "Nodes expanded: " << nodes_expanded-1 << "\n";
            return;
        }

        for (const auto& neighbor : neighbors(curr.tiles)) {
            string id = serialize(neighbor);
            if (!visited.count(id)) {
                vector<vector<vector<int>>> new_path = curr.path;
                new_path.push_back(neighbor);
                int h_val = heuristic(neighbor);
                pq.push({neighbor, curr.g + 1, h_val, move(new_path)});
                nodes_explored++;
            }
        }
    }

    out_file << "No solution found.\n";
}


int main() {
    ifstream in_file("in.txt");
    ofstream out_file("out.txt");
    
    int n;
    in_file >> n;
    
    vector<vector<int>> initial(n, vector<int>(n));
    for (auto &row : initial)
        for (int &x : row)
            in_file >> x;

    int choice;
    in_file >> choice;

    A_Star_Search(initial, choice, out_file);
    
    in_file.close();
    out_file.close();
    
    return 0;
}