#include <iostream>
#include <vector>
using namespace std;
void s_sort(vector <int> &arr){
    int n = arr.size();
    int temp;
    for (int x = 0 ; x < n -1 ; x++){
        int min_index = x;
        for(int y = x+1; y < n; y++){
            if (arr[y] < arr[min_index]) {
                min_index = y;  
            }
        }
        temp = arr[x];
        arr[x] = arr[min_index];
        arr[min_index] = temp;
        //swap can be used here
    }
}
int main(){
    vector<int> nums = {5, 3, 8, 4, 2};
    vector<int> v_s_sort = nums;
    cout << "Array started with: ";
    for (int x : nums) {
        cout << x << " ";
    }
    cout << "\nSelection sorted: ";
    s_sort(v_s_sort);
     for (int x : v_s_sort) {
        cout << x << " ";
    }  
}