#!/usr/bin/env python3
# experiment_bottleneck_floyd_vs_method1.py
# Compare Floyd–Warshall (bottleneck variant) vs. Method 1 (MST + Binary Lifting)
# Features:
# - Environment capture (Python, platform, CPU)
# - Reproducibility (seeds, trials)
# - Mean ± std reporting
# - Unified result encoding: disconnected=-1; self-pair=+inf -> 10**18
# - CSV export
# - --connected-only: queries restricted to DSU-connected pairs


# Environment
# Python: 3.14.0 | Platform: macOS-15.6-arm64-arm-64bit-Mach-O | Processor: arm | CPUs: 16
# Graph distribution: G(n,m), weight ~ Uniform[1, 1000]
# Trials per scale: 10, seed base: 1234
# Connected-only queries: False



# Scale  | n    | m    | q   | ConnectedOnly | Floyd_pre_ms        | Floyd_q_ms  | M1_pre_ms   | M1_q_ms     | Mismatch_sum | Mismatch_avg
# ----------------------------------------------------------------------------------------------------------------------------------------
# Small  | 100  | 200  | 50  | False         | 20.37 ± 2.07        | 0.01 ± 0.00 | 0.15 ± 0.03 | 0.04 ± 0.01 | 0            | 0           
# Medium | 500  | 1000 | 100 | False         | 2401.40 ± 96.54     | 0.02 ± 0.01 | 0.90 ± 0.15 | 0.12 ± 0.01 | 0            | 0           
# Large  | 1000 | 2000 | 200 | False         | 20004.56 ± 429.15   | 0.04 ± 0.01 | 1.92 ± 0.04 | 0.27 ± 0.02 | 0            | 0           
# XL     | 2000 | 4000 | 400 | False         | 164475.34 ± 3011.78 | 0.09 ± 0.02 | 4.46 ± 0.31 | 0.58 ± 0.02 | 0            | 0           

import argparse, csv, math, os, platform, random, statistics, sys, time
from collections import defaultdict

# -----------------------------
# Utilities
# -----------------------------
def now_ms() -> float:
    return time.perf_counter() * 1000.0

def mean_std(values):
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return float(values[0]), 0.0
    return statistics.mean(values), statistics.pstdev(values)

def format_ms_pair(values):
    mu, sd = mean_std(values)
    return f"{mu:.2f} ± {sd:.2f}"

def cpu_count():
    try:
        return os.cpu_count()
    except Exception:
        return None

def env_summary():
    lines = []
    lines.append(f"Python: {sys.version.split()[0]}")
    lines.append(f"Platform: {platform.platform()}")
    proc = platform.processor() or "Unknown-CPU"
    lines.append(f"Processor: {proc}")
    lines.append(f"CPUs: {cpu_count()}")
    return " | ".join(lines)

# -----------------------------
# DSU + Graph
# -----------------------------
class UnionFind:
    def __init__(self, n):
        self.p = list(range(n + 1))
        self.r = [0] * (n + 1)

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)

class Graph:
    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n + 1)]
    def add_edge(self, u, v, w):
        self.adj[u].append((v, w))
        self.adj[v].append((u, w))
    def neighbors(self, u):
        return self.adj[u]

# -----------------------------
# Method 1: MST + Binary Lifting
# -----------------------------
class Method1Solver:
    def __init__(self, n, edges):
        self.n = n
        self.edges = edges[:]  # (u,v,w)
        self.uf = UnionFind(n)
        self.tree = Graph(n)
        self.vis = [False] * (n + 1)
        self.depth = [0] * (n + 1)

        # dynamic MAX_LOG for correctness
        self.MAX_LOG = (n - 1).bit_length()
        self.parent = [[0] * (self.MAX_LOG + 1) for _ in range(n + 1)]
        self.minw = [[float('inf')] * (self.MAX_LOG + 1) for _ in range(n + 1)]

    def build_mst(self):
        # Kruskal in descending weights (maximum spanning forest)
        self.edges.sort(key=lambda e: e[2], reverse=True)
        for u, v, w in self.edges:
            if self.uf.union(u, v):
                self.tree.add_edge(u, v, w)

    def dfs(self, u, p, pw):
        self.vis[u] = True
        self.parent[u][0] = p
        self.minw[u][0] = pw
        for v, w in self.tree.neighbors(u):
            if not self.vis[v]:
                self.depth[v] = self.depth[u] + 1
                self.dfs(v, u, w)

    def preprocess(self):
        # DFS each component; use itself as parent root with inf weight
        for i in range(1, self.n + 1):
            if not self.vis[i]:
                self.depth[i] = 1
                self.dfs(i, i, float('inf'))
                self.parent[i][0] = i
                self.minw[i][0] = float('inf')

        # Binary lifting tables
        for k in range(1, self.MAX_LOG + 1):
            for u in range(1, self.n + 1):
                mid = self.parent[u][k - 1]
                self.parent[u][k] = self.parent[mid][k - 1]
                self.minw[u][k] = min(self.minw[u][k - 1], self.minw[mid][k - 1])

    def solve(self):
        self.build_mst()
        self.preprocess()

    def query(self, x, y):
        # disconnected?
        if not self.uf.connected(x, y):
            return -1
        if x == y:
            return float('inf')

        res = float('inf')

        # ensure depth[y] >= depth[x]
        if self.depth[x] > self.depth[y]:
            x, y = y, x

        # lift y up
        diff = self.depth[y] - self.depth[x]
        bit = 0
        while diff:
            if diff & 1:
                res = min(res, self.minw[y][bit])
                y = self.parent[y][bit]
            diff >>= 1
            bit += 1

        if x == y:
            return res

        for k in range(self.MAX_LOG, -1, -1):
            if self.parent[x][k] != self.parent[y][k]:
                res = min(res, self.minw[x][k], self.minw[y][k])
                x = self.parent[x][k]
                y = self.parent[y][k]

        # one final step to LCA
        res = min(res, self.minw[x][0], self.minw[y][0])
        return res

