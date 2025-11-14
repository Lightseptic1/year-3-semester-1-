#include <iostream>
#include <string>
using namespace std;
void b_sort(string &word){
    int n = word.size();
    for(int x = 0; x < n-1; x++){
        for (int y = 0; y < n - x - 1; y++){
            if(word[y] > word[y + 1]){
                char temp = word[y];
                word[y] = word[y + 1];
                word[y+1] = temp;
            }
        }
    }
}
void anagram_checker(string word_1, string word_2){
    for(char &c : word_1) c = tolower(c);
    for (char &c : word_2) c = tolower(c);
    b_sort(word_1);
    b_sort(word_2);
    if (word_1 == word_2){
        cout << "They are anagrams! ";

    }
    else{
        cout << "They aren't anagrams! ";
    }
}

int main(){
    string word_1, word_2;
    cin >> word_1 >> word_2;
    anagram_checker(word_1, word_2);
    return 0;


}
