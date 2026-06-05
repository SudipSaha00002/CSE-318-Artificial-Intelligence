#include <bits/stdc++.h>
using namespace std;

static random_device random;
static default_random_engine generator(random());  //for geting different results

// Generate random doubles in the interval [initial, final)
// double random_real(double initial, double final) {
//     uniform_real_distribution<double> distribution(initial, final);
//     return distribution(generator);
// }

int random_int(int initial, int final) {
    uniform_int_distribution<int> distribution(initial, final);// for ensuring the equal probability in the givne range
    return distribution(generator);
}

class Graph {
    int V;
    int **matrix;
    int cut_wt;      // for X, Y
    int real_cut_wt; // for S, S_
    int *sigma_X;
    int *sigma_Y;
    double semi_alpha;
    vector<int> X, Y; // for storing two partition of vertices
    vector<int> S, S_;// for computation
public:

    Graph(int V)  {
        this->V = V;
    matrix = new int*[V];
    for (int i = 0; i < V; ++i) {
        matrix[i] = new int[V](); // value-initialized to 0
    }
    semi_alpha = 0.0;

    sigma_X = new int[V]();
    sigma_Y = new int[V]();
}

void addEdge(int x, int y, int w) {
    if (x >= 0 && x < V && y >= 0 && y < V) {
        matrix[x][y] = w;     //for undirected graph
        matrix[y][x] = w;
    } else {
        cerr << "Invalid edge: (" << x << ", " << y << ")" << endl;
    }
}

    void RCL(vector<pair<int,int>> &rcl, double meu) {
        for (int i = 0; i < V; i++) {
            for (int j = 0; j < i; j++) {
                if (matrix[i][j] >= meu) {
                    rcl.push_back(make_pair(i, j));
                }
            }
        }
    }
    

    
    int get_sigma(int v, vector<int> &T) {//Calculating the sum of the edge weights between 
        int sum = 0;                      //vertex v and all the vertices in set T
         if (v < 0 || v >= V) {
        cerr << "Invalid vertex index v = " << v << endl;
        return 0;
        }
        for (int i = 0; i < T.size(); i++) {
            sum += matrix[v][T[i]];
        }
        return sum;
    }

   void get_rcl_semi(const vector<int>& V, const int* sigma_x, const int* sigma_y, double meu, vector<int>& rcl_v) {
    for (int v : V) {
        if (v < 0) continue; //skiping invalid indices
        int max_val = max(sigma_x[v], sigma_y[v]);
        if (max_val >= meu) {
            rcl_v.emplace_back(v);
        }
    }
}

//for cut weight between x and y partition
    int cut_weight() {
    cut_wt = 0;
    for (int u : X) {
        for (int v : Y) {
            if (u >= 0 && v >= 0 && u < V && v < V) { 
                cut_wt += matrix[u][v];
            }
        }
    }
    return cut_wt;
}



int search_node(const vector<int>& T, int v) const {
    for (int node : T) {
        if (node == v) return v;
    }
    return -1;
}

void delete_node(vector<int>& T, int v) {
    auto it = find(T.begin(), T.end(), v);
    if (it != T.end()) {
        T.erase(it);
    }
}

void insert_node(vector<int> &T, int v) {
        T.push_back(v);
    }
    
int randomizestart_ycut() {
    for (int i = 0; i < V; ++i) {
        if (random_int(0, 1) == 0) {
            Y.push_back(i);
        } else {
            X.push_back(i);
        }
    }

    int result = cut_weight();
    X.clear();
    Y.clear();
    return result;
}


