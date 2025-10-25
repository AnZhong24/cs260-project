"""
Method 1: 使用倍增算法(Binary Lifting)求解货车运输问题

算法步骤：
1. 使用 Kruskal 算法构建最大生成树
2. 在最大生成树上使用倍增算法预处理 LCA
3. 对于每个查询，找到两点的 LCA 并计算路径上的最小边权
"""

from common import Edge, UnionFind, Graph


class TruckTransportSolver1:
    """使用倍增算法的货车运输求解器"""

    def __init__(self, n, m):
        """
        初始化求解器
        Args:
            n: 城市数量
            m: 道路数量
        """
        self.n = n
        self.m = m
        self.edges = []  # 原始边列表
        self.tree = Graph(n)  # 最大生成树
        self.uf = UnionFind(n)  # 并查集

        # 倍增相关数组
        self.MAX_LOG = 20  # log2(10000) < 20
        self.depth = [0] * (n + 1)  # 节点深度
        self.parent = [[0] * (self.MAX_LOG + 1) for _ in range(n + 1)]  # parent[u][k] = u 的第 2^k 个祖先
        self.min_weight = [[float('inf')] * (self.MAX_LOG + 1) for _ in range(n + 1)]  # min_weight[u][k] = u 到第 2^k 个祖先路径上的最小边权
        self.visited = [False] * (n + 1)  # DFS 访问标记

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
        核心思想：按边权从大到小排序，依次加入不构成环的边
        """
        # 按边权从大到小排序
        self.edges.sort(key=lambda e: e.weight, reverse=True)

        # Kruskal 算法
        for edge in self.edges:
            u, v, weight = edge.u, edge.v, edge.weight
            # 如果 u 和 v 不在同一连通分量，则加入这条边
            if self.uf.union(u, v):
                self.tree.add_edge(u, v, weight)

    def dfs(self, u, parent_node=-1, parent_weight=float('inf')):
        """
        深度优先搜索，预处理深度和倍增数组
        Args:
            u: 当前节点
            parent_node: 父节点
            parent_weight: 到父节点的边权
        """
        self.visited[u] = True

        # 设置直接父节点和到父节点的边权
        self.parent[u][0] = parent_node
        self.min_weight[u][0] = parent_weight

        # 遍历所有邻居
        for v, weight in self.tree.get_neighbors(u):
            if not self.visited[v]:
                self.depth[v] = self.depth[u] + 1
                self.dfs(v, u, weight)

    def preprocess_lca(self):
        """
        预处理倍增数组
        处理所有连通分量（可能是森林）
        """
        # 对每个连通分量的根节点进行 DFS
        for i in range(1, self.n + 1):
            if not self.visited[i]:
                self.depth[i] = 1
                self.dfs(i, i, float('inf'))  # 根节点的父节点是自己
                self.parent[i][0] = i
                self.min_weight[i][0] = float('inf')

        # 预处理倍增数组
        for k in range(1, self.MAX_LOG + 1):
            for u in range(1, self.n + 1):
                # parent[u][k] = parent[parent[u][k-1]][k-1]
                mid = self.parent[u][k - 1]
                self.parent[u][k] = self.parent[mid][k - 1]
                # min_weight[u][k] = min(min_weight[u][k-1], min_weight[parent[u][k-1]][k-1])
                self.min_weight[u][k] = min(
                    self.min_weight[u][k - 1],
                    self.min_weight[mid][k - 1]
                )

    def query_max_weight(self, x, y):
        """
        查询从 x 到 y 的路径上能承载的最大重量
        Args:
            x, y: 起点和终点城市
        Returns:
            最大载重，如果不连通返回 -1
        """
        # 检查是否连通
        if not self.uf.connected(x, y):
            return -1

        # 特殊情况：查询节点到自己
        if x == y:
            return float('inf')

        result = float('inf')

        # 确保 y 的深度不小于 x
        if self.depth[x] > self.depth[y]:
            x, y = y, x

        # 将 y 提升到与 x 相同的深度
        diff = self.depth[y] - self.depth[x]
        for k in range(self.MAX_LOG + 1):
            if (diff >> k) & 1:  # 如果 diff 的第 k 位是 1
                result = min(result, self.min_weight[y][k])
                y = self.parent[y][k]

        # 如果此时 x == y，说明 x 是 y 的祖先
        if x == y:
            return result

        # 同时向上跳，直到跳到 LCA 的下一层
        for k in range(self.MAX_LOG, -1, -1):
            if self.parent[x][k] != self.parent[y][k]:
                result = min(result, self.min_weight[x][k], self.min_weight[y][k])
                x = self.parent[x][k]
                y = self.parent[y][k]

        # 最后再跳一步到 LCA
        result = min(result, self.min_weight[x][0], self.min_weight[y][0])

        return result

    def solve(self):
        """
        求解问题：构建最大生成树并预处理 LCA
        """
        self.build_maximum_spanning_tree()
        self.preprocess_lca()


def main():
    """主函数：读取输入，求解并输出结果"""
    # 读取城市数和道路数
    n, m = map(int, input().split())

    # 创建求解器
    solver = TruckTransportSolver1(n, m)

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
