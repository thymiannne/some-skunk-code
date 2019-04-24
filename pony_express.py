#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# https://code.google.com/codejam/contest/8294486/dashboard#s=p2

# import networkx as nx  # ←ダメだから！！
import math


class Graph:
    def __init__(self):
        self.vertex = set()
        self.edge = {}

    def __repr__(self):
        return f'Graph vertices: {self.vertex}, edges: {self.edge}'

    def add_edge(self, tail, head, weight):
        if tail != head:  # self loop排除
            self.vertex.add(tail)
            self.vertex.add(head)
            self.edge[(tail, head)] = weight

    def add_weighted_edges_from(self, weights):
        for weight in weights:
            self.add_edge(*weight)


def dijkstra(G: Graph, source: int) -> dict:
    """気が向いたらいずれnxに頼らずこれに置き換えたい。→置き換えました。
    """
    adjacent = {v: [] for v in G.vertex}
    for edge in G.edge.keys():
        tail, head = edge
        adjacent[tail] += [head]
    distance = {v: math.inf for v in G.vertex}  # 最短路長distanceは辞書で出力することにする．
    distance[source] = 0  # 始点そのものへの最短路長は0である．
    vertices = list(G.vertex.copy())  # 集合（リスト）Uに頂点集合をコピーする．
    while vertices:
        minimum_of_d = math.inf
        v = vertices[0]
        for u in vertices:
            if distance[u] < minimum_of_d:
                v = u
                minimum_of_d = distance[v]
        vertices.remove(v)
        for w in adjacent[v]:
            if distance[w] > distance[v] + G.edge[(v, w)]:
                distance[w] = distance[v] + G.edge[(v, w)]
    return distance


def construct_graph(array: list, n: int) -> Graph:
    """arrayからグラフを生成する
    """
    # G = nx.DiGraph()  # アウト
    G = Graph()
    for i in range(n):
        for j in range(n):
            if array[i][j] != -1:
                G.add_edge(i, j, weight=array[i][j])
    return G


def pony_express(G: Graph, horses: list, mails: list) -> str:
    """
    手順としては、Bellman-Fordアルゴリズムで全点間最短距離を求めてから、各枝について
    始点の馬の到達できる最大距離以内であれば、その距離を始点の馬の速さで割り、
    その割った値を枝の重さに持つ新たなグラフを構築する。
    そしてそのグラフに対し、届けるメールの出発地・目的地ごとにDijkstra法で最短時間を求める。
    勿論networkxライブラリの使用は反則。
    :param G: 町のグラフ
    :param horses: 各町が持つ馬
    :param mails: 各メールの出発地と目的地
    :return: 最短時間

    """
    shortest_paths = {source: dijkstra(G, source) for source in G.vertex}
    # shortest_paths = dict(nx.all_pairs_bellman_ford_path_length(G))  # TODO: nxを使わない
    weights = []
    for i in shortest_paths.keys():
        duration, speed = horses[i]
        for j in shortest_paths[i].keys():
            if shortest_paths[i][j] <= duration:
                weight = (i, j, shortest_paths[i][j] / speed)
                weights.append(weight)

    # H = nx.DiGraph()
    H = Graph()
    H.add_weighted_edges_from(weights)

    times = []
    for mail in mails:
        source, target = mail
        # time = nx.dijkstra_path_length(H, source - 1, target - 1)  # TODO: nxを使わない
        time_dict = dijkstra(H, source - 1)
        time = time_dict[target - 1]
        times.append(time)
    return ' '.join(map(str, times))


def answer(input_file_name, output_file_name):
    with open(input_file_name) as input_file, open(output_file_name, 'w') as output_file:
        T = int(next(input_file))
        for case_number in range(1, T + 1):
            print(f'Solving Case #{case_number}...')
            n, q = map(int, next(input_file).split())
            horses = [tuple(map(int, next(input_file).split())) for i in range(n)]
            array = [list(map(int, next(input_file).split())) for i in range(n)]
            mails = [tuple(map(int, next(input_file).split())) for i in range(q)]
            G = construct_graph(array, n)
            output_file.write(f'Case #{case_number}: {pony_express(G, horses, mails)}\n')


if __name__ == '__main__':
    answer('pony-small-practice.in', 'pony-small-practice.out')
    answer('pony-large-practice.in', 'pony-large-practice.out')
