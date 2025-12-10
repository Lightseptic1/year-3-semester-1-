#include <iostream>
#include <vector>
#include <stack>
#include <string>
#include <unordered_set>
#include <unordered_map>
#include <algorithm>
#include <random>
#include <chrono>
#include <fstream>
#include <queue>

using namespace std;

struct GameState {
    vector<vector<int>> stacks;  
    int capacity;

    bool operator==(const GameState& other) const {
        return stacks == other.stacks;
    }
};

struct StateHash {
    size_t operator()(GameState const& s) const noexcept {
        // hash all integers in all stacks
        size_t h = 0;
        for (auto& st : s.stacks) {
            for (int v : st) {
                h = h * 1315423911 ^ std::hash<int>()(v + 0x9e3779b9);
            }
            h ^= 0x12345678;
        }
        return h;
    }
};

// ---------- Strict Goal Check ----------
bool isGoal(const GameState& state) {
    unordered_map<int,int> colorOwner;

    for (int i = 0; i < (int)state.stacks.size(); i++) {
        const auto& st = state.stacks[i];
        if (st.empty()) continue;

        int color = st[0]; // bottom color

        // must be pure stack
        for (int x : st) {
            if (x != color) return false;
        }

        // color must not appear in another stack
        auto it = colorOwner.find(color);
        if (it == colorOwner.end()) {
            colorOwner[color] = i;
        } else {
            if (it->second != i) return false;
        }
    }
    return true;
}

// ---------- Heuristic: misplaced balls ----------
int heuristic_misplaced(const GameState& s) {
    int h = 0;

    for (auto& st : s.stacks) {
        if (st.empty()) continue;

        // a pure stack has no misplacements
        bool pure = true;
        int color0 = st[0];

        for (int x : st)
            if (x != color0)
                pure = false;

        if (!pure)
            h += (int)st.size();  // all balls in mixed stacks are "misplaced"
    }

    return h;
}

// ---------- Encode state for debugging (optional) ----------
string encodeState(const GameState& s) {
    string out;
    for (int i = 0; i < (int)s.stacks.size(); i++) {
        if (i) out.push_back('|');
        for (int j = 0; j < (int)s.stacks[i].size(); j++) {
            out += to_string(s.stacks[i][j]);
            if (j+1 < (int)s.stacks[i].size()) out.push_back(',');
        }
    }
    return out;
}

// ---------- A* Search ----------
struct Node {
    GameState state;
    int g; // cost so far
    int f; // g + h
};

struct Compare {
    bool operator()(const Node& a, const Node& b) const {
        return a.f > b.f;  // min-heap
    }
};

bool a_star(const GameState& start, vector<pair<int,int>>& movesOut) {
    unordered_map<GameState, pair<GameState,pair<int,int>>, StateHash> parent;
    unordered_set<GameState, StateHash> visited;

    priority_queue<Node, vector<Node>, Compare> pq;

    Node root;
    root.state = start;
    root.g = 0;
    root.f = heuristic_misplaced(start);
    pq.push(root);

    parent[start] = {start, {-1,-1}}; // parent of root is itself

    const int EXPANSION_LIMIT = 300000;

    int expansions = 0;

    while (!pq.empty()) {

        Node cur = pq.top();
        pq.pop();

        if (visited.count(cur.state)) continue;
        visited.insert(cur.state);

        // FOUND GOAL
        if (isGoal(cur.state)) {
            // reconstruct path
            vector<pair<int,int>> path;
            GameState s = cur.state;

            while (true) {
                auto par = parent[s];
                if (par.second.first == -1) break; // reached start

                path.push_back(par.second);
                s = par.first;

                if (s == start) break;
            }

            reverse(path.begin(), path.end());
            movesOut = path;
            return true;
        }

        expansions++;
        if (expansions > EXPANSION_LIMIT) {
            return false;
        }

        int n = (int)cur.state.stacks.size();

        // Generate successors
        for (int i = 0; i < n; i++) {
            auto& from = cur.state.stacks[i];
            if (from.empty()) continue;

            int ball = from.back();

            for (int j = 0; j < n; j++) {
                if (i == j) continue;

                auto& to = cur.state.stacks[j];

                if ((int)to.size() >= cur.state.capacity) continue;
                if (!to.empty() && to.back() != ball) continue;

                GameState next = cur.state;
                next.stacks[j].push_back(ball);
                next.stacks[i].pop_back();

                if (visited.count(next)) continue;

                int g2 = cur.g + 1;
                int h2 = heuristic_misplaced(next);

                Node child;
                child.state = next;
                child.g = g2;
                child.f = g2 + h2;

                pq.push(child);

                parent[next] = {cur.state, {i, j}};
            }
        }
    }

    return false;
}

// ---------- Random Puzzle Generator ----------
bool generateInitialStacks(int numColors,
                           int numStacks,
                           int capacity,
                           int numEmpty,
                           vector<vector<int>>& stacksOut)
{
    int nonEmpty = numStacks - numEmpty;
    if (nonEmpty <= 0) return false;

    int totalBalls = nonEmpty * capacity;
    vector<int> balls;
    balls.reserve(totalBalls);

    for (int i = 0; i < totalBalls; i++) {
        balls.push_back((i % numColors) + 1);
    }

    unsigned seed = chrono::high_resolution_clock::now().time_since_epoch().count();
    mt19937 rng(seed);
    shuffle(balls.begin(), balls.end(), rng);

    stacksOut.assign(numStacks, vector<int>());

    int idx = 0;
    for (int i = 0; i < nonEmpty; i++) {
        for (int j = 0; j < capacity; j++) {
            stacksOut[i].push_back(balls[idx++]);
        }
    }
    return true;
}

// ---------- MAIN ----------
int main() {

    int numColors, numStacks, capacity, numEmpty;

    cout << "Enter number of colors: ";
    cin >> numColors;

    cout << "Enter TOTAL number of stacks: ";
    cin >> numStacks;

    cout << "Enter capacity (balls per non-empty stack): ";
    cin >> capacity;

    cout << "Enter how many stacks start empty: ";
    cin >> numEmpty;

    vector<vector<int>> initStacks;

    if (!generateInitialStacks(numColors, numStacks, capacity, numEmpty, initStacks)) {
        cout << "Invalid generator parameters.\n";
        return 1;
    }

    GameState start;
    start.capacity = capacity;
    start.stacks = initStacks;

    cout << "\nRunning A* solver...\n";

    vector<pair<int,int>> moves;
    bool solved = a_star(start, moves);

    if (!solved) {
        cout << "No solution found (or state limit reached).\n";
    } else {
        cout << "Solution found in " << moves.size() << " moves.\n";
    }

    // Write to game.txt
    ofstream fout("game.txt");
    fout << numStacks << " " << capacity << "\n";

    for (int i = 0; i < numStacks; i++) {
        fout << initStacks[i].size();
        for (int x : initStacks[i]) fout << " " << x;
        fout << "\n";
    }

    if (solved) {
        for (auto& mv : moves) {
            fout << mv.first+1 << " " << mv.second+1 << "\n";
        }
    }

    fout.close();
    cout << "Saved puzzle + moves to game.txt\n";
    return 0;
}
