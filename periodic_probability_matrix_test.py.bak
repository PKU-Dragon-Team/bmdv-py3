#!/usr/bin/env python
# encoding: utf-8

import unittest
import periodic_probability_matrix as ppm


class PpmTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def print_result(self, matrix):
        for location, row in matrix.items():
            print location
            print ' '.join(map(lambda x: '%.3f' % x, row))

    def test_get_time_interval(self):
        self.assertEqual(ppm.get_time_interval('20131229000000', '20131229062222'), (0, 12))
        self.assertEqual(ppm.get_time_interval('20131229000000', '20131229061222'), (0, 11))
        self.assertEqual(ppm.get_time_interval('20131229200000', '20131229234222'), (40, 46))
        self.assertEqual(ppm.get_time_interval('20131229203100', '20131229234222'), (41, 46))
        self.assertEqual(ppm.get_time_interval('20131229204900', '20131229234222'), (42, 46))

    def test_generate_matrix(self):
        data = [
            {
                "date": "01",
                "locations": [
                    {
                        "duration": 423.26666666666665,
                        "start_time": "20131201001835",
                        "end_time": "20131201072151",
                        "location": "116.21832 40.02880"
                    },
                    {
                        "duration": 513.2166666666667,
                        "start_time": "20131201095115",
                        "end_time": "20131201182428",
                        "location": "116.35075 39.92321"
                    },
                    {
                        "duration": 241.7,
                        "start_time": "20131201194838",
                        "end_time": "20131201235020",
                        "location": "116.21863 40.01969"
                    }
                ]
            },
            {
                "date": "02",
                "locations": [
                    {
                        "duration": 442.23333333333335,
                        "start_time": "20131202000048",
                        "end_time": "20131202072302",
                        "location": "116.21863 40.01969"
                    },
                    {
                        "duration": 602.3333333333334,
                        "start_time": "20131202091812",
                        "end_time": "20131202192032",
                        "location": "116.34819 39.92131"
                    }
                ]
            }
        ]

        expected = {'116.35075 39.92321': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '116.34819 39.92131': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0], '116.21832 40.02880': [0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '116.21863 40.01969': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]}
        returned = ppm.generate_matrix(data)
        self.assertEqual(returned, expected)

if __name__ == '__main__':
    unittest.main()
