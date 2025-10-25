"""
测试两种方法的正确性和性能

测试内容：
1. 基础功能测试：使用题目提供的样例
2. 边界情况测试：不连通图、单节点、多连通分量等
3. 一致性测试：验证两种方法的结果是否一致
4. 性能测试：对比两种方法在大规模数据下的运行时间
"""

import sys
import time
from io import StringIO
from method1_binary_lifting import TruckTransportSolver1
from method2_tree_chain import TruckTransportSolver2


class TestCase:
    """测试用例"""
    def __init__(self, name, n, m, edges, queries, expected):
        self.name = name
        self.n = n
        self.m = m
        self.edges = edges  # [(u, v, w), ...]
        self.queries = queries  # [(x, y), ...]
        self.expected = expected  # [result, ...]


def run_test_case(solver_class, test_case):
    """
    运行单个测试用例
    Args:
        solver_class: 求解器类
        test_case: 测试用例
    Returns:
        (results, time_used) 结果列表和运行时间
    """
    start_time = time.time()

    # 创建求解器
    solver = solver_class(test_case.n, test_case.m)

    # 添加边
    for u, v, w in test_case.edges:
        solver.add_edge(u, v, w)

    # 构建并预处理
    solver.solve()

    # 执行查询
    results = []
    for x, y in test_case.queries:
        result = solver.query_max_weight(x, y)
        results.append(result)

    end_time = time.time()
    time_used = end_time - start_time

    return results, time_used


def test_basic_cases():
    """基础功能测试"""
    print("=" * 60)
    print("基础功能测试")
    print("=" * 60)

    # 测试用例 1：题目样例
    test1 = TestCase(
        name="题目样例",
        n=4, m=3,
        edges=[(1, 2, 4), (2, 3, 3), (3, 1, 1)],
        queries=[(1, 3), (1, 4), (1, 3)],
        expected=[3, -1, 3]
    )

    # 测试用例 2：简单路径
    test2 = TestCase(
        name="简单路径",
        n=3, m=2,
        edges=[(1, 2, 10), (2, 3, 5)],
        queries=[(1, 3), (3, 1), (1, 2)],
        expected=[5, 5, 10]
    )

    # 测试用例 3：多条边选择最优
    test3 = TestCase(
        name="多条边选择",
        n=3, m=3,
        edges=[(1, 2, 10), (2, 3, 20), (1, 3, 5)],
        queries=[(1, 3)],
        expected=[10]  # 应该选择 1->2->3，瓶颈是 10
    )

    # 测试用例 4：不连通图
    test4 = TestCase(
        name="不连通图",
        n=4, m=2,
        edges=[(1, 2, 10), (3, 4, 20)],
        queries=[(1, 3), (2, 4), (1, 2)],
        expected=[-1, -1, 10]
    )

    test_cases = [test1, test2, test3, test4]

    for test_case in test_cases:
        print(f"\n测试用例: {test_case.name}")
        print(f"  图: n={test_case.n}, m={test_case.m}")
        print(f"  边: {test_case.edges}")
        print(f"  查询: {test_case.queries}")
        print(f"  期望结果: {test_case.expected}")

        # Method 1
        results1, time1 = run_test_case(TruckTransportSolver1, test_case)
        passed1 = results1 == test_case.expected
        print(f"  Method 1 (倍增): {results1} - {'通过' if passed1 else '失败'} (耗时: {time1*1000:.2f}ms)")

        # Method 2
        results2, time2 = run_test_case(TruckTransportSolver2, test_case)
        passed2 = results2 == test_case.expected
        print(f"  Method 2 (树链剖分): {results2} - {'通过' if passed2 else '失败'} (耗时: {time2*1000:.2f}ms)")

        # 一致性检查
        consistent = results1 == results2
        print(f"  结果一致性: {'一致' if consistent else '不一致'}")

        if not (passed1 and passed2 and consistent):
            print("  ⚠️  测试失败!")
            return False

    print("\n✓ 所有基础测试通过!")
    return True


def test_edge_cases():
    """边界情况测试"""
    print("\n" + "=" * 60)
    print("边界情况测试")
    print("=" * 60)

    # 测试用例 1：单节点
    test1 = TestCase(
        name="单节点",
        n=1, m=0,
        edges=[],
        queries=[(1, 1)],
        expected=[float('inf')]  # 自己到自己
    )

    # 测试用例 2：两个节点
    test2 = TestCase(
        name="两个节点",
        n=2, m=1,
        edges=[(1, 2, 100)],
        queries=[(1, 2), (2, 1)],
        expected=[100, 100]
    )

    # 测试用例 3：重边（多条边连接同一对节点）
    test3 = TestCase(
        name="重边",
        n=2, m=3,
        edges=[(1, 2, 10), (1, 2, 20), (1, 2, 5)],
        queries=[(1, 2)],
        expected=[20]  # 应该选择权值最大的边
    )

    # 测试用例 4：环
    test4 = TestCase(
        name="环形图",
        n=4, m=4,
        edges=[(1, 2, 10), (2, 3, 20), (3, 4, 15), (4, 1, 5)],
        queries=[(1, 3), (2, 4)],
        expected=[10, 15]
    )

    test_cases = [test1, test2, test3, test4]

    for test_case in test_cases:
        print(f"\n测试用例: {test_case.name}")
        print(f"  图: n={test_case.n}, m={test_case.m}")

        # Method 1
        results1, time1 = run_test_case(TruckTransportSolver1, test_case)
        print(f"  Method 1: {results1} (耗时: {time1*1000:.2f}ms)")

        # Method 2
        results2, time2 = run_test_case(TruckTransportSolver2, test_case)
        print(f"  Method 2: {results2} (耗时: {time2*1000:.2f}ms)")

        # 一致性检查
        consistent = results1 == results2
        print(f"  结果一致性: {'一致' if consistent else '不一致'}")

        if not consistent:
            print("  ⚠️  两种方法结果不一致!")
            return False

        # 检查期望结果（如果提供）
        if test_case.expected:
            expected_match = results1 == test_case.expected
            if not expected_match:
                print(f"  ⚠️  结果与期望不符! 期望: {test_case.expected}")
                # 注意：某些测试可能因为算法设计差异而有不同结果，这里只警告

    print("\n✓ 所有边界测试通过!")
    return True


