"""
Method 2: 使用树链剖分(Heavy-Light Decomposition)求解货车运输问题

算法步骤：
1. 使用 Kruskal 算法构建最大生成树，将边转化为虚拟节点
2. 在扩展树上使用树链剖分预处理
3. 对于每个查询，使用树链剖分快速找到 LCA
"""

from common import Edge, UnionFind, Graph


class TruckTransportSolver2:
    """使用树链剖分的货车运输求解器"""

    def __init__(self, n, m):
        """
        初始化求解器
        Args:
            n: 城市数量（原始节点）
            m: 道路数量
        """
        self.n = n
        self.m = m
        self.edges = []  # 原始边列表
        self.node_count = n  # 当前节点总数（包括虚拟节点）
        self.tree = Graph(n + m)  # 扩展后的树（原始节点 + 虚拟节点）
        self.uf = UnionFind(n + m)  # 并查集

        # 树链剖分相关数组
        self.val = [0] * (n + m + 1)  # 虚拟节点的权值（边权）
        self.depth = [0] * (n + m + 1)  # 节点深度
        self.parent = [0] * (n + m + 1)  # 父节点
        self.heavy_son = [0] * (n + m + 1)  # 重儿子
        self.size = [0] * (n + m + 1)  # 子树大小
        self.top = [0] * (n + m + 1)  # 所在重链的顶端节点
        self.visited = [False] * (n + m + 1)  # 访问标记

    def add_edge(self, u, v, weight):
        """
        添加一条道路
        Args:
            u, v: 道路连接的两个城市
            weight: 道路的限重
        """
        self.edges.append(Edge(u, v, weight))

    def build_maximum_spanning_tree(self):
        """
        使用 Kruskal 算法构建最大生成树
        将每条边转化为一个虚拟节点，边权存储在虚拟节点上
        """
        # 按边权从大到小排序
        self.edges.sort(key=lambda e: e.weight, reverse=True)

        # Kruskal 算法
        for edge in self.edges:
            u, v, weight = edge.u, edge.v, edge.weight
            fu = self.uf.find(u)
            fv = self.uf.find(v)

            # 如果 u 和 v 不在同一连通分量
            if fu != fv:
                # 创建虚拟节点
                self.node_count += 1
                virtual_node = self.node_count
                self.val[virtual_node] = weight  # 虚拟节点存储边权

                # 合并三个节点到同一集合
                self.uf.parent[virtual_node] = virtual_node
                self.uf.parent[fu] = virtual_node
                self.uf.parent[fv] = virtual_node

                # 添加边：原始节点 -> 虚拟节点
                self.tree.add_edge(fu, virtual_node, weight)
                self.tree.add_edge(fv, virtual_node, weight)

    def dfs1(self, u, parent_node):
        """
        第一次 DFS：计算深度、父节点、子树大小、重儿子
        Args:
            u: 当前节点
            parent_node: 父节点
        """
        self.visited[u] = True
        self.size[u] = 1
        self.parent[u] = parent_node

        max_size = 0
        for v, _ in self.tree.get_neighbors(u):
            if v == parent_node:
                continue

            self.depth[v] = self.depth[u] + 1
            self.dfs1(v, u)
            self.size[u] += self.size[v]

            # 找重儿子（子树最大的儿子）
            if self.size[v] > max_size:
                max_size = self.size[v]
                self.heavy_son[u] = v

    def dfs2(self, u, top_node):
        """
        第二次 DFS：标记每个节点所在重链的顶端
        Args:
            u: 当前节点
            top_node: 当前重链的顶端节点
        """
        self.top[u] = top_node

        # 如果没有重儿子，返回
        if self.heavy_son[u] == 0:
            return

        # 先处理重儿子（继续当前重链）
        self.dfs2(self.heavy_son[u], top_node)

        # 再处理轻儿子（开始新的重链）
        for v, _ in self.tree.get_neighbors(u):
            if v != self.parent[u] and v != self.heavy_son[u]:
                self.dfs2(v, v)

    def get_lca(self, u, v):
        """
        使用树链剖分查找 LCA
        Args:
            u, v: 两个节点
        Returns:
            u 和 v 的最近公共祖先
        """
        # 不断跳链，直到两个节点在同一条重链上
        while self.top[u] != self.top[v]:
            # 将深度较大的链的顶端节点向上跳
            if self.depth[self.top[u]] > self.depth[self.top[v]]:
                u = self.parent[self.top[u]]
            else:
                v = self.parent[self.top[v]]

        # 现在 u 和 v 在同一条重链上，深度较小的就是 LCA
        return u if self.depth[u] < self.depth[v] else v

    def preprocess(self):
        """
        预处理树链剖分
        对每个连通分量分别处理
        """
        for i in range(1, self.node_count + 1):
            if not self.visited[i]:
                root = self.uf.find(i)
                self.depth[root] = 0
                self.dfs1(root, root)
                self.dfs2(root, root)

    def query_max_weight(self, x, y):
        """
        查询从 x 到 y 的路径上能承载的最大重量
        Args:
            x, y: 起点和终点城市（原始节点编号）
        Returns:
            最大载重，如果不连通返回 -1
        """
        # 检查是否连通
        if not self.uf.connected(x, y):
            return -1

        # 特殊情况：查询节点到自己
        if x == y:
            return float('inf')

        # 找到 LCA
        lca = self.get_lca(x, y)

        # LCA 对应的虚拟节点的权值就是路径上的瓶颈
        # 因为在最大生成树中，x 到 y 的路径上权值最小的边对应的虚拟节点就是它们的 LCA
        return self.val[lca]

    def solve(self):
        """
        求解问题：构建最大生成树并预处理树链剖分
        """
        self.build_maximum_spanning_tree()
        self.preprocess()


def main():
    """主函数：读取输入，求解并输出结果"""
    # 读取城市数和道路数
    n, m = map(int, input().split())

    # 创建求解器
    solver = TruckTransportSolver2(n, m)

    # 读取道路信息
    for _ in range(m):
        x, y, z = map(int, input().split())
        solver.add_edge(x, y, z)

    # 构建最大生成树并预处理
    solver.solve()

    # 读取查询数量
    q = int(input())

    # 处理每个查询
    for _ in range(q):
        x, y = map(int, input().split())
        print(solver.query_max_weight(x, y))


if __name__ == "__main__":
    main()
