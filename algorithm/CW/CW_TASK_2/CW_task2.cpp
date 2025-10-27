#include <iostream>  
using namespace std;
int i = 1;
void towerOfHanoi(int n, char from_rod, char to_rod, char aux_rod)
{
    if (n == 0) {
        return;
    }
    bool adjacent = (from_rod=='A'&&to_rod=='B')||(from_rod=='B'&&to_rod=='A')||(from_rod=='B'&&to_rod=='C')||(from_rod=='C'&&to_rod=='B');
    if (adjacent) {
        towerOfHanoi(n - 1, from_rod, aux_rod, to_rod);
        cout << "Move no. " << i << " : ";
        cout << "Move disk " << n << " from rod " << from_rod << " to rod " << to_rod << endl;
        i++;
        towerOfHanoi(n - 1, aux_rod, to_rod, from_rod);
    } else {
        towerOfHanoi(n - 1, from_rod, to_rod, aux_rod);
        cout << "Move no. " << i << " : ";
        cout << "Move disk " << n << " from rod " << from_rod << " to rod " << aux_rod << endl;
        i++;
        towerOfHanoi(n - 1, to_rod, from_rod, aux_rod);
        cout << "Move no. " << i << " : ";
        cout << "Move disk " << n << " from rod " << aux_rod << " to rod " << to_rod << endl;
        i++;
        towerOfHanoi(n - 1, from_rod, to_rod, aux_rod);
    }
}
int main()
{
    int N; 
    cout << "How many disks? ";
    cin >> N;
    
    towerOfHanoi(N, 'A', 'C', 'B');
    return 0;
}
