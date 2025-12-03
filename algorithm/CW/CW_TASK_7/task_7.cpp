#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>
#include <limits>
using namespace std;

struct Item
{
    string name;
    int price;
};

struct State {
    int count;
    int spent;
};
bool b_value(const State& a, const State& b) {
    if (a.count != b.count) return a.count > b.count;
    return a.spent > b.spent;
}

vector<int> greedy(const vector<Item>& items, int budget) {
   int n = items.size();
   vector<int> indicies(n);
    for (int i = 0; i < n; i++) {
         indicies[i] = i;
    }
    sort(indicies.begin(), indicies.end(), [&](int a, int b) {
        return items[a].price < items[b].price;
    });
    vector<int> chosen;
    int remaining = budget;
    for(int idx : indicies){
        if(items[idx].price <= remaining){
            chosen.push_back(idx);
            remaining -= items[idx].price;
        }
    }
    return chosen;
}
vector<int> dpSelect(const vector<Item>& items, int budget){
    int n = items.size();
    vector<vector<State>> dp(n + 1, vector<State>(budget + 1, {0,0}));
    for(int i = 1; i <= n; ++i){
        int price = items[i-1].price;
        for(int w = 0; w <= budget; ++w){
            dp[i][w] = dp[i-1][w];
            if(w >= price){
                State cand = dp[i -1][w - price];
                cand.count += 1;
                cand.spent += price;
                if(b_value(cand, dp[i][w])){
                    dp[i][w] = cand;
                }            
        }
    }
}
    vector<int> chosen;
    int w = budget;
    for(int i = n; i >= 1; --i){
        int price = items[i-1].price;
        if(price <= w){
            State skip = dp[i-1][w];
            if (b_value(dp[i][w], skip)) {
                chosen.push_back(i-1);
                w -= price;
            }
        }
    }
    reverse(chosen.begin(), chosen.end());
    return chosen;
}
int totalPrice(const vector<Item>& items, const vector<int>& chosen){
    int sum = 0;
    for (int idx : chosen){
        sum += items[idx].price;
    }
    return sum;
}
void printChosen(const string& title, const vector<Item>& items, const vector<int>& chosen, int budget){
    cout << title << endl;
    if(chosen.empty()){
        cout << "  No items selected." << endl;
        return;
    }
    cout << "  Selected items:" << endl;
    cout << left << setw(3) << "#" << setw(20) << "Name" << "Price\n";
    cout << "--------------------------------------------\n";
    int idxDisplay = 1;
    for(int idx : chosen){
        cout << left << setw(3) << idxDisplay++ << setw(20) << items[idx].name << items[idx].price << endl;
    }
    int cost = totalPrice(items, chosen);
    cout << "\nTotal items: " << chosen.size() << "\n";
    cout << "Total cost:  " << cost << "\n";
    cout << "Budget:      " << budget << "\n";
    cout << "Remaining:   " << (budget - cost) << "\n";
}
int main(){
    cout << "Shopping Optimizer\n";
    int budget;
    cout << "Enter budget: ";
    cin >> budget;
    int n;
    cout << "Enter number of items:";
    cin >> n;
    vector<Item> items;
    cout << "Enter each item name followed by it's price:\n";
    for (int i = 0; i < n; ++i){
        Item it;
        cout << "Item " << (i+1) << " name: ";
        cin >> ws;
        getline(cin, it.name);
        cout << "Item " << (i+1) << " price: ";
        cin >> it.price;
        items.push_back(it);
    }
    vector<int> chosenGreedy = greedy(items, budget);
    vector<int> chosenDP = dpSelect(items, budget);
    printChosen("Greedy Selection:", items, chosenGreedy, budget);
    cout << "\n--------------------------------------------\n";
    printChosen("Dynamic Programming Selection:", items, chosenDP, budget);
    return 0;
}
