#!/usr/bin/env python
# encoding: utf-8

from db import MySQL as DB
from batch_common import fetch_user_location_logs
from batch_common import dbconfig
from batch_common import fetch_users
from merge_locations import merge_locations
from periodic_probability_matrix import generate_matrix
from tag_config import clean_tags
from app import fetch_semantic_data
import sys
import json
from csv import DictWriter
import sys

reload(sys)
exec("sys.setdefaultencoding('utf-8')");


def run():
    output = open(sys.argv[1], 'w')
    writer = DictWriter(output, fieldnames=['uid', 'data'])
    writer.writeheader()
    db = DB(dbconfig)

    for uid in fetch_users(db):
        data = fetch_user_location_logs(uid, db)
        locations = merge_locations(data)
        matrix = generate_matrix(locations)
        semantic_data = fetch_semantic_data(matrix.keys())
        semantic_dict = {}
        for row in semantic_data:
            semantic_dict[row['location']] = clean_tags(row['tags'], 5)
        tag_matrix = {}
        for location, proba in matrix.items():
            tag_dict = semantic_dict[location]
            tag_weight = sum(v for v in tag_dict.values())
            if tag_weight == 0:
                continue
            for tag, cnt in tag_dict.items():
                tag_matrix.setdefault(tag, [0] * 48)
                for i in range(48):
                    tag_matrix[tag][i] += (proba[i] * cnt + 0.001) / (tag_weight + 0.001)
        writer.writerow({
            'uid': uid,
            'data': json.dumps(tag_matrix)
        })
    output.close()


if __name__ == '__main__':
    run()
