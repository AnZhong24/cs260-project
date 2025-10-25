# 货车运输问题 - 算法项目

基于 NOIP 2013 提高组题目的算法课程项目，实现并对比两种解决方案。

## 项目简介

本项目研究货车运输问题：在有权重限制的城市道路网络中，找出从一个城市到另一个城市的路径上能通过的最大载重。

核心算法：**最大生成树 + LCA（最近公共祖先）**

## 实现方案

### Method 1: 倍增算法 (Binary Lifting)
- 使用 Kruskal 构建最大生成树
- 使用倍增算法预处理 LCA
- 时间复杂度：O(m log m + n log n + q log n)
- 空间复杂度：O(n log n + m)

### Method 2: 树链剖分 (Heavy-Light Decomposition)
- 使用 Kruskal 构建最大生成树（含虚拟节点）
- 使用树链剖分查询 LCA
- 时间复杂度：O(m log m + n + q log n)
- 空间复杂度：O(n + m)

## 项目结构

```
cs260/
├── docs/                        # 文档目录
│   ├── question.md              # 原始题目
│   ├── project_description.md   # 项目说明
│   ├── method1_explanation.md   # Method 1 详解
│   └── method2_explanation.md   # Method 2 详解
├── refs/                        # 参考实现（C++）
│   ├── method1.cpp
│   └── method2.cpp
├── src/                         # Python 实现
│   ├── common.py                # 公共模块
│   ├── method1_binary_lifting.py
│   ├── method2_tree_chain.py
│   └── test_methods.py          # 测试代码
├── done.md                      # 完成记录
└── README.md                    # 本文件
```

## 快速开始

### 运行测试
```bash
cd src
python test_methods.py
```

### 使用 Method 1
```python
from method1_binary_lifting import TruckTransportSolver1

solver = TruckTransportSolver1(n=4, m=3)
solver.add_edge(1, 2, 4)
solver.add_edge(2, 3, 3)
solver.add_edge(3, 1, 1)
solver.solve()

result = solver.query_max_weight(1, 3)  # 输出: 3
```

### 使用 Method 2
```python
from method2_tree_chain import TruckTransportSolver2

solver = TruckTransportSolver2(n=4, m=3)
solver.add_edge(1, 2, 4)
solver.add_edge(2, 3, 3)
solver.add_edge(3, 1, 1)
solver.solve()

result = solver.query_max_weight(1, 3)  # 输出: 3
```

## 测试结果

### 正确性测试
- ✓ 基础功能测试：4/4 通过
- ✓ 边界情况测试：4/4 通过
- ✓ 一致性测试：5/5 通过

### 性能对比

| 规模 | n | m | q | Method 1 | Method 2 | 加速比 |
|------|---|---|---|----------|----------|--------|
| 小 | 100 | 200 | 50 | 0.43ms | 0.18ms | 2.34x |
| 中 | 500 | 1000 | 100 | 3.04ms | 1.12ms | 2.72x |
| 大 | 1000 | 2000 | 200 | 4.33ms | 2.69ms | 1.61x |

**结论**：Method 2 (树链剖分) 在性能上全面优于 Method 1。

## 技术亮点

1. **模块化设计**：公共模块复用，代码结构清晰
2. **完整测试**：包含基础、边界、一致性和性能测试
3. **详细文档**：每个方法都有独立的详细说明文档
4. **优化实现**：
   - 并查集路径压缩和按秩合并
   - 位运算优化倍增查询
   - 虚拟节点技巧处理边权

## 学习资源

- 详细的算法说明：见 `docs/method1_explanation.md` 和 `docs/method2_explanation.md`
- 完整的实现代码：见 `src/` 目录
- 测试用例：见 `src/test_methods.py`
- 完成记录：见 `done.md`

## 依赖

- Python 3.7+
- 无需额外依赖库（仅使用标准库）

## 作者

CS260 算法课程项目

## 许可

本项目仅用于学习和研究目的。
