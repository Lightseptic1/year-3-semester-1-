#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
using namespace std;

struct Node {
    string key;
    int h;       
    Node* left;
    Node* right;
    Node(const string& k): key(k), h(1), left(nullptr), right(nullptr) {}
};

int height(Node* n) {
    if (n == nullptr) return 0;
    return n->h;
}

int balance(Node* n) {
    if (n == nullptr) return 0;
    return height(n->left) - height(n->right);
}

void fix_height(Node* n) {
    int hl = height(n->left);
    int hr = height(n->right);
    n->h = (hl > hr ? hl : hr) + 1;
}
// rotate right around y
Node* rotate_right(Node* y) {
    Node* x = y->left;
    Node* T2 = x->right;

    // do rotation
    x->right = y;
    y->left = T2;

    // fix heights
    fix_height(y);
    fix_height(x);

    // new root of this part
    return x;
}
// rotate left around x
Node* rotate_left(Node* x) {
    Node* y = x->right;
    Node* T2 = y->left;

    // do rotation
    y->left = x;
    x->right = T2;

    // fix heights
    fix_height(x);
    fix_height(y);

    // new root of this part
    return y;
}
// rebalance one node after insert or delete below it
Node* rebalance(Node* n) {
    fix_height(n);
    int b = balance(n);

    // left heavy
    if (b > 1) {
        // left right case
        if (balance(n->left) < 0)
            n->left = rotate_left(n->left);
        // left left case
        return rotate_right(n);
    }

    // right heavy
    if (b < -1) {
        // right left case
        if (balance(n->right) > 0)
            n->right = rotate_right(n->right);
        // right right case
        return rotate_left(n);
    }

    // already fine
    return n;
}

Node* insert_node(Node* n, const string& key) {
    // normal BST insert
    if (n == nullptr) return new Node(key);

    if (key < n->key) n->left  = insert_node(n->left, key);
    else if (key > n->key) n->right = insert_node(n->right, key);
    else return n; // ignore duplicates

    // fix and rebalance
    return rebalance(n);
}

void clear_all(Node* n) {
    if (!n) return;
    clear_all(n->left);
    clear_all(n->right);
    delete n;
}
// lowercase helper
static inline void to_lower_inplace(string& s) {
    transform(s.begin(), s.end(), s.begin(),
              [](unsigned char c){ return (char)tolower(c); });
}

bool has_prefix(const string& word, const string& prefix) {
    if (prefix.size() > word.size()) return false;
    for (size_t i = 0; i < prefix.size(); ++i) {
        if (word[i] != prefix[i]) return false;
    }
    return true;
}

void autocomplete_dfs(Node* n, const string& incom, bool& printed) {
    if (!n) return;

    // visit left subtree
    autocomplete_dfs(n->left, incom, printed);

    // check this node
    if (has_prefix(n->key, incom)) {
        cout << n->key << '\n';
        printed = true;
    }

    // visit right subtree
    autocomplete_dfs(n->right, incom, printed);
}

void autocomplete(Node* root, const string& incom) {
    if (incom.empty()) {
        cout << "(no matches)\n";
        return;
    }

    bool printed = false;
    autocomplete_dfs(root, incom, printed);

    if (!printed) {
        cout << "(no matches)\n";
    }
}

void challenge(Node* root, const string& unc) {
    if (unc.empty()) { cout << "(no matches)\n"; return; }
    const string lo = unc;
    const string hi = unc + "{"; // '{' is right after 'z' in ASCII

    struct Helper {
        static void moveto(Node* n, const string& lo, const string& hi, bool& any) {
            if (!n) return;

            // Only explore left if keys there can be >= lo
            if (n->key >= lo) moveto(n->left, lo, hi, any);

            // If current key is within [lo, hi), it matches the prefix
            if (n->key >= lo && n->key < hi) {
                cout << n->key << '\n';
                any = true;
            }

            // Only explore right if keys there can still be < hi
            if (n->key < hi) moveto(n->right, lo, hi, any);
        }
    };

    bool any = false;
    Helper::moveto(root, lo, hi, any);
    if (!any) cout << "(no matches)\n";
}

int main() {
    Node* root = nullptr;
    ifstream file("dictionary.txt");
    if (!file) {
        cout << "Could not open dictionary.txt\n";
        return 1;
    }
    string word;
   while (getline(file, word)) {
    if (!word.empty() && word.back() == '\r') word.pop_back(); // handles invisible formating stuff

    if (word.empty()) continue;

    to_lower_inplace(word);
    root = insert_node(root, word);
}
    file.close();
    cout << "Enter incomplete word: ";
    string incom;
    getline(cin, incom);
    to_lower_inplace(incom);
    cout << "\nAutocomplete:\n";
    autocomplete(root, incom);
    cout << "\nChallenge:\n";
    challenge(root, incom);
    clear_all(root); // del all
    return 0;
}
