/*

	容斥原理 + 递推

	不重复地选择一些的集合

	答案要求的是每一种元素必须出现两次以上

	ans = \sum (-1)^i f[i]

	其中 f[i] 表示至少有 i 个元素不满足条件

	考虑枚举这 i 个元素, 有 C(n, i) 种方式

	这 i 个元素放在集合的个数是 O(n) 级别的, 而且最后答案也跟集合个数有关

	就先设 g[i][j] 为考虑了前 i 个元素放在 j 个集合里, 且都不满足条件的方案数

	g[i][j] = g[i - 1][j - 1] + g[i - 1][j] * (j + 1)

	前一个表示这个元素就放在第 j 个集合里

	后一个表示这个元素可以放在 j 个集合里, 也可以不放 

*/

#include <bits/stdc++.h>

#define N 3005



using namespace std;



const int bl = 32761;



int n, mod;

int comb[N][N], g[N][N];



int pw[2][2][bl + 1];



void init(int a[2][bl + 1], int x, const int mo) {

	a[0][0] = 1;

	for(int i = 1; i <= bl; ++i)

		a[0][i] = 1LL * x * a[0][i - 1] % mo;

	a[1][0] = 1;

	for(int i = 1; i <= bl; ++i)

		a[1][i] = 1LL * a[0][bl] * a[1][i - 1] % mo;

}

inline int fpm(int typ, int y) {

	return 1LL * pw[typ][1][y / bl] * pw[typ][0][y % bl] % mod;

}



int main() {

	scanf("%d %d", &n, &mod);

	

	init(pw[0], 2, mod);

	init(pw[1], 2, mod - 1);

	

	for(int i = 0; i <= n; ++i) {

		comb[i][0] = 1;

		for(int j = 1; j <= i; ++j)

			comb[i][j] = (comb[i - 1][j - 1] + comb[i - 1][j]) % mod;

	}

	for(int i = 0; i <= n; ++i) {

		g[i][0] = 1;

		for(int j = 1; j <= i; ++j)

			g[i][j] = (g[i - 1][j - 1] +

			(j + 1LL) * g[i - 1][j]) % mod;

	}

	

	int ans = 0;

	for(int i = 0; i <= n; ++i) {

		int res = 0;

		for(int j = 0; j <= i; ++j) {

			res = (res + 1LL * comb[n][i] * g[i][j] % mod

				   * fpm(0, (n - i) * j) % mod

				   * fpm(0, fpm(1, n - i))) % mod;

		}

		if(i & 1) {

			ans = (ans + mod - res) % mod;

		} else {

			ans = (ans + res) % mod;

		}

	}

	printf("%d\n", ans);

	return 0;

}