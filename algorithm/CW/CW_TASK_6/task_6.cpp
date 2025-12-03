#include <iostream>
#include <vector>
#include <string>
using namespace std;
int n;          
int fakeIndex;    
int fakeDelta;  
const int BASE_WEIGHT = 10; 
int weighingCount = 0;  
int coinWeight(int idx) {
    int w = BASE_WEIGHT;
    if (idx == fakeIndex) {
        w += fakeDelta;
    }
    return w;
}
int weigh(const vector<int>& leftIndices, const vector<int>& rightIndices) {
    ++weighingCount;

    int leftSum = 0;
    for (int idx : leftIndices) {
        leftSum += coinWeight(idx);
    }

    int rightSum = 0;
    for (int idx : rightIndices) {
        rightSum += coinWeight(idx);
    }

    if (leftSum < rightSum) return -1;
    if (leftSum > rightSum) return +1;
    return 0;
}
string solve_for_three() {
    int r1 = weigh({0}, {1});

    if (r1 == 0) {
        int r2 = weigh({2}, {0});
        if (r2 > 0) {
            return "Fake coin is HEAVIER (used O(1) method for n = 3).";
        } else if (r2 < 0) {
            return "Fake coin is LIGHTER (used O(1) method for n = 3).";
        } else {
            return "Inconsistent result in n = 3 branch.";
        }
    } else {
        int r2 = weigh({0}, {2}); 

        if (r1 > 0) {
            if (r2 > 0) {
                return "Fake coin is HEAVIER (used O(1) method for n = 3).";
            } else if (r2 == 0) {
                return "Fake coin is LIGHTER (used O(1) method for n = 3).";
            } else {
                return "Inconsistent result in n = 3 branch.";
            }
        } else {
            if (r2 < 0) {
                return "Fake coin is LIGHTER (used O(1) method for n = 3).";
            } else if (r2 == 0) {
                return "Fake coin is HEAVIER (used O(1) method for n = 3).";
            } else {
                return "Inconsistent result in n = 3 branch.";
            }
        }
    }
}
string solve_general() {
    if (n < 3) {
        return "Need at least 3 coins.";
    }
    int r1 = weigh({0}, {1});
    if (r1 != 0) {
        if (n < 3) {
            return "Not enough coins for this method.";
        }
        int r2 = weigh({0}, {2});
        if (r1 > 0) {
            if (r2 > 0) {
                return "Fake coin is HEAVIER (used general method for n > 3).";
            } else if (r2 == 0) {
                return "Fake coin is LIGHTER (used general method for n > 3).";
            } else {
                return "Inconsistent result in general branch.";
            }
        } else {
            if (r2 < 0) {
                return "Fake coin is LIGHTER (used general method for n > 3).";
            } else if (r2 == 0) {
                return "Fake coin is HEAVIER (used general method for n > 3).";
            } else {
                return "Inconsistent result in general branch.";
            }
        }
    } else {
        for (int i = 2; i < n; ++i) {
            int r = weigh({i}, {0});
            if (r > 0) {
                return "Fake coin is HEAVIER (used general method for n > 3).";
            } else if (r < 0) {
                return "Fake coin is LIGHTER (used general method for n > 3).";
            }
        }
        return "No fake coin found, setup inconsistent.";
    }
}
int main() {
    cout << "Enter number of coins (n > 2): ";
    cin >> n;
    if (n <= 2) {
        cout << "n must be greater than 2.\n";
        return 0;
    }
    cout << "Enter which coin is fake (1 to " << n << "): ";
    int userIndex;
    cin >> userIndex;
    if (userIndex < 1 || userIndex > n) {
        cout << "Invalid coin index.\n";
        return 0;
    }
    fakeIndex = userIndex - 1; 
    cout << "Enter 1 if fake coin is heavier, 0 if fake coin is lighter: ";
    int isHeavier;
    cin >> isHeavier;
    if (isHeavier == 1) {
        fakeDelta = +1;
    } else if (isHeavier == 0) {
        fakeDelta = -1;
    } else {
        cout << "Invalid input, must be 1 or 0.\n";
        return 0;
    }
    weighingCount = 0;
    string result;
    if (n == 3) {
        result = solve_for_three(); 
    } else {
        result = solve_general();    
    }
    cout << "\nResult: " << result << "\n";
    cout << "Total number of simulated weighings: " << weighingCount << "\n";
    cout << "Ground truth: fake coin index = " << fakeIndex+1
         << " (user coin " << (fakeIndex + 1) << "), and it is actually "
         << (fakeDelta > 0 ? "HEAVIER" : "LIGHTER") << ".\n";

    return 0;
}