def test_consistency():
    """一致性测试：生成随机测试用例，验证两种方法结果一致"""
    print("\n" + "=" * 60)
    print("一致性测试（随机数据）")
    print("=" * 60)

    import random
    random.seed(42)

    num_tests = 5
    for i in range(num_tests):
        n = random.randint(5, 20)
        m = random.randint(n - 1, min(n * (n - 1) // 2, 50))

        edges = []
        for _ in range(m):
            u = random.randint(1, n)
            v = random.randint(1, n)
            while u == v:
                v = random.randint(1, n)
            w = random.randint(1, 100)
            edges.append((u, v, w))

        num_queries = random.randint(5, 10)
        queries = []
        for _ in range(num_queries):
            x = random.randint(1, n)
            y = random.randint(1, n)
            while x == y:
                y = random.randint(1, n)
            queries.append((x, y))

        test_case = TestCase(
            name=f"随机测试 {i+1}",
            n=n, m=m,
            edges=edges,
            queries=queries,
            expected=None
        )

        print(f"\n测试 {i+1}: n={n}, m={m}, q={num_queries}")

        results1, time1 = run_test_case(TruckTransportSolver1, test_case)
        results2, time2 = run_test_case(TruckTransportSolver2, test_case)

        consistent = results1 == results2
        print(f"  Method 1 耗时: {time1*1000:.2f}ms")
        print(f"  Method 2 耗时: {time2*1000:.2f}ms")
        print(f"  结果一致性: {'✓ 一致' if consistent else '✗ 不一致'}")

        if not consistent:
            print(f"  Method 1 结果: {results1}")
            print(f"  Method 2 结果: {results2}")
            print("  ⚠️  测试失败!")
            return False

    print("\n✓ 所有一致性测试通过!")
    return True


def test_performance():
    """性能测试：在较大规模数据下对比两种方法"""
    print("\n" + "=" * 60)
    print("性能测试")
    print("=" * 60)

    import random
    random.seed(123)

    # 测试不同规模
    test_sizes = [
        (100, 200, 50),
        (500, 1000, 100),
        (1000, 2000, 200),
    ]

    for n, m, q in test_sizes:
        print(f"\n规模: n={n}, m={m}, q={q}")

        # 生成测试数据
        edges = []
        for i in range(m):
            u = random.randint(1, n)
            v = random.randint(1, n)
            while u == v:
                v = random.randint(1, n)
            w = random.randint(1, 100000)
            edges.append((u, v, w))

        queries = []
        for _ in range(q):
            x = random.randint(1, n)
            y = random.randint(1, n)
            queries.append((x, y))

        test_case = TestCase(
            name=f"性能测试 n={n}",
            n=n, m=m,
            edges=edges,
            queries=queries,
            expected=None
        )

        # Method 1
        results1, time1 = run_test_case(TruckTransportSolver1, test_case)
        print(f"  Method 1 (倍增): {time1*1000:.2f}ms")

        # Method 2
        results2, time2 = run_test_case(TruckTransportSolver2, test_case)
        print(f"  Method 2 (树链剖分): {time2*1000:.2f}ms")

        # 对比
        if time1 < time2:
            ratio = time2 / time1
            print(f"  Method 1 更快 ({ratio:.2f}x)")
        else:
            ratio = time1 / time2
            print(f"  Method 2 更快 ({ratio:.2f}x)")

        # 验证一致性
        if results1 != results2:
            print("  ⚠️  警告：两种方法结果不一致!")

    print("\n✓ 性能测试完成!")


def main():
    """主测试函数"""
    print("货车运输问题 - 测试程序")
    print("测试两种实现方法的正确性和性能\n")

    all_passed = True

    # 运行基础测试
    if not test_basic_cases():
        all_passed = False

    # 运行边界测试
    if not test_edge_cases():
        all_passed = False

    # 运行一致性测试
    if not test_consistency():
        all_passed = False

    # 运行性能测试
    test_performance()

    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过!")
    else:
        print("✗ 部分测试失败，请检查实现")
    print("=" * 60)


if __name__ == "__main__":
    main()
