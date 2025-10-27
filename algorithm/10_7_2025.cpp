#include <iostream>
using namespace std;
int Binary_Search(int arr[], int low, int high, int t){
    if(high>=low){
        int mid = low + (high - low) / 2;
    if(arr[mid] == t){
        return mid;
    }
    if(arr[mid] > t){
        return Binary_Search(arr, low, mid - 1, t);
    }
    else{
        return Binary_Search(arr, mid + 1, high, t);
    }

}
return -1;
}
int main(){
    int arr[] = {2, 4, 6, 19, 20, 40, 55, 93};
    int x = 6;
    int n = sizeof(arr) / sizeof(arr[0]);
    int result = Binary_Search(arr, 0, n - 1, x);
    cout << result;
}