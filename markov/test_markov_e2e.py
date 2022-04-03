import random
import unittest

from markov import cronuts, markov


class TestMarkovE2e(unittest.TestCase):
    def test_markov_e2e(self):
        random.seed(9)
        graph = markov.Graph()
        graph.add_node(
            "Play", ["offense"], ["turn-over", "score-one", "score-two", "score-three"]
        )
        graph.add_action("turn-over", cronuts.turn_over)  # functions turn_over, etc. defined elsewhere
        graph.add_action("score-one", cronuts.score_one)
        graph.add_action("score-two", cronuts.score_two)
        graph.add_action("score-three", cronuts.score_three)
        graph.add_action("tip-off", cronuts.tip_off)

        graph.train(cronuts.data)
        actual = markov.sims(graph, teams=["duke", "north-carolina"], num_sims=100)
        expected = {'duke': 0.25, 'north-carolina': 0.73}
        self.assertEqual(actual, expected)
