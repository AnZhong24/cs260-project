#include<iostream>
#include<vector>
#include<algorithm>
#include<queue>
#include<cstring>
#include<cstdio>
using namespace std;

int read()
{
    int f=1,x=0;
    char ss=getchar();
    while(ss<'0'||ss>'9'){if(ss=='-')f=-1;ss=getchar();}
    while(ss>='0'&&ss<='9'){x=x*10+ss-'0';ss=getchar();}
    return f*x;
}

const int maxn=200010;
int n,m,cnt;
struct node{int u,v,dis;}edge[maxn];
bool cmp(node a,node b){return a.dis>b.dis;}
struct node2{int v,nxt;}E[maxn];
int head[maxn],tot;
int val[maxn],ff[maxn],vis[maxn];
int fa[maxn],top[maxn],son[maxn];
int size[maxn],dep[maxn];

void add(int u,int v)
{
    E[++tot].nxt=head[u];
    E[tot].v=v;
    head[u]=tot;
}

int find(int x)
{
    if(x==ff[x])return x;
    else return ff[x]=find(ff[x]);
}

void dfs1(int u,int pa)
{
    size[u]=1; vis[u]=1;
    for(int i=head[u];i;i=E[i].nxt)
    {
        int v=E[i].v;
        if(v==pa) continue;
        dep[v]=dep[u]+1; fa[v]=u;
        dfs1(v,u);
        size[u]+=size[v];
        if(size[v]>size[son[u]])son[u]=v;
    }
}

void dfs2(int u,int tp)
{
    top[u]=tp;
    if(son[u])dfs2(son[u],tp);
    for(int i=head[u];i;i=E[i].nxt)
    {
        int v=E[i].v;
        if(v==fa[u]||v==son[u])continue;
        dfs2(v,v);
    }
}

void kruskal()
{
    sort(edge+1,edge+1+m,cmp);
    for(int i=1;i<=n;++i)ff[i]=i;
    for(int i=1;i<=m;++i)
    {
        int fu=find(edge[i].u),fv=find(edge[i].v);
        if(fu!=fv)
        {
            val[++cnt]=edge[i].dis;
            ff[cnt]=ff[fu]=ff[fv]=cnt;
            add(fu,cnt); add(cnt,fu);
            add(fv,cnt); add(cnt,fv);
        }
    }
    for(int i=1;i<=cnt;++i)//注意图可能是个森林
    if(!vis[i])
    {
        int f=find(i);
        dfs1(f,0); dfs2(f,f);
    }
}

int LCA(int u,int v)
{
    while(top[u]!=top[v])
    {
        if(dep[top[u]]>dep[top[v]])u=fa[top[u]];
        else v=fa[top[v]];
    }
    return dep[u]<dep[v]?u:v;
}

int main()
{
    n=read();m=read();cnt=n;
    for(int i=1;i<=m;i++)
    edge[i].u=read(),edge[i].v=read(),edge[i].dis=read();
    
    kruskal();
    int q=read();
    while(q--)
    {
        int u=read(),v=read();
        if(find(u)!=find(v))printf("-1\n");
        else printf("%d\n",val[LCA(u,v)]);
    }
    return 0;
    //niiick
}