     int get_max_arg(vector<int> &t, int size) {
        int max = t[0];
        int argmax = 0;
        for (int i = 0; i < t.size(); i++) {
            if (t[i] > max) {
                max = t[i];
                argmax = i;
            }
        }
        return argmax;
    }
    

int greedy_maxcut(int start_x, int start_y) {
    X.push_back(start_x);
    Y.push_back(start_y);

    vector<int> V_;
    for (int i = 0; i < V; ++i) {
        if (i != start_x && i != start_y) {
            V_.push_back(i);
        }
    }

    while (!V_.empty()) {
        vector<int> g(V, INT_MIN);//It will store the how much cut weight is added for each node 

        for (int v : V_) {
            sigma_X[v] = get_sigma(v, Y);
            sigma_Y[v] = get_sigma(v, X);
            g[v] = max(sigma_X[v], sigma_Y[v]);
        }

        int vert = get_max_arg(g, V);//returns the index of the vertex with the highest value in g
        if (sigma_X[vert] > sigma_Y[vert]) {
            X.push_back(vert);
        } else {
            Y.push_back(vert);
        }

        V_.erase(remove(V_.begin(), V_.end(), vert), V_.end());

        fill(sigma_X, sigma_X + V, 0);  //reseting the sigmas for next iteration
        fill(sigma_Y, sigma_Y + V, 0);
    }

    int result = cut_weight();
    X.clear();
    Y.clear();
    return result;
}

    
    void semi_greedy_maxcut(int weight_min, int weight_max) {
        // double alpha = random_real(0, 1);
        double alpha = 0.5;
        semi_alpha = alpha;
        double meu = weight_min + alpha * (weight_max - weight_min);
        vector<pair<int, int>> rcl;
       RCL(rcl, meu);
        int random = random_int(0, rcl.size() - 1);
        pair<int, int> rand_edge = rcl[random];
        X.push_back(rand_edge.first);
        Y.push_back(rand_edge.second);
        int x = 1, y = 1;
        vector<int> V_;
        for (int i = 0; i < V; i++) {
            V_.push_back(i);
        }
        V_.erase(find(V_.begin(), V_.end(), rand_edge.first));
        V_.erase(find(V_.begin(), V_.end(), rand_edge.second));
        while (x + y != V) {
            int sigmax_min = INT_MAX, sigmax_max = INT_MIN, sigmay_min = INT_MAX, sigmay_max = INT_MIN;
            for (int v : V_) {
                sigma_X[v] = get_sigma(v, Y);
                if (sigma_X[v] < sigmax_min) {
                    sigmax_min = sigma_X[v];
                }
                if (sigma_X[v] > sigmax_max) {
                    sigmax_max = sigma_X[v];
                }
                sigma_Y[v] = get_sigma(v, X);
                if (sigma_Y[v] < sigmay_min) {
                    sigmay_min = sigma_Y[v];
                }
                if (sigma_Y[v] > sigmay_max) {
                    sigmay_max = sigma_Y[v];
                }
            }
            weight_min = min(sigmax_min, sigmay_min);
            weight_max = max(sigmax_max, sigmay_max);
            meu = weight_min + alpha * (weight_max - weight_min);
            vector<int> rcl_v;
            get_rcl_semi(V_, sigma_X, sigma_Y, meu, rcl_v);
            random = random_int(0, rcl_v.size() - 1);
            int rand_vertex = rcl_v[random];
            if (sigma_X[rand_vertex] > sigma_Y[rand_vertex]) {//greedily assign rand_vertex to the partition where it adds more to the cut
                X.push_back(rand_vertex);
                x++;
            }
            else {
                Y.push_back(rand_vertex);
                y++;
            }
            V_.erase(find(V_.begin(), V_.end(), rand_vertex));
            memset(sigma_X, 0, V);
            memset(sigma_Y, 0, V);
        }
        cut_weight();
    }



    int local_iteration = 0;
    int local_weight = 0;

    void local_search_maxcut() {
    bool change = true;
    int it = 0;

    // Track node partitions for quick lookup
    vector<bool> inX(V, false), inY(V, false);
    for (int node : X) inX[node] = true;
    for (int node : Y) inY[node] = true;

    while (change) {
        it++;
        change = false;

        for (int i = 0; i < V; i++) {
            int sigmax = get_sigma(i, Y);
            int sigmay = get_sigma(i, X);
                    //moving vertex i to the opposite partition improves the cut weight
            if (inX[i] && sigmay > sigmax) {
                // Move from X to Y
                delete_node(X, i);
                insert_node(Y, i);
                inX[i] = false;
                inY[i] = true;
                change = true;
            }
            else if (inY[i] && sigmax > sigmay) {
                // Move from Y to X
                delete_node(Y, i);
                insert_node(X, i);
                inY[i] = false;
                inX[i] = true;
                change = true;
            }
        }
    }

    cut_weight();
    local_iteration += it;
    local_weight += cut_wt;
}

    
    struct GraspResults {
        int semi_greedy_avg;
        int local_search_iterations_avg;
        int local_search_value_avg;
        int best_value;
        int iterations;
        double alpha;
    };
    


