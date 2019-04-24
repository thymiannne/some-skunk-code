#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# https://code.google.com/codejam/contest/11274486/dashboard#s=p3

import itertools
import functools


class Card:
    """カードのクラス
    使ってないメソッドも割りとある
    """

    def __init__(self):
        self.max_level = 1  # 最大のレベル
        self.current_level = 1  # 現在のレベル
        self.attacks = [None]  # 各レベルの攻撃力
        self.costs = []  # 各レベルでのレベルアップのためのコスト
        self.cumulative_costs = [0]  # 現在のレベルから各レベルになるまでの累積コスト

    def accumulate(self):
        self.cumulative_costs = [0] * self.current_level + list(
            itertools.accumulate(self.costs[self.current_level - 1:]))

    def get_attack(self):
        return self.attacks[self.current_level - 1]

    def get_cost(self):
        return self.cumulative_costs[self.current_level - 1]

    def is_reached(self):
        if self.current_level == self.max_level:
            return True
        else:
            return False

    def level_up(self, m):
        if self.current_level < self.max_level:
            m -= self.costs[self.current_level - 1]
            self.current_level += 1
        return m


def full_search(m, cards):
    """全探索。使い物にならない。
    """
    levels = (range(card.current_level, card.max_level + 1) for card in cards)
    naives = itertools.product(*levels)
    strongest = 0
    for naive in naives:
        cost = sum(card.cumulative_costs[naive[i] - 1] for i, card in enumerate(cards))
        if cost > m:
            continue
        force = sum(card.attacks[naive[i] - 1] for i, card in enumerate(cards))
        if force > strongest:
            strongest = force
    return strongest


def knapsack(m, cards):
    """容量（この問題においてはコスト）が膨大なため、動的計画法は逆に使わない方が良い。
    ただし、smallなら解ける規模なので一応やってみる。
    この問題はどちらかというと0-1ナップザック問題なので、メモは2次元配列となる。（個数無限なら1次元でいい）
    """
    memo = [[0 for j in range(m + 1)] for i in range(8 + 1)]
    # i番目までのカードを使っていい場合ごとに、j個のコインで得られる攻撃力の最大値を記録する配列
    for i in range(8):
        le = cards[i].current_level  # カードの元々のレベルを記録する
        for coin in range(m + 1):
            cards[i].current_level = cards[i].max_level  # カードのレベルを最大にする
            cand = []  # i番目のカードがそれぞれのレベルで貢献するパワーの集合
            while cards[i].current_level >= le:  # カードが元々のレベルになるまで
                if coin - cards[i].get_cost() >= 0 and \
                        memo[i][coin] < memo[i][coin - cards[i].get_cost()] + cards[i].get_attack():
                    cand += [memo[i][coin - cards[i].get_cost()] + cards[i].get_attack()]
                cards[i].current_level -= 1  # レベル一つ下げる
            memo[i + 1][coin] = max(cand)  # メモ更新
    return memo[-1][-1]  # これは「m枚のコインで8枚全てのカードを使って得られる攻撃力の最大値」まさに答え


