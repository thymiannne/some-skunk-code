#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# https://code.google.com/codejam/contest/11274486/dashboard#s=p1

from copy import deepcopy


def solve_rain(R, C, height):
    adjacent_vertex = {}
    for i in range(R):
        for j in range(C):
            adjacent_vertex[(i, j)] = neighbor(i, j, R, C)
    water = flood(R, C, height, adjacent_vertex)
    difference = sum(sum(water[i][j] - height[i][j] for j in range(C)) for i in range(R))
    return difference


def neighbor(i, j, R, C):
    """各地点の隣接地点を渡す関数。
    """
    if i in range(1, R - 1) and j in range(1, C - 1):
        neighbor_point = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
    elif i == 0 and j in range(1, C - 1):
        neighbor_point = [(i + 1, j)]
    elif i == R - 1 and j in range(1, C - 1):
        neighbor_point = [(i - 1, j)]
    elif i in range(1, R - 1) and j == 0:
        neighbor_point = [(i, j + 1)]
    elif i in range(1, R - 1) and j == C - 1:
        neighbor_point = [(i, j - 1)]
    else:
        neighbor_point = []
    return neighbor_point


def flood(R, C, height, adjacent_vertex):
    water = deepcopy(height)  # 二次元配列はcopyモジュールのdeepcopyを使わないと完全にコピーできない。pythonはここがクソ
    heights = set()  # 重複を消すためにまずセット型で高さの集合を定義
    for r in range(1, R - 1):
        for c in range(1, C - 1):
            heights.add(water[r][c])
    heights = sorted(heights)  # 昇順ソートでリストに直す
    for h in heights:
        dfs(water, h, adjacent_vertex, R, C)
    return water


def dfs(water, h, adjacent_vertex, R, C):
    """与えられたhの高さである座標を、深さ優先探索で結合し、その結合部分（湖と呼ぶ）の隣接部分（岸と呼ぶ）を見て、
    岸の高さの最小値がhより小さければその岸の最小値に湖の高さを更新する、という処理を行っている。
    """
    already = {}  # 与えられたhの高さである座標をキー、探索済みかどうかのbool代数を値に持つ辞書を作成
    for key in adjacent_vertex.keys():
        r, c = key
        if water[r][c] == h and r in range(1, R - 1) and c in range(1, C - 1):  # 島の内部でかつ高さがhなら
            already[key] = False  # 辞書に加える。初期値はFalse

    for key in already.keys():
        if not already[key]:
            neighbors = []  # 岸の高さの集合を表すリスト
            connected_component = [key]  # 結合部分（湖）のリスト。最初にkeyを入れる
            stack = [key]  # スタック　最初にkeyを入れる
            already[key] = True  # keyは探索済みになる
            while stack:  # スタックが空でない限り
                v = stack.pop()
                for w in adjacent_vertex[v]:
                    if w not in connected_component:  # wが（まだ）湖に入っておらず、
                        if w in already.keys():  # 更に高さhを持つとき
                            connected_component += [w]  # 湖に追加する
                            stack += [w]  # スタックに追加
                            already[w] = True  # wは探索済みになる
                        else:  # 逆に高さhを持たないとき
                            neighbors += [water[w[0]][w[1]]]  # 岸に追加する
            if min(neighbors) > h:  # 湖の岸の最大値がhより大きければ
                for point in connected_component:
                    water[point[0]][point[1]] = min(neighbors)  # 湖の高さを岸の最小値に更新


def answer0(input_file_name, output_file_name):
    with open(input_file_name) as input_file, open(output_file_name, 'w') as output_file:
        T = int(next(input_file))
        for case_number in range(1, T + 1):
            print(f'solving Case #{case_number}...')
            R, C = map(int, next(input_file).split())
            height = [list(map(int, next(input_file).split())) for r in range(R)]
            output_file.write(f'Case #{case_number}: {solve_rain(R, C, height)}\n')


if __name__ == '__main__':
    # print(solve_rain(3, 3, [[3, 5, 5], [5, 4, 5], [5, 5, 5]]))
    # print(solve_rain(4, 4, [[5, 5, 5, 1], [5, 1, 1, 5], [5, 1, 5, 5], [5, 2, 5, 8]]))
    # print(solve_rain(4, 3, [[2, 2, 2], [2, 1, 2], [2, 1, 2], [2, 1, 2]]))
    answer0('rain-small-practice.in', 'rain-small-practice.out')
    answer0('rain-large-practice.in', 'rain-large-practice.out')
