#!/usr/bin/env python
# encoding: utf-8


def get_most_proba_locations(matrix):
    n = len(matrix[matrix.keys()[0]])
    total_probas = [sum([row[i] for row in matrix.values()]) for i in range(n)]
    t = 0.3
    thresholds = [proba / 2 if proba > t else 2 for proba in total_probas]
    most_proba_locations = [[location for location, row in matrix.items() if row[i] >= thresholds[i]] for i in range(n)]
    return most_proba_locations


def pretty_print_most_proba_locations(most_proba_locations):
    result = []
    n = len(most_proba_locations)
    start_idx = None
    start_locations = None
    for i in range(n):
        if start_locations is not None and start_locations != most_proba_locations[i]:
            result.append({
                'range': [start_idx + 1, i],
                'locations': start_locations
            })
            start_idx = None
            start_locations = None

        if start_idx is None and most_proba_locations[i] != []:
            start_idx = i
            start_locations = most_proba_locations[i]

    if start_idx is not None:
        result.append({
            'range': [start_idx + 1, n],
            'locations': start_locations
        })

    return result