def meet_in_the_middle(m, cards):
    """中間一致攻撃（？？？）
    なんでも中間一致攻撃とやらを行えばlargeも解けるらしい。(とけた)
    中間一致攻撃とは、ある合成関数 g(f(x)) について、f(x_1) = g^-1(x_2) となるようなx_1, x_2 を見つける手法らしい。
    この問題の場合、関数gは「4枚のカード2組の合計値」、
    関数fは「4枚のカードについて、引数となるコインの枚数から得られる攻撃力の最大値」に相当するのだろうか。
    fに相当する部分はそれぞれmake_map()に渡して辞書型で作っている。

    8枚のカードからどのように4枚ずつに分けるかは単純に順番通りに区切るのでOKで、分け方を全通り試す必要もない。
    どうやら、8枚のカードを「必ず全て使う」ことがキモになっている感じがする
    また、2枚ずつに区切るとか1枚ずつ区切るみたいな分割統治法めいた手法も考えられるが、
    その場合コストの分配の組み合わせが複数通り生じてしまい、それはそれで計算量が大きくなる。
    4枚ずつに分ければ、片方にかけるコストを決めればもう片方にかけられるコストも一意に決まるというのが地味にデカい

    実行時間はC++で2分らしいが、pythonだと1時間越え…そもそもpythonを使うのが間違いな可能性が高い
    分枝限定法とか使えばもっと早く解けそう
    あと「中間一致攻撃　ナップザック問題」とかでググっても何も出てこないんですがそれは
    """
    # assert len(cards) == 8
    first_cards, second_cards = cards[:4], cards[4:]
    first_map = make_map(m, first_cards)
    second_map = make_map(m, second_cards)
    comb = sorted(second_map.items())  # 順序付けのためにタプルのリストにしてソートする
    length = len(comb)
    power = 0
    for first_key in first_map.keys():  # first_keyの意味は「前半4枚のカードにコインをfirst_keyだけ使う」
        power_cand = first_map[first_key]  # 前半4枚のカードの攻撃力を入れる
        second_key = m - first_key  # 後半4枚のカードにはコインをsecond_keyだけ使える
        if second_map.get(second_key) is None:
            # こっから二分探索
            lower = 0  # second_mapのキーのうち、second_key以下で一番近いやつを求めたい
            upper = length  # len(comb) - 1 だとなんかうまくいかない
            while upper - lower > 1:  # 2つが隣り合うまで
                middle = (upper + lower) // 2
                if comb[middle][0] > second_key:
                    upper = middle
                else:
                    lower = middle
            power_cand += comb[lower][1]  # 後半4枚のカードの攻撃力を足す
        else:
            power_cand += second_map[second_key]
        if power_cand > power:
            power = power_cand
    return power


def make_map(m, cards):
    """コインの数をキー、そのコインで得られる最大の攻撃力を値にした辞書を返す関数。
    """
    # assert len(cards) == 4
    the_map = {}
    levels = (range(card.current_level, card.max_level + 1) for card in cards)  # 各カードの取り得るレベルの幅
    naives = itertools.product(*levels)  # レベルの組み合わせを出すジェネレータを作ってる *()はタプルのアンパック
    for naive in naives:
        cost = sum(card.cumulative_costs[naive[i] - 1] for i, card in enumerate(cards))
        if cost > m:
            continue
        power = sum(card.attacks[naive[i] - 1] for i, card in enumerate(cards))
        if the_map.get(cost) is None:  # dictのgetメソッドはエラー回避できるからオススメ
            the_map[cost] = power
        elif power > the_map[cost]:
            the_map[cost] = power

    keys = sorted(the_map.keys())
    for i, key in enumerate(keys):  # コインの枚数が少ない方から順に
        if i == 0:
            continue
        if the_map[key] < the_map[keys[i - 1]]:  # より少ないコインで高い攻撃力を得られるのがあれば更新
            the_map[key] = the_map[keys[i - 1]]
    return the_map


def select(m, cards):
    """8～12枚のカードから8枚のカードを選ぶ
    12枚のとき、12C8 = 495回行う
    """
    selected_cards = itertools.combinations(cards, 8)
    return max(meet_in_the_middle(m, selected_card) for selected_card in selected_cards)


def answer(input_file_name, output_file_name):
    with open(input_file_name) as input_file, open(output_file_name, 'w') as output_file:
        t = int(next(input_file))
        for case_number in range(1, t + 1):
            print(f'solving Case #{case_number}...')
            m, n = map(int, next(input_file).split())
            cards = [Card() for _ in range(n)]
            for card in cards:
                card.max_level, card.current_level = map(int, next(input_file).split())
                card.attacks = list(map(int, next(input_file).split()))
                card.costs = list(map(int, next(input_file).split()))
                card.accumulate()
            # output_file.write(f'Case #{case_number}: {knapsack(m, cards)}\n')  # small用
            output_file.write(f'Case #{case_number}: {select(m, cards)}\n')


if __name__ == '__main__':
    # answer('clash_tiny.in', 'clash_tiny.out')
    answer('clash-small-practice.in', 'clash-small-practice.out')
    answer('clash-large-practice.in', 'clash-large-practice.out')