# -----------------------------
# Floyd–Warshall (bottleneck)
# dp[i][j] = max_k min(dp[i][k], dp[k][j])
# -----------------------------
def floyd_bottleneck(n, edges):
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = float('inf')
    for u, v, w in edges:
        u -= 1; v -= 1
        if w > dp[u][v]:
            dp[u][v] = w
            dp[v][u] = w

    for k in range(n):
        rowk = dp[k]
        for i in range(n):
            dik = dp[i][k]
            if dik == 0:
                continue
            rowi = dp[i]
            for j in range(n):
                if rowk[j] == 0:
                    continue
                cand = min(dik, rowk[j])
                if cand > rowi[j]:
                    rowi[j] = cand
    return dp  # 0 => disconnected

# -----------------------------
# Random graph + queries
# -----------------------------
def make_random_graph(n, m, cap_lo=1, cap_hi=1000, seed=0):
    rnd = random.Random(seed)
    edges = set()
    # simple G(n, m) without duplicates/self-loops
    while len(edges) < m:
        u = rnd.randint(1, n)
        v = rnd.randint(1, n)
        if u == v:
            continue
        if u > v:
            u, v = v, u
        w = rnd.randint(cap_lo, cap_hi)
        edges.add((u, v, w))
    return list(edges)

def make_queries(n, q, seed=1):
    rnd = random.Random(seed)
    return [(rnd.randint(1, n), rnd.randint(1, n)) for _ in range(q)]

