/*
#include <iostream>
using namespace std;
int sum_of_digits(int num){
    if (num < 10){
        return num;
    }
    return ((num%10) + sum_of_digits(num/10));
}
int main(){
    int x = 12345;
    cout << sum_of_digits(x);
    return 0;
}
*/
/*
#include <iostream>
using namespace std;
int sum_of_digits(int num){
    int sum = 0;
    while(num > 0){
        sum += num % 10;
        num = num/10;
    }
   return(sum);
}
int main(){
    int x = 12345;
    cout << sum_of_digits(x);
    return 0;
}
*/
#include <iostream>
#include <vector>
using namespace std;
void i_sort(vector<int> &arr){
    int n = arr.size();
    for (int x = 1; x < n; x++) {
        int key = arr[x];
        int y = x - 1;
       
        while (y >= 0 && arr[y] > key) {
            arr[y + 1] = arr[y];
            y--;
        }
        arr[y + 1] = key;
    }

}

int main() {
    vector<int> nums = {5, 3, 8, 4, 2};
    vector<int> v_i_sort = nums;
    i_sort(v_i_sort);
    cout << "Array started with: ";
    for (int x : nums) {
        cout << x << " ";
    }
    cout << "\nInsertion sorted: ";
     for (int x : v_i_sort) {
        cout << x << " ";
    }
    return 0;
}