    GraspResults grasp_maxcut(int weight_min, int weight_max) {
    int best_value = INT_MIN;
    int max_iteration = 50;
    int i = 0;
    int semi_greedy_total = 0;
    local_iteration = 0;
    local_weight = 0;

    while (i < max_iteration) {
        // Performing semi-greedy maxcut and accumulate the result
        semi_greedy_maxcut(weight_min, weight_max);
        semi_greedy_total += cut_wt;
        // Performing local search maxcut for refinement
        local_search_maxcut();
        // Checking if the current solution is better than the previous best
        if (cut_wt > best_value) {
            S = X;
            S_ = Y;
            real_cut_wt = cut_wt;
            best_value = cut_wt;
        }
        X.clear();
        Y.clear();

        i++;
    }
        
        GraspResults results;
        results.semi_greedy_avg = semi_greedy_total / max_iteration;
        results.local_search_iterations_avg = local_iteration / max_iteration;
        results.local_search_value_avg = local_weight / max_iteration;
        results.best_value = best_value;
        results.iterations = max_iteration;
        results.alpha = semi_alpha;
        
        return results;
    }
};


string getGraphName(const string& filepath) {
    filesystem::path pathObj(filepath);
    return pathObj.stem().string(); // stem() returns filename without extension
}

// Struct to hold results for a single graph
struct GraphResults {
    string name;
    int vertices;
    int edges;
    int randomized_result;
    int greedy_result;
    int semi_greedy_result;
    int local_search_iterations;
    int local_search_avg_value;
    int grasp_iterations;
    int grasp_best_value;
    double alpha_value;
    int known_best;
};

GraphResults graphGenerate(const string& filepath) {
    int V, E;
    int s1;
    int s2;
    int weight;
    int  weight_max=INT_MAX;
    int weight_min=INT_MIN;
    int start_x, start_y;
    int x_min, y_min;
    
    ifstream file(filepath);
    if (!file.is_open()) {
        cerr << "Failed to open file: " << filepath << endl;
        exit(1);
    }
    
    file >> V >> E;
    
    Graph g(V);
    int edge = E; 
    
    while (E--) {
        file >> s1 >> s2 >> weight;
        s1--;
        s2--;
        if(weight>=weight_min){
            weight_min=weight;
            start_x=s1;
            start_y=s2;
        }
        if(weight<=weight_min){
            weight_min=weight;
            x_min=s1;
            y_min=s2;
        }
        
        g.addEdge(s1, s2, weight);
    }
    
    int max_iteration = 50;
    int it = 0;
    int rand_total = 0;
    while (it < max_iteration) {
        rand_total += g.randomizestart_ycut();
        it++;
    }
    int rand_result = rand_total / max_iteration;
    int greedy_result = g.greedy_maxcut(start_x, start_y);
    auto grasp_results = g.grasp_maxcut(weight_min, weight_min);
    
    file.close();

    GraphResults results;
    results.name = getGraphName(filepath);
    results.vertices = V;
    results.edges = edge;
    results.randomized_result = rand_result;
    results.greedy_result = greedy_result;
    results.semi_greedy_result = grasp_results.semi_greedy_avg;
    results.local_search_iterations = grasp_results.local_search_iterations_avg;
    results.local_search_avg_value = grasp_results.local_search_value_avg;
    results.grasp_iterations = grasp_results.iterations;
    results.grasp_best_value = grasp_results.best_value;
    results.alpha_value = grasp_results.alpha;
    results.known_best = 0;
    
    return results;
}

