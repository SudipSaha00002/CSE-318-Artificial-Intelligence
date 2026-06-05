#include <bits/stdc++.h>

using namespace std;

struct attriInstance{
    vector<string> attributes;
    string label;
};

struct Node{
    string attribute;
    string value;
    map<string, Node *> child;
    bool isLeaf = false;
    vector<attriInstance> nodeInfo; // storing instances at the
                                    // node for better majority class handling
};

class DecisionTree{
private:
    vector<attriInstance> data;
    vector<string> attributeNames;
    string criterion;
    int maxDepth;
    int nodeCount;
    int treeDepth;

    double entropy(const vector<attriInstance> &dataset){
        if (dataset.empty()){
            return 0.0;
        }
        map<string, int> count;
        for (const auto &attriInstance : dataset){
            count[attriInstance.label]++;
        }
        double entropy = 0.0;
        const double S = dataset.size();
        for (const auto& pair : count) {
            double prob = pair.second / S;
            if (prob > 0.0) {
                entropy -= prob * log2(prob);
            }
        }
        return entropy;
    }
    
    double IG(const vector<attriInstance>& dataset, int index) {
    if (dataset.empty()) {
        return 0.0;
    }

    const double base = entropy(dataset);
    const double S = dataset.size();

    // grouping instances by the value of the selected attribute
    map<string, vector<attriInstance>> groups;
    
    for (const auto& instance : dataset) {
        groups[instance.attributes[index]].push_back(instance);
    }

    // weighted entropy of all groups
    double entropySum = 0.0;
    for (const auto& [value, group] : groups) {
        const double p = group.size() / S;
        entropySum += p * entropy(group);
    }

    return base - entropySum;
}

    // information gain ratio
    double IGR(const vector<attriInstance> &dataset, int index){
        if (dataset.empty()){
            return 0.0;
        }

        map<string, int> count;
        for (const auto &instance : dataset){
            count[instance.attributes[index]]++;
        }

        double size = dataset.size();
        double iv = 0.0;
        for (const auto &pair : count){
            double p = pair.second / size;
            if (p > 0.0)
                iv -= p * log2(p);
        }
        return iv;
    }

    //  normalized weighted information Gain
    double NWIG(const vector<attriInstance> &dataset, int index){

        double ig = IG(dataset, index);
        set<string> value;
        for (const auto &instance : dataset){
            value.insert(instance.attributes[index]);
        }
        double k = value.size();
        double S = dataset.size();
        if (k <= 1)
            return 0.0;
        double nwig = ig / log2(k+1);
        double penalty = 1.0 - ((k+1) / S);
        if (penalty < 0.0)
            penalty = 0.0;
        return nwig * penalty;
    }

    // selecting the best attribute based on the criterion
    int selectBestAttr(const vector<attriInstance>& dataset, const set<int>& attributes) {
    if (attributes.empty()) 
        return -1;
    if (attributes.size() == 1)
        return *attributes.begin();

    int bestA = -1;
    double bestS = -1.0;

    for (int attr : attributes) {
        double result = 0.0;
        
        if (criterion == "IG") {
            result = IG(dataset, attr);
        } 
        else if (criterion == "IGR") {
            double iv = IGR(dataset, attr);
            if (iv > 0.0) {
                result = IG(dataset, attr) / iv;
            } else {
                result = 0.0;
            }
        } 
        else {
            result = NWIG(dataset, attr);
        }

        if (result > bestS) {
            bestS = result;
            bestA = attr;
        }
        else if (result == bestS && attr < bestA) {
            bestA = attr;
        }
    }

    return bestA;
}

    string majorityfind(const vector<attriInstance> &dataset){
        if (dataset.empty()){
            return "unknown";
        }   
        map<string, int> count;
        for (const auto &attriInstance : dataset){
            count[attriInstance.label]++;
        }
        string majority;
        int maxCount = 0;
        for (const auto &pair : count){
            if (pair.second > maxCount)
            {
                maxCount = pair.second;
                majority = pair.first;
            }
        }
        return majority;
    }

    // constructing decision tree recursively
    Node *constructTree(const vector<attriInstance> &dataset, set<int> attributes, int depth){

        nodeCount++;
        treeDepth = max(treeDepth, depth);

        Node *node = new Node();
        node->nodeInfo = dataset;

        if (dataset.empty()){
            node->isLeaf = true;
            node->value = "unknown";
            return node;
        }
        // checking if all instances have the same label
        string firstLabel = dataset[0].label;
        bool allSame = true;
        for (const auto& instance : dataset) {
            if (instance.label != firstLabel) {
                allSame = false;
                break;
            }
        }
        if (allSame) {
            node->isLeaf = true;
            node->value = firstLabel;
            return node;
        }

    
        // checking if there are no attributes left to split on
        if (attributes.empty() || (maxDepth > 0 && depth >= maxDepth)){
            node->isLeaf = true;
            node->value = majorityfind(dataset);
            return node;
        }
        // selecting the best attribute to split on
        int attrBest = selectBestAttr(dataset, attributes);
        if (attrBest == -1){
            node->isLeaf = true;
            node->value = majorityfind(dataset);
            return node;
        }
        node->attribute = attributeNames[attrBest];
        attributes.erase(attrBest);

        // splitting dataset by attribute values
        map<string, vector<attriInstance>> subsets;
        for (const auto &attriInstance : dataset){
            subsets[attriInstance.attributes[attrBest]].push_back(attriInstance);
        }

        //constructing child nodes for each subset
        for (const auto &pair : subsets){
            Node *c = constructTree(pair.second, attributes, depth + 1);
            node->child[pair.first] = c;
        }

        return node;
    }

