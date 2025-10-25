"""
公共模块：提供图的数据结构和并查集实现
"""

class Edge:
    """表示一条边"""
    def __init__(self, u, v, weight):
        self.u = u  # 起点
        self.v = v  # 终点
        self.weight = weight  # 边权（限重）

    def __repr__(self):
        return f"Edge({self.u}, {self.v}, {self.weight})"


class UnionFind:
    """并查集数据结构"""
    def __init__(self, n):
        """
        初始化并查集
        Args:
            n: 元素个数（1-indexed，所以实际创建 n+1 个）
        """
        self.parent = list(range(n + 1))
        self.rank = [0] * (n + 1)

    def find(self, x):
        """
        查找 x 的根节点，带路径压缩优化
        Args:
            x: 要查找的元素
        Returns:
            x 所在集合的代表元素
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 路径压缩
        return self.parent[x]

    def union(self, x, y):
        """
        合并 x 和 y 所在的集合
        Args:
            x, y: 要合并的两个元素
        Returns:
            如果合并成功返回 True，如果已在同一集合返回 False
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # 按秩合并
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True

    def connected(self, x, y):
        """
        判断 x 和 y 是否在同一集合中
        Args:
            x, y: 要判断的两个元素
        Returns:
            如果在同一集合返回 True，否则返回 False
        """
        return self.find(x) == self.find(y)


class Graph:
    """图的邻接表表示"""
    def __init__(self, n):
        """
        初始化图
        Args:
            n: 节点个数
        """
        self.n = n
        self.adj = [[] for _ in range(n + 1)]  # adj[u] = [(v, weight), ...]

    def add_edge(self, u, v, weight):
        """
        添加一条无向边
        Args:
            u, v: 边的两个端点
            weight: 边权
        """
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))

    def get_neighbors(self, u):
        """
        获取节点 u 的所有邻居
        Args:
            u: 节点编号
        Returns:
            [(v, weight), ...] 邻居列表
        """
        return self.adj[u]
