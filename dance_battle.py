#!/usr/bin/env python
# -*- coding: utf-8 -*-


def dance_battle(energy: int, rivals: list) -> int:
    honor = 0
    while rivals:
        rivals.sort()  # delay
        win = list(filter(lambda x: energy > x, rivals))
        lose = list(filter(lambda x: energy <= x, rivals))
        if len(win) > 0:  # dance
            energy -= rivals.pop(0)
            honor += 1
        elif honor > 0 and len(lose) >= 2:  # recruit
            energy += rivals.pop()
            honor -= 1
        else:  # truce
            break
    return honor


def answer(input_file_name, output_file_name):
    with open(input_file_name) as input_file, open(output_file_name, 'w') as output_file:
        t = int(next(input_file))
        for case_number in range(1, t + 1):
            energy, n = map(int, next(input_file).split())
            rivals = list(map(int, next(input_file).split()))
            assert len(rivals) == n, "ライバルの数違くね？"
            output_file.write(f'Case #{case_number}: {dance_battle(energy, rivals)}\n')


if __name__ == '__main__':
    answer('dance-small-practice.in', 'dance-small-practice.out')
    answer('dance-large-practice.in', 'dance-large-practice.out')