    // predicting class for a single iInstance
    string predict(Node* node, const attriInstance& instance) {
    while (true) {
        if (node->isLeaf) return node->value;
        
        int index = -1;
        for (size_t i = 0; i < attributeNames.size(); ++i) {
            if (attributeNames[i] == node->attribute) {
                index = i;
                break;
            }
        }
        if (index == -1) return majorityfind(node->nodeInfo);
        
        string value = instance.attributes[index];
        auto c = node->child.find(value);
        if (c == node->child.end()) {
            return majorityfind(node->nodeInfo);
        }

        node = c->second; 
    }
    }

    // for debugging
    // void printTree(Node *node, int depth = 0)
    // {
    //     for (int i = 0; i < depth; ++i)
    //         cout << "  ";
    //     if (node->isLeaf)
    //     {
    //         cout << "Leaf: " << node->value << " (attriInstances: " << node->nodeInfo.size() << ")" << endl;
    //     }
    //     else
    //     {
    //         cout << "Split on " << node->attribute << " (attriInstances: " << node->nodeInfo.size() << ")" << endl;
    //         for (const auto &pair : node->child)
    //         {
    //             for (int i = 0; i < depth; ++i)
    //                 cout << "  ";
    //             cout << "Value: " << pair.first << endl;
    //             printTree(pair.second, depth + 1);
    //         }
    //     }
    // }

public:
    DecisionTree(const string &crit, int depth)
    {
        criterion = crit;
        maxDepth = depth;
        nodeCount = 0;
        treeDepth = 0;
    }

    // normalizing whitespace and normalize to lowercase
    static string normalize(const string &str) {
   
    size_t start = str.find_first_not_of(" \t");
    if (start == string::npos) return ""; 
    
   
    size_t end = str.find_last_not_of(" \t");
    
   
    string t = str.substr(start, end - start + 1);
    

    for (char &c : t) {
        c = tolower(c);
    }

    return t;
}


static vector<string> parseLine(const string &line, char delimiter = ',') {
    vector<string> tokens;
    string curr;
    
    for (char c : line) {
        if (c == delimiter) {
         
            string cleaned = normalize(curr);
            if (!cleaned.empty()) {
                tokens.push_back(cleaned);
            }
            curr.clear();
        } else {
       
            curr += c;
        }
    }
    
    string clear = normalize(curr);
    if (!clear.empty()) {
        tokens.push_back(clear);
    }
    
    return tokens;
}

   
    bool isNumeric(const string &s) {
        if (s.empty()) 
            return false;
        size_t i = 0;
        if (s[0] == '+' || s[0] == '-') {
            i++;
        }
        bool decimalPointFound = false;
        for (; i < s.size(); ++i) {
            if (isdigit(s[i])) continue;
        else if (s[i] == '.' && !decimalPointFound) decimalPointFound = true;
        else return false;
        }
        return true;
    }
void IrisDataFile()
{
    for (auto &attriInstance : data)
    {
        for (int i = 0; i < 4; ++i)
        {
            string &val = attriInstance.attributes[i];
            if (isNumeric(val))
            {
                float value = stof(val);
                if (value < 3.0)
                    val = "low";
                else if (value < 5.0)
                    val = "medium";
                else
                    val = "high";
            }
            else
            {
                val = "unknown";
            }
        }
    }
}

    void AdultDataFile()
{
    for (auto &attriInstance : data)
    {
        string &str1 = attriInstance.attributes[0];
        if (isNumeric(str1))
        {
            float val = stof(str1);
            if (val < 25)
                str1 = "low";
            else if (val < 50)
                str1 = "medium";
            else
                str1 = "high";
        }
        else
        {
            str1 = "unknown";
        }

        string &str2 = attriInstance.attributes[2];
        if (isNumeric(str2))
        {
            float val = stof(str2);
            if (val < 100000)
                str2 = "low";
            else if (val < 200000)
                str2 = "medium";
            else
                str2 = "high";
        }
        else
        {
            str2 = "unknown";
        }
        string &str3 = attriInstance.attributes[4];
        if (isNumeric(str3))
        {
            float val = stof(str3);
            if (val < 9)
                str3 = "low";
            else if (val < 13)
                str3 = "medium";
            else
                str3 = "high";
        }
        else
        {
            str3 = "unknown";
        }

 
        string &str4 = attriInstance.attributes[10];
        if (isNumeric(str4))
        {
            float val = stof(str4);
            if (val == 0)
                str4 = "low";
            else if (val < 5000)
                str4 = "medium";
            else
                str4 = "high";
        }
        else
        {
            str4 = "unknown";
        }

        string &str5 = attriInstance.attributes[11];
        if (isNumeric(str5))
        {
            float val = stof(str5);
            if (val == 0)
                str5 = "low";
            else if (val < 2000)
                str5 = "medium";
            else
                str5 = "high";
        }
        else
        {
            str5 = "unknown";
        }

        string &str6 = attriInstance.attributes[12];
        if (isNumeric(str6))
        {
            float val = stof(str6);
            if (val < 30)
                str6 = "low";
            else if (val <= 40)
                str6 = "medium";
            else
                str6 = "high";
        }
        else
        {
            str6 = "unknown";
        }
    }
}