int main() {
    unordered_map<string, int> knownBest = {
    {"g1", 12078},
    {"g2", 12084},
    {"g3", 12077},
    // {"g4", NULL},
    // {"g5", NULL},
    // {"g6", NULL},
    // {"g7", NULL},
    // {"g8",NULL},
    // {"g9", NULL},
    // {"g10",NULL},
    // {"g11", 627},
    // {"g12", 621},
    // {"g13", 645},
    // {"g14", 3187},
    // {"g15", 3169},
    // {"g16", 3172},
    // {"g17", NULL},
    // {"g18", NULL},
    // {"g19", NULL},
    // {"g20",NULL},
    // {"g21", NULL},
    // {"g22", 14123},
    // {"g23", 14129},
    // {"g24", 14131},
    // {"g25", NULL},
    // {"g26", NULL},
    // {"g27", NULL},
    // {"g28",NULL},
    // {"g29", NULL},
    // {"g30", NULL},
    // {"g31", NULL},
    // {"g32", 1560},
    // {"g33", 1537},
    // {"g34", 1541},
    // {"g35", 8000},
    // {"g36", 7996},
    // {"g37", 8009},
    // {"g38",NULL},
    // {"g39", NULL},
    // {"g40", NULL},
    // {"g41", NULL},
    // {"g42", NULL},
    // {"g43", 7027},
    // {"g44", 7022},
    // {"g45", 7020},
    // {"g46", NULL},
    // {"g47", NULL},
    // {"g48", 6000},
    // {"g49", 6000},
    // {"g50", 5988},
    // {"g51", NULL},  
    // {"g52", NULL},
    // {"g53",NULL},
    // {"g54",NULL}
};
    
    vector<string> graphFiles = {
    "set1/g1.rud",
    "set1/g2.rud",
    "set1/g3.rud",
    // "set1/g4.rud",
    // "set1/g5.rud",
    // "set1/g6.rud",
    // "set1/g7.rud",
    // "set1/g8.rud",
    // "set1/g9.rud",
    // "set1/g10.rud",
    // "set1/g11.rud",
    // "set1/g12.rud",
    // "set1/g13.rud",
    // "set1/g14.rud",
    // "set1/g15.rud",
    // "set1/g16.rud",
    // "set1/g17.rud",
    // "set1/g18.rud",
    // "set1/g19.rud",
    // "set1/g20.rud",
    // "set1/g21.rud",
    // "set1/g22.rud",
    // "set1/g23.rud",
    // "set1/g24.rud",
    // "set1/g25.rud",
    // "set1/g26.rud",
    // "set1/g27.rud",
    // "set1/g28.rud",
    // "set1/g29.rud",
    // "set1/g30.rud",
    // "set1/g31.rud",
    // "set1/g32.rud",
    // "set1/g33.rud",
    // "set1/g34.rud",
    // "set1/g35.rud",
    // "set1/g36.rud",
    // "set1/g37.rud",
    // "set1/g38.rud",
    // "set1/g39.rud",
    // "set1/g40.rud",
    // "set1/g41.rud",
    // "set1/g42.rud",
    // "set1/g43.rud",
    // "set1/g44.rud",
    // "set1/g45.rud",
    // "set1/g46.rud",
    // "set1/g47.rud",
    // "set1/g48.rud",
    // "set1/g49.rud",
    // "set1/g50.rud",
    // "set1/g51.rud",  
    // "set1/g52.rud",
    // "set1/g53.rud",
    // "set1/g54.rud"
};
    
    ofstream csvFile("2105152.csv");
    if (!csvFile.is_open()) {
        cerr << "Failed to create output CSV file" << endl;
        return 1;
    }
 
    csvFile << fixed << setprecision(3);

    csvFile << "Name  |V| or n  |E| or m   Simple Randomized    Simple Greedy   Semi-greedy   ";
    csvFile << "Simple local iterations   Simple local Average value   ";
    csvFile << "GRASP iterations    GRASP Best value    Alpha    Known best solution" << endl;

    for (const auto& file : graphFiles) {
        GraphResults results = graphGenerate(file);
        
        if (knownBest.find(results.name) != knownBest.end()) {
            results.known_best = knownBest[results.name];
        }

        csvFile << left << setw(8) << results.name;
        csvFile << setw(10) << results.vertices;
        csvFile << setw(11) << results.edges ;
        csvFile << setw(21) << results.randomized_result ;
        csvFile << setw(16) << results.greedy_result ;
        csvFile << setw(21) << results.semi_greedy_result ;
        csvFile << setw(21) << results.local_search_iterations ;
        csvFile << setw(28) << results.local_search_avg_value ;
        csvFile << setw(21) << results.grasp_iterations ;
        csvFile << setw(16) << results.grasp_best_value ;
        csvFile << setw(13) << results.alpha_value;
        csvFile << setw(21) << results.known_best << endl;
    }
    
    csvFile.close();
    
    cout << "Results have been written to 2105152.csv" << endl;
    
    return 0;
}