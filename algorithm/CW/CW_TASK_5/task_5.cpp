#include <iostream>
#include <vector>
using namespace std;
bool isSorted(const vector<char>& disks) {
    bool seenD = false;
    for (char c : disks) {
        if (c == 'D') {
            seenD = true;
        } else if (c == 'L' && seenD) {
            return false;
        }
    }
    return true;
}
long long solveDisks(vector<char>& disks) {
    long long moves = 0;
    int size = (int)disks.size();
    while (!isSorted(disks)) {
        for (int i = 0; i < size - 1; ++i) {
            if (disks[i] == 'D' && disks[i + 1] == 'L') {
                swap(disks[i], disks[i + 1]);
                ++moves;
            }
        }
    }
    return moves;
}
int main() {
    int n;
    cout << "Enter n (number of dark and light disks each): ";
    cin >> n;

    if (n <= 0) {
        cout << "n must be positive." << endl;
        return 0;
    }
    vector<char> disks(2 * n);
    for (int i = 0; i < 2 * n; ++i) {
        if (i % 2 == 0) {
            disks[i] = 'D';
        } else {
            disks[i] = 'L';
        }
    }
    cout << "Initial configuration: ";
    for (char c : disks) cout << c << ' ';
    cout << endl;
    long long moves = solveDisks(disks);
    cout << "Final configuration:   ";
    for (char c : disks){
        cout << c << ' ';
    }
    cout << "\nNumber of moves (neighbor swaps): " << moves << endl;
    return 0;
}
