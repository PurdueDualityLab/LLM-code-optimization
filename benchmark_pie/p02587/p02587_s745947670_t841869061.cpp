#include <iostream>

#include <string>

#include <cstdlib>

#include <cmath>

#include <vector>

#include <unordered_map>

#include <map>

#include <set>

#include <algorithm>

#include <queue>

#include <stack>

#include <functional>

#include <bitset>

#include <assert.h>

#include <unordered_map>

#include <fstream>

#include <ctime>

#include <complex>

using namespace std;

typedef long long ll;

typedef vector<ll> vl;

typedef vector<vl> vvl;

typedef vector<char> vc;

typedef vector<string> vs;

typedef vector<bool> vb;

typedef vector<double> vd;

typedef pair<ll,ll> P;

typedef pair<int,int> pii;

typedef vector<P> vpl;

typedef tuple<ll,ll,ll> tapu;

#define rep(i,n) for(int i=0; i<(n); i++)

#define REP(i,a,b) for(int i=(a); i<(b); i++)

#define all(x) (x).begin(), (x).end()

#define rall(x) (x).rbegin(), (x).rend()

const int inf = 1<<30;

const ll linf = 1LL<<62;

const int MAX = 510000;

ll dy[8] = {1,-1,0,0,1,-1,1,-1};

ll dx[8] = {0,0,1,-1,1,-1,-1,1};

const double pi = acos(-1);

const double eps = 1e-7;

template<typename T1,typename T2> inline bool chmin(T1 &a,T2 b){

	if(a>b){

		a = b; return true;

	}

	else return false;

}

template<typename T1,typename T2> inline bool chmax(T1 &a,T2 b){

	if(a<b){

		a = b; return true;

	}

	else return false;

}

template<typename T> inline void print(T &a){

    rep(i,a.size()) cout << a[i] << " ";

    cout << "\n";

}

template<typename T1,typename T2> inline void print2(T1 a, T2 b){cout << a << " " << b << "\n";}

template<typename T1,typename T2,typename T3> inline void print3(T1 a, T2 b, T3 c){

	cout << a << " " << b << " " << c << "\n";

}

ll pcount(ll x) {return __builtin_popcountll(x);}

const int mod = 1e9 + 7;

//const int mod = 998244353;



struct state{

	string s;

	ll cost;

	int d;

	bool operator< (const state &st) const {

		return cost > st.cost;

	}

};



map<pair<string,int>,ll> mp;



void ins(string s, ll c, int d){

	if(mp.find({s,d}) != mp.end()){

		chmin(mp[{s,d}], c);

	}else{

		mp[{s,d}] = c;

	}

}



int main(){

	int n; cin >> n;

	vl c(n);

	vs s(n);

	rep(i,2) mp[{"",i}] = linf;

	rep(i,n){

		cin >> s[i] >> c[i];

		int m = s[i].size();

		rep(j,26){

			s[i].push_back((char)('a'+j));

			ins(s[i],c[i],0);

			reverse(all(s[i]));

			ins(s[i],c[i],1);

			reverse(all(s[i]));

			s[i].pop_back();

		}

		rep(j,m){

			string t = s[i].substr(0,j);

			string u = t; reverse(all(u));

			if(t == u){

				string v = s[i].substr(j,m-j);

				ins(v,c[i],0);

			}

		}

		rep(j,m){

			string t = s[i].substr(j,s[i].size()-j);

			string u = t; reverse(all(u));

			if(t == u){

				string v = s[i].substr(0,j);

				reverse(all(v));

				ins(v,c[i],1);

			}

		}

	}

	priority_queue<state> pq;

	auto push = [&](string s, ll c, int d){

		state st;

		st.s = s; st.cost = c; st.d = d;

		if(mp.find({s,d}) != mp.end()){

			if(mp[{s,d}] > c){

				mp[{s,d}] = c;

				pq.emplace(st);

			}

		}else{

			mp[{s,d}] = c;

			pq.emplace(st);

		}

	};

	for(auto i : mp){

		state st;

		st.s = i.first.first; st.cost = i.second;

		st.d = i.first.second;

		pq.emplace(st);

	}

	while(!pq.empty()){

		auto p = pq.top(); pq.pop();

		if(mp[{p.s,p.d}] < p.cost) continue;

		rep(i,n){

			if(p.d == 0){

				reverse(all(s[i]));

				int si = s[i].size(), sp = p.s.size();

				if(si < sp){

					string t = p.s.substr(0,si);

					if(t == s[i]){

						push(p.s.substr(si,sp-si), p.cost+c[i], p.d);

					}

				}else{

					string t = s[i].substr(0,sp);

					if(t == p.s){

						push(s[i].substr(sp,si-sp), p.cost+c[i], 1-p.d);

					}

				}

				reverse(all(s[i]));

			}else{

				int si = s[i].size(), sp = p.s.size();

				if(si < sp){

					string t = p.s.substr(0,si);

					if(t == s[i]){

						push(p.s.substr(si,sp-si), p.cost+c[i], p.d);

					}

				}else{

					string t = s[i].substr(0,sp);

					if(t == p.s){

						push(s[i].substr(sp,si-sp), p.cost+c[i], 1-p.d);

					}

				}

			}

		}

	}

	ll ans = min(mp[{"",0}], mp[{"",1}]);

	if(ans == linf) cout << -1 << endl;

	else cout << ans << "\n";

}