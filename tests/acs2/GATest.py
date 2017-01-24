import unittest
from alcs.agent.acs2 import Classifier
from alcs.agent.acs2.GA import _should_fire, _apply_crossover


class GATest(unittest.TestCase):

    def setUp(self):
        self.cl1 = __class__._create_classifier(tga=0, num=1)
        self.cl2 = __class__._create_classifier(tga=0, num=1)
        self.cl3 = __class__._create_classifier(tga=12, num=1)
        self.cl4 = __class__._create_classifier(tga=8, num=2)
        self.cl5 = __class__._create_classifier(tga=11, num=1)

    def test_should_not_fire_ga_at_the_beginning(self):
        action_set = [self.cl1, self.cl2]
        for time in range(5):
            self.assertFalse(_should_fire(action_set, time, theta_ga=100))

    def test_should_fire_ga(self):
        action_set = [self.cl3, self.cl4, self.cl5]
        self.assertTrue(_should_fire(action_set, 200, theta_ga=40))

    def test_should_apply_crossover(self):
        cl1 = Classifier()
        cl2 = Classifier()

        for _ in range(1000):
            cl1.condition = ['1', '1', '1', '1']
            cl2.condition = ['2', '2', '2', '2']

            _apply_crossover(cl1, cl2)

            self.assertNotEqual(cl1.condition, cl2.condition)

    @staticmethod
    def _create_classifier(tga: int, num: int):
        cl = Classifier()

        cl.tga = tga
        cl.num = num

        return cl