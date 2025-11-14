#include <iostream>
#include <vector>
#include <random>
using namespace std;
int bubble_sort_count(vector <int> arr){
int n = arr.size();
int count = 0;
for(int x = 0; x < n-1; x++){
    for(int y = 0; y < n - x - 1; y++){
        if(arr[y] > arr[y+1]){
            swap(arr[y], arr[y+1]);            
        }
        count++;
    }
}
return count;
}
int selection_sort_count(vector <int> arr){
   int n = arr.size();
   int count = 0;
    for (int x = 0 ; x < n -1 ; x++){
        int min_index = x;
        for(int y = x+1; y < n; y++){
            if (arr[y] < arr[min_index]) {
                min_index = y;  
            }
            count++;
        }
     swap(arr[x], arr[min_index]);
    }
    return count;

}
int insertion_sort_count(vector <int> arr){
    int n = arr.size();
    int count = 0;
    for (int x = 1; x < n; x++) {
        int key = arr[x];
        int y = x - 1;
       
        while (y >= 0 && arr[y] > key) {
            count++;
            arr[y + 1] = arr[y];
            y--;
        }
        arr[y + 1] = key;
    }
return count;
}
vector <int> array_gen(int n){
    vector <int> arr;
    for(int x = 0; x < n; x++){
        arr.push_back(rand() % 101);
    }
    return arr;
}

int main(){
    int b_total = 0, s_total = 0, i_total = 0;
    for(int x = 0; x <= 30; x++){
    vector <int> generated = array_gen(x);
    b_total += bubble_sort_count(generated);
    s_total += selection_sort_count(generated);
    i_total += insertion_sort_count(generated); 
    cout << b_total << "  " << s_total << "  " << i_total << "  " << x << "[";
    for (int y = 0; y < x; y ++){
        cout << generated[y] << ", ";
    }
    cout << "]\n";
    }
   
    cout << "Bubble sort comaprisons " << b_total << " comparisons.\n";
    cout << "Selection sort comparisons " << s_total << " comparisons.\n";
    cout << "Insertion sort comparisons " << i_total << " comparisons.\n";

    return 0;

}

