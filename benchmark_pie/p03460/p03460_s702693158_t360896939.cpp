#include<bits/stdc++.h>

using namespace std;

int a[1003][1003],b[1003][1003];

int s1[1003][1003],s2[1003][1003];

int n,k;

char t;

int dfs(int x,int y)

{

	int i=0,j=0;

	i=s1[k][k]-s1[x][k]-s1[k][y]+s1[x][y]+s1[x][y];

	i+=s2[x][k]+s2[k][y]-s2[x][y]-s2[x][y];

	j+=s2[k][k]-s2[x][k]-s2[k][y]+s2[x][y]+s2[x][y];

	j+=s1[x][k]+s1[k][y]-s1[x][y]-s1[x][y];

	return max(i,j);

}

int main()

{

    int ans,x,y;

	cin>>n>>k;

	for (int i=1;i<=n;i++)

	{

		cin>>x>>y>>t;

		int tx=x,ty=y;

		x%=k;y%=k;

		if (x==0)x=k;

		if (y==0)y=k;

		if (((abs(tx-x)+abs(ty-y))/k)%2==1)

		{

			if (t=='W')t='B';else t='W';

		}

		if (t=='W')b[x][y]++;else a[x][y]++;

	}

	for (int i=1;i<=k;i++)

	{

		for (int j=1;j<=k;j++)

		{

			s1[i][j]=s1[i-1][j]+s1[i][j-1]-s1[i-1][j-1]+a[i][j];

			s2[i][j]=s2[i-1][j]+s2[i][j-1]-s2[i-1][j-1]+b[i][j];

		}

	}

	for (int i=0;i<=k+1;i++)

	{

		for (int j=0;j<=k+1;j++)

		{

			ans=max(ans,dfs(i,j));

		}

	}

	cout<<ans;

	return 0;

}
