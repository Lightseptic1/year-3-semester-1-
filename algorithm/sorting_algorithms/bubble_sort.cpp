#include <iostream>
#include <vector>
using namespace std;
void b_sort(vector<int> &arr) {
    int n = arr.size();
    for (int x = 0; x < n - 1; x++) {
        for (int y = 0; y < n - x - 1; y++) {
            if (arr[y] > arr[y + 1]) {
                swap(arr[y], arr[y + 1]);
            }
        }
    }
}
int main() {
    vector<int> nums = {5, 3, 8, 4, 2};
    vector<int> v_b_sort = nums;
    b_sort(v_b_sort);
    cout << "Array started with: ";
    for (int x : nums) {
        cout << x << " ";
    }
    cout << "\nBubble sorted: ";
     for (int x : v_b_sort) {
        cout << x << " ";
    }    
    return 0;
}