def make_connected_queries(n, q, uf, seed=1, max_attempts=None):
    """Sample q pairs that are DSU-connected. If not enough pairs can be found
    within max_attempts, return as many as found."""
    rnd = random.Random(seed)
    out = []
    attempts = 0
    if max_attempts is None:
        max_attempts = 20 * q * max(1, n // 10)  # generous cap to avoid infinite loops
    while len(out) < q and attempts < max_attempts:
        s, t = rnd.randint(1, n), rnd.randint(1, n)
        attempts += 1
        if uf.connected(s, t):
            out.append((s, t))
    return out

# -----------------------------
# One trial of one scale
# -----------------------------
def run_one_trial(n, m, q, seed_base, cap_lo, cap_hi, connected_only):
    edges = make_random_graph(n, m, cap_lo=cap_lo, cap_hi=cap_hi, seed=seed_base)

    # Build Method 1 first so we can use DSU connectivity if needed for queries
    t4 = now_ms()
    m1 = Method1Solver(n, edges)
    m1.solve()
    t5 = now_ms()
    meth1_pre_ms = t5 - t4

    # Queries
    if connected_only:
        queries = make_connected_queries(n, q, m1.uf, seed=seed_base + 1)
        # If稀疏导致不够 q 个，用已有的尽量评测
        if len(queries) < q:
            # 补齐剩余随机对（可能不连通，但 mismatch 仍按统一编码比较）
            queries += make_queries(n, q - len(queries), seed=seed_base + 2)
    else:
        queries = make_queries(n, q, seed=seed_base + 1)

    # Floyd (optionally skip if n too large)
    floyd_pre_ms = None
    floyd_q_ms = None
    floyd_answers = None
    t0 = now_ms()
    dp = floyd_bottleneck(n, edges)
    t1 = now_ms()
    floyd_pre_ms = t1 - t0
    t2 = now_ms()
    floyd_answers = []
    for s, t in queries:
        val = dp[s-1][t-1]
        if val == 0:                # disconnected
            floyd_answers.append(-1)
        elif val == float('inf'):   # s==t
            floyd_answers.append(10**18)
        else:
            floyd_answers.append(int(val))
    t3 = now_ms()
    floyd_q_ms = t3 - t2

    # Method 1 query phase (unified encoding)
    t6 = now_ms()
    meth1_answers = []
    for s, t in queries:
        val = m1.query(s, t)
        if val == float('inf'):     # s==t
            val = 10**18
        # val == -1 means disconnected
        meth1_answers.append(int(val))
    t7 = now_ms()
    meth1_q_ms = t7 - t6

    # agreement (if Floyd computed)
    disagree = None
    if floyd_answers is not None:
        disagree = sum(a != b for a, b in zip(floyd_answers, meth1_answers))

    return floyd_pre_ms, floyd_q_ms, meth1_pre_ms, meth1_q_ms, disagree

# -----------------------------
# Multi-trial harness
# -----------------------------
def run_scale(scale_name, n, m, q, trials, seed_base, cap_lo, cap_hi, connected_only):
    floyd_pre_list, floyd_q_list = [], []
    m1_pre_list, m1_q_list = [], []
    mismatch_list = []

    for t in range(trials):
        seed = seed_base + 1000 * t  # deterministic but different per trial
        fp, fq, mp, mq, mis = run_one_trial(
            n, m, q, seed, cap_lo, cap_hi, connected_only
        )
        if fp is not None: floyd_pre_list.append(fp)
        if fq is not None: floyd_q_list.append(fq)
        m1_pre_list.append(mp)
        m1_q_list.append(mq)
        if mis is not None: mismatch_list.append(mis)

    # combine stats
    res = {
        "Scale": scale_name,
        "n": n, "m": m, "q": q,
        "ConnectedOnly": connected_only,
        "Floyd_pre_ms": format_ms_pair(floyd_pre_list) if floyd_pre_list else "SKIPPED",
        "Floyd_q_ms": format_ms_pair(floyd_q_list) if floyd_q_list else "SKIPPED",
        "M1_pre_ms": format_ms_pair(m1_pre_list),
        "M1_q_ms": format_ms_pair(m1_q_list),
        "Mismatch_sum": sum(mismatch_list) if mismatch_list else ("N/A" if not floyd_pre_list else 0),
        "Mismatch_avg": (statistics.mean(mismatch_list) if mismatch_list else float("nan")),
    }
    return res

def print_table(results):
    cols = ["Scale","n","m","q","ConnectedOnly","Floyd_pre_ms","Floyd_q_ms","M1_pre_ms","M1_q_ms","Mismatch_sum","Mismatch_avg"]
    widths = {c: max(len(c), max(len(str(r[c])) for r in results)) for c in cols}
    line = " | ".join(c.ljust(widths[c]) for c in cols)
    print(line)
    print("-" * len(line))
    for r in results:
        row = " | ".join(str(r[c]).ljust(widths[c]) for c in cols)
        print(row)

def write_csv(path, results):
    cols = ["Scale","n","m","q","ConnectedOnly","Floyd_pre_ms","Floyd_q_ms","M1_pre_ms","M1_q_ms","Mismatch_sum","Mismatch_avg"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow(r)

# -----------------------------
# CLI
# -----------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Bottleneck path experiments: Floyd vs MST+Binary-Lifting")
    p.add_argument("--trials", type=int, default=10, help="number of repeated trials per scale")
    p.add_argument("--seed", type=int, default=1234, help="base random seed")
    p.add_argument("--cap-lo", type=int, default=1, help="min edge capacity")
    p.add_argument("--cap-hi", type=int, default=1000, help="max edge capacity")
    p.add_argument("--skip-floyd-threshold", type=int, default=1200,
                   help="skip Floyd when n > threshold (Python runtime realism)")
    p.add_argument("--connected-only", action="store_true",
                   help="restrict queries to DSU-connected pairs (from MST/DSU)")
    p.add_argument("--csv", type=str, default="", help="optional path to write CSV results")
    return p.parse_args()

def main():
    args = parse_args()

    # Define scales (editable)
    scales = [
        ("Small", 100, 200, 50),
        ("Medium", 500, 1000, 100),
        ("Large", 1000, 2000, 200),
        ("XL", 2000, 4000, 400),
    ]

    print("# Environment")
    print(env_summary())
    print(f"Graph distribution: G(n,m), weight ~ Uniform[{args.cap_lo}, {args.cap_hi}]")
    print(f"Trials per scale: {args.trials}, seed base: {args.seed}")
    print(f"Connected-only queries: {args.connected_only}\n")

    results = []
    for name, n, m, q in scales:
        res = run_scale(
            name, n, m, q,
            trials=args.trials,
            seed_base=args.seed,
            cap_lo=args.cap_lo,
            cap_hi=args.cap_hi,
            connected_only=args.connected_only,
        )
        results.append(res)

    print_table(results)

    if args.csv:
        write_csv(args.csv, results)
        print(f"\nCSV written to: {args.csv}")

if __name__ == "__main__":
    main()
