import pytest

from lcs import Perception
from lcs.agents.acs2 import Configuration, Classifier, \
    Condition, Effect


class TestClassifier:

    @pytest.fixture
    def cfg(self):
        return Configuration(8, 8)

    def test_equality(self, cfg):
        # given
        cl = Classifier(action=1, numerosity=2, cfg=cfg)

        # when & then
        assert Classifier(action=1, numerosity=2, cfg=cfg) == cl

    def test_should_calculate_fitness(self, cfg):
        # given
        cls = Classifier(reward=0.25, cfg=cfg)

        # then
        assert 0.125 == cls.fitness

    def test_should_anticipate_change(self, cfg):
        # given
        cls = Classifier(cfg=cfg)
        assert cls.does_anticipate_change() is False

        # when
        cls.effect[1] = '1'

        # then
        assert cls.does_anticipate_change() is True

    def test_should_anticipate_correctly(self, cfg):
        # given
        cls = Classifier(
            effect='#1####0#',
            cfg=cfg)
        p0 = Perception('00001111')
        p1 = Perception('01001101')

        # then
        assert cls.does_anticipate_correctly(p0, p1) is True

    def test_should_calculate_specificity_1(self, cfg):
        cls = Classifier(cfg=cfg)
        assert 0 == cls.specificity

    def test_should_calculate_specificity_2(self, cfg):
        # given
        cls = Classifier(
            condition=Condition('#1#01#0#'),
            cfg=cfg)

        # then
        assert 0.5 == cls.specificity

    def test_should_calculate_specificity_3(self, cfg):
        # given
        cls = Classifier(
            condition=Condition('11101001'),
            cfg=cfg)

        # then
        assert 1 == cls.specificity

    def test_should_be_considered_as_reliable_1(self, cfg):
        # given
        cls = Classifier(quality=0.89, cfg=cfg)

        # then
        assert cls.is_reliable() is False

    def test_should_be_considered_as_reliable_2(self, cfg):
        # given
        cls = Classifier(quality=0.91, cfg=cfg)

        # then
        assert cls.is_reliable() is True

    def test_should_be_considered_as_inadequate_1(self, cfg):
        # given
        cls = Classifier(quality=0.50, cfg=cfg)

        # then
        assert cls.is_reliable() is False

    def test_should_be_considered_as_inadequate_2(self, cfg):
        # given
        cls = Classifier(quality=0.09, cfg=cfg)

        # then
        assert cls.is_inadequate() is True

    def test_should_update_reward(self, cfg):
        # given
        cls = Classifier(cfg=cfg)

        # when
        cls.update_reward(1000)

        # then
        assert 50.475 == cls.r

    def test_should_update_intermediate_reward(self, cfg):
        # given
        cls = Classifier(cfg=cfg)

        # when
        cls.update_intermediate_reward(1000)

        # then
        assert 50.0 == cls.ir

    def test_should_increase_experience(self, cfg):
        # given
        cls = Classifier(experience=5, cfg=cfg)

        # when
        cls.increase_experience()

        # then
        assert 6 == cls.exp

    def test_should_increase_quality(self, cfg):
        # given
        cls = Classifier(quality=0.5, cfg=cfg)

        # when
        cls.increase_quality()

        # then
        assert 0.525 == cls.q

    def test_should_decrease_quality(self, cfg):
        # given
        cls = Classifier(quality=0.47, cfg=cfg)

        # when
        cls.decrease_quality()

        # then
        assert abs(0.45 - cls.q) < 0.01

    def test_should_detect_correct_anticipation_1(self, cfg):
        # Classifier is not predicting any change, all pass-through effect
        # should predict correctly

        # given
        cls = Classifier(effect=Effect('########'), cfg=cfg)
        p0 = Perception('00001111')
        p1 = Perception('00001111')

        # then
        assert cls.does_anticipate_correctly(p0, p1) is True

    def test_should_detect_correct_anticipation_2(self, cfg):
        # Introduce two changes into situation and effect (should
        # also predict correctly)

        # given
        cls = Classifier(
            effect=Effect(['#', '1', '#', '#', '#', '#', '0', '#']),
            cfg=cfg)
        p0 = Perception(['0', '0', '0', '0', '1', '1', '1', '1'])
        p1 = Perception(['0', '1', '0', '0', '1', '1', '0', '1'])

        # then
        assert cls.does_anticipate_correctly(p0, p1) is True

    def test_should_detect_correct_anticipation_3(self, cfg):
        # Case when effect predicts situation incorrectly

        # given
        cls = Classifier(
            effect=Effect(['#', '0', '#', '#', '#', '#', '#', '#']),
            cfg=cfg)
        p0 = Perception(['0', '0', '0', '0', '1', '1', '1', '1'])
        p1 = Perception(['0', '1', '0', '0', '1', '1', '1', '1'])

        # then
        assert cls.does_anticipate_correctly(p0, p1) is False

    def test_should_detect_correct_anticipation_4(self, cfg):
        # Case when effect predicts situation incorrectly

        # given
        cls = Classifier(
            effect=Effect(['#', '#', '0', '#', '#', '1', '#', '#']),
            cfg=cfg)
        p0 = Perception(['1', '0', '1', '0', '1', '0', '0', '1'])
        p1 = Perception(['1', '0', '1', '0', '1', '0', '0', '1'])

        # then
        assert cls.does_anticipate_correctly(p0, p1) is False

    def test_should_detect_correct_anticipation_5(self, cfg):
        # Case when effect predicts situation incorrectly

        # given
        cls = Classifier(
            effect=Effect(['#', '#', '#', '#', '1', '#', '0', '#']),
            cfg=cfg)
        p0 = Perception(['0', '1', '1', '0', '0', '0', '1', '1'])
        p1 = Perception(['1', '1', '1', '0', '1', '1', '0', '1'])

        # then
        assert cls.does_anticipate_correctly(p0, p1) is False

    def test_should_detect_correct_anticipation_6(self, cfg):
        # Case when effect predicts situation incorrectly

        # given
        cls = Classifier(
            effect=Effect(['#', '#', '1', '#', '0', '#', '0', '#']),
            cfg=cfg)
        p0 = Perception(['0', '0', '0', '1', '1', '0', '1', '0'])
        p1 = Perception(['0', '0', '1', '1', '0', '0', '0', '0'])

        # then
        assert cls.does_anticipate_correctly(p0, p1) is True

    def test_should_handle_pass_through_symbol(self, cfg):
        # A case when there was no change in perception but effect has no
        # pass-through symbol

        # given
        cls = Classifier(
            effect=Effect(['#', '0', '#', '#', '#', '#', '#', '#']),
            cfg=cfg)
        p0 = Perception(['0', '0', '0', '0', '1', '1', '1', '1'])
        p1 = Perception(['0', '0', '0', '0', '1', '1', '1', '1'])

        # then
        assert cls.does_anticipate_correctly(p0, p1) is False

    def test_should_specialize_1(self, cfg):
        # given
        cls = Classifier(cfg=cfg)
        p0 = Perception('00001111')
        p1 = Perception('00001111')

        # when
        cls.specialize(p0, p1)

        # then
        assert Condition('########') == cls.condition
        assert Effect('########') == cls.effect

    def test_should_specialize_2(self, cfg):
        # given
        cls = Classifier(cfg=cfg)
        p0 = Perception('00001111')
        p1 = Perception('00011111')

        # when
        cls.specialize(p0, p1)

        # then
        assert Condition('###0####') == cls.condition
        assert Effect('###1####') == cls.effect

    def test_should_specialize_3(self, cfg):
        # given
        cls = Classifier(
            condition=Condition('01#####1'),
            effect=Effect('10#####0'),
            cfg=cfg)
        p0 = Perception('01110111')
        p1 = Perception('10101010')

        # when
        cls.specialize(p0, p1)

        # then
        assert 6 == cls.condition.specificity
        assert Condition('01#101#1') == cls.condition

        assert 6 == cls.effect.number_of_specified_elements
        assert Effect('10#010#0', cfg) == cls.effect

    def test_should_count_specified_unchanging_attributes_1(self, cfg):
        # given
        cls = Classifier(
            condition='######0#',
            effect='########',
            cfg=cfg
        )

        # when & then
        assert 1 == cls.specified_unchanging_attributes

    def test_should_count_specified_unchanging_attributes_2(self, cfg):
        # given
        cls = Classifier(
            condition='#####0#0',
            effect='########',
            cfg=cfg
        )

        # when & then
        assert 2 == cls.specified_unchanging_attributes

    def test_should_count_specified_unchanging_attributes_3(self, cfg):
        # given
        cls = Classifier(
            condition='10000001',
            effect='####1#1#',
            cfg=cfg
        )

        # when & then
        assert 6 == cls.specified_unchanging_attributes

    def test_should_count_specified_unchanging_attributes_4(self, cfg):
        # given
        cls = Classifier(
            condition='1#0#1011',
            effect='0####1##',
            cfg=cfg
        )
        # when & then
        assert 4 == cls.specified_unchanging_attributes

    def test_should_count_specified_unchanging_attributes_5(self, cfg):
        # given
        cls = Classifier(
            condition='1###1011',
            effect='0####1##',
            cfg=cfg
        )

        # when & then
        assert 3 == cls.specified_unchanging_attributes

    def test_copy_from_and_change_does_not_influence_another_effect(self, cfg):
        """ Verify that not just reference to Condition copied (changing which
        will change the original - definitily not original C++ code did). """
        # given
        operation_time = 123
        original_cl = Classifier(
            effect='10####1#',
            cfg=cfg)

        # when
        copied_cl = Classifier.copy_from(original_cl, operation_time)

        # when & then
        copied_cl.effect[2] = '1'
        assert Effect('101###1#') == copied_cl.effect
        assert Effect('10####1#') == original_cl.effect

        # when & then
        original_cl.effect[3] = '0'
        assert Effect('101###1#') == copied_cl.effect
        assert Effect('10#0##1#') == original_cl.effect

    def test_should_copy_classifier(self, cfg):
        # given
        operation_time = 123
        original_cl = Classifier(
            condition='1###1011',
            action=1,
            effect='10####1#',
            reward=50,
            quality=0.7,
            cfg=cfg
        )

        # when
        copied_cl = Classifier.copy_from(original_cl, operation_time)

        # Assert that we are dealing with different object
        assert original_cl is not copied_cl

        # Assert that condition is equal but points to another object
        assert original_cl.condition == copied_cl.condition
        assert original_cl.condition is not copied_cl.condition

        # Assert that action is equal
        assert original_cl.action == copied_cl.action

        # Assert that effect is equal but points to another object
        assert original_cl.effect == copied_cl.effect
        assert original_cl.effect is not copied_cl.effect

        # Assert that other properties were set accordingly
        assert copied_cl.is_marked() is False
        assert 50 == copied_cl.r
        assert 0.7 == copied_cl.q
        assert operation_time == copied_cl.tga
        assert operation_time == copied_cl.talp

    def test_should_detect_similar_classifiers_1(self, cfg):
        # given
        base = Classifier(
            condition='1###1011',
            action=1,
            effect='10####1#',
            cfg=cfg
        )

        c1 = Classifier(
            condition='1###1011',
            action=1,
            effect='10####1#',
            cfg=cfg
        )

        # when && then
        assert base.is_similar(c1) is True

    def test_similar_returns_true_if_differs_by_numbers(self, cfg):
        # given
        original = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.9,
            intermediate_reward=1.2,
            quality=0.5,
            reward=0.6,
            talp=None,
            tav=1,
            tga=2,
            cfg=cfg
        )

        c_num = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.2,
            experience=0.9,
            intermediate_reward=1.2,
            quality=0.5,
            reward=0.6,
            talp=None,
            tav=1,
            tga=2,
            cfg=cfg
        )

        c_exp = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.95,
            intermediate_reward=1.2,
            quality=0.5,
            reward=0.6,
            talp=None,
            tav=1,
            tga=2,
            cfg=cfg
        )

        c_inter = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.9,
            intermediate_reward=1.3,
            quality=0.5,
            reward=0.6,
            talp=None,
            tav=1,
            tga=2,
            cfg=cfg
        )

        c_qual = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.9,
            intermediate_reward=1.2,
            quality=1,
            reward=0.6,
            talp=None,
            tav=1,
            tga=2,
            cfg=cfg
        )

        c_rew = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.9,
            intermediate_reward=1.2,
            quality=0.5,
            reward=0.5,
            talp=None,
            tav=1,
            tga=2,
            cfg=cfg
        )

        c_talp = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.9,
            intermediate_reward=1.2,
            quality=0.5,
            reward=0.6,
            talp=1,
            tav=1,
            tga=2,
            cfg=cfg
        )

        c_tav = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.9,
            intermediate_reward=1.2,
            quality=0.5,
            reward=0.6,
            talp=None,
            tav=2,
            tga=2,
            cfg=cfg
        )

        c_tga = Classifier(
            condition='#01##10#',
            action=2,
            effect='1##01##0',
            numerosity=1.1,
            experience=0.9,
            intermediate_reward=1.2,
            quality=0.5,
            reward=0.6,
            talp=None,
            tav=1,
            tga=0,
            cfg=cfg
        )

        # then
        cls = [c_num, c_exp, c_inter, c_qual, c_rew, c_talp, c_tav, c_tga]
        for cl in cls:
            assert cl.is_similar(original) is True
            assert original.is_similar(cl) is True

    def test_should_detect_similar_classifiers_2(self, cfg):
        # given
        base = Classifier(
            condition='1###1011',
            action=1,
            effect='10####1#',
            cfg=cfg
        )

        # when & then
        # Changed condition part
        assert base.is_similar(
            Classifier(
                condition='1#1#1011',
                action=1,
                effect='10####1#',
                cfg=cfg
            )) is False

        # when & then
        # changed action part
        assert base.is_similar(
            Classifier(
                condition='1###1011',
                action=2,
                effect='10####1#',
                cfg=cfg
            )) is False

        # when & then
        # changed effect part
        assert base.is_similar(
            Classifier(
                condition='1###1011',
                action=1,
                effect='10####11',
                cfg=cfg
            )) is False

    def test_should_detect_more_general_classifier_1(self, cfg):
        # given
        cls = Classifier(cfg=cfg)
        c = Classifier(cfg=cfg)

        # when & then
        # no specified elements - should not be more general
        assert cls.is_more_general(c) is False

    def test_should_detect_more_general_classifier_2(self, cfg):
        # given
        cls = Classifier(cfg=cfg)
        c = Classifier(condition='1###1011', cfg=cfg)

        # when & then
        # Should be more general
        assert cls.is_more_general(c) is True

    def test_should_detect_more_general_classifier_3(self, cfg):
        # given
        cls = Classifier(condition='1#1#1011', cfg=cfg)
        c = Classifier(condition='1###1###', cfg=cfg)

        # when & then
        # shouldn't be more general
        assert cls.is_more_general(c) is False

    def test_should_distinguish_classifier_as_subsumer_1(self, cfg):
        # given
        cls = Classifier(cfg=cfg)

        # when & then
        # general classifier should not be considered as subsumer
        assert cls._is_subsumer() is False

    def test_should_distinguish_classifier_as_subsumer_2(self, cfg):
        # given
        # let's assign enough experience and quality
        cls = Classifier(experience=30, quality=0.92, cfg=cfg)

        # when & then
        assert cls._is_subsumer()

    def test_should_distinguish_classifier_as_subsumer_3(self, cfg):
        # given
        # let's reduce experience below threshold
        cls = Classifier(experience=15, quality=0.92, cfg=cfg)

        # when & then
        assert cls._is_subsumer() is False

    def test_should_distinguish_classifier_as_subsumer_4(self, cfg):
        # given
        # Now check if the fact that classifier is marked will block
        # it from being considered as a subsumer
        cls = Classifier(experience=30, quality=0.92, cfg=cfg)
        cls.mark[3].add('1')

        # when & then
        assert cls._is_subsumer() is False

    def test_should_subsume_another_classifier_1(self, cfg):
        # given
        cls = Classifier(quality=0.93, reward=1.35, experience=23, cfg=cfg)
        cls.condition[3] = '0'
        cls.action = 3
        cls.effect[2] = '1'

        other = Classifier(quality=0.5, reward=0.35, experience=1, cfg=cfg)
        other.condition[0] = '1'
        other.condition[3] = '0'
        other.action = 3
        other.effect[2] = '1'

        # when & then
        assert cls.does_subsume(other) is True

    def test_should_subsume_another_classifier_2(self, cfg):
        # given
        cls = Classifier(quality=0.84, reward=0.33, experience=3, cfg=cfg)
        cls.condition[0] = '1'
        cls.condition[1] = '0'
        cls.condition[4] = '0'
        cls.condition[6] = '1'
        cls.action = 6
        cls.effect[0] = '0'
        cls.effect[1] = '1'
        cls.effect[6] = '0'

        other = Classifier(quality=0.5, reward=0.41, experience=1, cfg=cfg)
        other.condition[0] = '1'
        other.condition[1] = '0'
        other.condition[6] = '2'
        other.action = 3
        other.effect[0] = '0'
        other.effect[1] = '1'
        other.effect[6] = '0'

        # when & then
        assert cls.does_subsume(other) is False

    def test_should_subsume_another_classifier_3(self, cfg):
        # Given
        cls = Classifier(quality=0.99, reward=11.4, experience=32, cfg=cfg)
        cls.condition[6] = '0'
        cls.action = 6

        other = Classifier(quality=0.5, reward=9.89, experience=1, cfg=cfg)
        other.condition[3] = '1'
        other.condition[6] = '0'
        other.action = 6

        # when & then
        assert cls.does_subsume(other) is True

    def test_should_set_mark_from_condition_1(self, cfg):
        # given
        p0 = Perception('00001111')
        cls = Classifier(condition='##0#1#1#', cfg=cfg)
        cls.mark[0].add('0')
        cls.mark[1].add('0')
        cls.mark[3].add('0')
        cls.mark[5].add('1')
        cls.mark[7].add('1')

        # when
        cls.set_mark(p0)

        # then
        assert 8 == len(cls.mark)
        assert 1 == len(cls.mark[0])  # 0
        assert 1 == len(cls.mark[1])  # 0
        assert 0 == len(cls.mark[2])
        assert 1 == len(cls.mark[3])  # 0
        assert 0 == len(cls.mark[4])
        assert 1 == len(cls.mark[5])  # 1
        assert 0 == len(cls.mark[6])
        assert 1 == len(cls.mark[7])  # 1

    def test_should_set_mark_from_condition_2(self, cfg):
        # given
        p0 = Perception('12101101')
        cls = Classifier(condition='###0#101', cfg=cfg)

        # when
        cls.set_mark(p0)

        # then
        assert 1 == len(cls.mark[0])
        assert '1' in cls.mark[0]

        assert 1 == len(cls.mark[1])
        assert '2' in cls.mark[1]

        assert 1 == len(cls.mark[2])
        assert '1' in cls.mark[2]

        assert 1 == len(cls.mark[4])
        assert '1' in cls.mark[4]

    def test_should_set_mark_from_condition_3(self, cfg):
        # given
        p0 = Perception('11111010')
        cls = Classifier(condition='11#11##0', cfg=cfg)

        # when
        cls.set_mark(p0)

        # Then
        assert 1 == len(cls.mark[2])
        assert '1' in cls.mark[2]

        assert 1 == len(cls.mark[5])
        assert '0' in cls.mark[5]

        assert 1 == len(cls.mark[6])
        assert '1' in cls.mark[6]

    def test_should_set_mark_from_condition_4(self, cfg):
        # given
        p0 = Perception('01100000')
        cls = Classifier(condition='###0###0', cfg=cfg)

        # when
        cls.set_mark(p0)

        # then
        assert 1 == len(cls.mark[0])
        assert '0' in cls.mark[0]

        assert 1 == len(cls.mark[1])
        assert '1' in cls.mark[1]

        assert 1 == len(cls.mark[2])
        assert '1' in cls.mark[2]

        assert 1 == len(cls.mark[4])
        assert '0' in cls.mark[4]

        assert 1 == len(cls.mark[5])
        assert '0' in cls.mark[5]

        assert 1 == len(cls.mark[6])
        assert '0' in cls.mark[6]

    def test_should_predict_successfully_1(self, cfg):
        # given
        action = 5
        cls = Classifier(
            condition='1#0111#1',
            action=action,
            effect='0#1000#0',
            quality=0.94,
            cfg=cfg
        )
        p0 = Perception('11011101')
        p1 = Perception('01100000')

        # then
        assert cls.predicts_successfully(p0, action, p1) is True

    def test_should_not_generalize_random_attributes(self, cfg):
        # given
        cls = Classifier(
            condition='#####0#0',
            effect='#####1#1',
            cfg=cfg)

        no_spec = cls.specified_unchanging_attributes
        assert 0 == no_spec

        # when
        generalized = cls.generalize_unchanging_condition_attribute(no_spec)

        # then
        assert generalized is False
        assert 0 == cls.specified_unchanging_attributes

    def test_should_generalize_random_attribute(self, cfg):
        # given
        cls = Classifier(
            condition='#####0#0',
            effect='#######1',
            cfg=cfg)

        no_spec = cls.specified_unchanging_attributes
        assert 1 == no_spec

        # when
        generalized = cls.generalize_unchanging_condition_attribute(no_spec)

        # then
        assert generalized is True
        assert 0 == cls.specified_unchanging_attributes

    def test_should_generalize_one_random_attribute(self, cfg):
        # given
        cls = Classifier(
            condition='#####0#0',
            effect='########',
            cfg=cfg)

        no_spec = cls.specified_unchanging_attributes
        assert 2 == no_spec

        # when
        generalized = cls.generalize_unchanging_condition_attribute(no_spec)

        # then
        assert generalized is True
        assert 1 == cls.specified_unchanging_attributes

    def test_should_generalize_second_unchanging_attribute(self, cfg):
        # given
        cls = Classifier(
            condition='#####0#0',
            effect='########',
            cfg=cfg)

        no_spec = cls.specified_unchanging_attributes
        assert 2 == no_spec

        # when
        generalized = cls.generalize_unchanging_condition_attribute(
            no_spec, lambda x, y: 1)

        # then
        assert generalized is True
        assert 1 == cls.specified_unchanging_attributes
        assert Condition('#####0##') == cls.condition