#include <iostream>
#include <vector>
using namespace std;

void quick_sort(vector<int>& arr, int low, int high) {
    if (low < high) {
        int pivot = arr[high];
        int i = low - 1;

        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                swap(arr[i], arr[j]);
            }
        }
        swap(arr[i + 1], arr[high]);
        int pi = i + 1;
        quick_sort(arr, low, pi - 1);
        quick_sort(arr, pi + 1, high);
    }
}
int main() {
    vector<int> nums = {5, 3, 8, 4, 2};
    vector<int> v_q_sort = {5, 3, 8, 4, 2};
    quick_sort(v_q_sort, 0, v_q_sort.size() - 1);

    cout << "Array started with: ";
    for (int x : nums) {
        cout << x << " ";
    }
    cout << "\nBubble sorted: ";
     for (int x : v_q_sort) {
        cout << x << " ";
    }    
    return 0;
}