    bool loadData(const string &filename, bool isIris)
    {
        ifstream file(filename);
        data.clear();
        attributeNames.clear();
        string line;

        if (isIris)
        {
            if (getline(file, line))
            {
                vector<string> headers = parseLine(line);
                size_t index;
                if (headers[0] == "Id")
                    index = 1;
                else
                    index = 0;
                for (size_t i = index; i < headers.size() - 1; ++i)
                    attributeNames.push_back(headers[i]);
            }
        }
        else
        {
            attributeNames = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n"};
        }

        while (getline(file, line))
        {
            if (line.empty())
                continue;
            vector<string> tokens = parseLine(line, ',');
            if (tokens.size() < attributeNames.size() + 1)
                continue;
            attriInstance i;
            i.attributes = vector<string>(tokens.begin(), tokens.begin() + attributeNames.size());
            i.label = tokens[attributeNames.size()];
            data.push_back(i);
        }
        file.close();

        if (data.empty())
        {
            cerr << "No valid data loaded from " << filename << endl;
            return false;
        }

        if (isIris)
            IrisDataFile();
        else
            AdultDataFile();

        return true;
    }

    // spliting into 80/20 for training and testing

void evaluate(const string &datasetName, int runs = 20) {
    cout << "\nEvaluating " << datasetName << " (" << runs << " runs)\n";

    double totalAccuracy = 0;
    int totalNodes = 0;
    int totalDepth = 0;

   
    srand(time(NULL)); 

    for (int run = 1; run <= runs; run++) {
      
        for (size_t i = data.size()-1; i > 0; i--) {
            int j = rand() % (i+1); 
            swap(data[i], data[j]);
        }


        size_t trainSize = data.size() * 0.8;
        vector<attriInstance> train(data.begin(), data.begin() + trainSize);
        vector<attriInstance> test(data.begin() + trainSize, data.end());


        nodeCount = 0;
        treeDepth = 0;
        set<int> attributes;
        for (size_t i = 0; i < attributeNames.size(); i++) {
            attributes.insert(i);
        }
        Node* root = constructTree(train, attributes, 0);

      
        int correct = 0;
        for (const auto& instance : test) {
            if (predict(root, instance) == normalize(instance.label)) {
                correct++;
            }
        }
        double accuracy = (double)correct / (double)test.size();

   
        totalAccuracy += accuracy;
        totalNodes += nodeCount;
        totalDepth += treeDepth;

        cout << "Run " << run << ": " 
             << fixed << setprecision(1) << (accuracy*100) << "% accuracy, "
             << nodeCount << " nodes, " << treeDepth << " depth\n";

        delete root;
    }

    
     cout << "Max Depth: ";
    if (maxDepth == 0) {
        cout << "No pruning";
    } else {
        cout << maxDepth;
    }
    cout << endl;
        // cout << "Max Depth: " << (maxDepth == 0 ? "No pruning" : to_string(maxDepth)) << endl;
        cout << "Average Accuracy: " << fixed << setprecision(4) <<  setprecision(2) << (totalAccuracy/runs*100) << "%" << endl;
        cout << "Average Nodes: " << fixed << setprecision(1) << (totalNodes/runs) << endl;
        cout << "Average Depth: " << fixed << setprecision(1) << (totalDepth/runs) << endl;
    }

};
int main(int argc, char *argv[])
{

    string criterion = argv[1];
    int maxDepth = stoi(argv[2]); 
    
   

    cout << "Decision Tree Learning Algorithm" << endl;
    cout << "Criterion: " << criterion << ", Max Depth: " << maxDepth << endl;

    DecisionTree iris(criterion, maxDepth);
    if (iris.loadData("Iris.csv", true))
    {
        cout << "Evaluating Iris dataset..." << endl;
        iris.evaluate("Iris");
    }
    else
    {
        cerr << "Failed to load Iris.csv" << endl;
    }

    DecisionTree adult(criterion, maxDepth);
    if (adult.loadData("adult.data", false))
    {
        cout << "Evaluating Adult dataset..." << endl;
        adult.evaluate("Adult");
    }
    else
    {
        cerr << "Failed to load adult.data " << endl;
    }

    return 0;
}