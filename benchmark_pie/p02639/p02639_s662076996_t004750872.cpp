#include<iostream>
using namespace std;

int main(){
    int x1,x2,x3,x4,x5;
    cin >> x1 >> x2 >> x3 >> x4 >> x5;
    int ans = 0;
    if(x1 == 0){ans = 1;}
    if(x2 == 0){ans = 2;}
    if(x3 == 0){ans = 3;}
    if(x4 == 0){ans = 4;}
    if(x5 == 0){ans = 5;}
    cout << ans << endl;
    return 0;
}
