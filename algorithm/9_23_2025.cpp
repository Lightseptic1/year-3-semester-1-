/*
#include <iostream>
using namespace std;
int main(){
    int y = 0;
    for(int x = 0; x <= 10; x++){
        y += x;
    }
    cout << y;
    return 0;
}
*/
/*
#include <iostream>
#include <vector>
using namespace std;
int main()
{
    vector<string> names;
    cout << "How many names you want? ";
    int count;
    string str;
    cin >> count;
    for(int x = 0; x < count; x++){
        cout << "Enter name " << x+1 << " :";
        cin >> str;
        names.push_back(str);
    }
    cout << names.at(2);
    return 0;

}
    */
#include <iostream>
using namespace std;
int main(){
    int firstvalue, secondvalue;
    int *  mypointer;
    mypointer = &firstvalue;
    *mypointer = 10;
    mypointer = &secondvalue;
    *mypointer = 20;
    cout << firstvalue << endl;
    cout << secondvalue << endl;
    return 0;

    
}