import logging
from random import random

from . import Classifier
from . import Constants as c
from .ACS2Utils import get_general_perception, remove_classifier

logger = logging.getLogger(__name__)


def apply_alp(classifiers: list,
              action: int,
              time: int,
              action_set: list,
              perception: list,
              previous_perception: list,
              theta_i: float = None):

    if theta_i is None:
        theta_i = c.THETA_I

    logger.debug('Applying ALP module')
    was_expected_case = 0

    for cl in action_set:
        cl.exp += 1
        _update_application_average(cl, time)

        if _does_anticipate_correctly(cl,
                                      perception,
                                      previous_perception):
            new_cl = _expected_case(cl, perception)
            was_expected_case = 1
        else:
            new_cl = _unexpected_case(cl,
                                      perception,
                                      previous_perception)
            if cl.q < theta_i:
                remove_classifier(classifiers, cl)
                remove_classifier(action_set, cl)

        if new_cl is not None:
            new_cl.t_ga = time
            _add_alp_classifier(new_cl,
                                classifiers,
                                action_set)

    if was_expected_case == 0:
        new_cl = _cover_triple(previous_perception,
                               perception,
                               action,
                               time)
        _add_alp_classifier(new_cl, classifiers, action_set)


def _expected_case(cl: Classifier,
                   perception: list,
                   beta: float = None,
                   u_max: int = None) -> Classifier:

    if beta is None:
        beta = c.BETA

    if u_max is None:
        u_max = c.U_MAX

    diff = _get_differences(cl.mark, perception)

    if diff == get_general_perception():
        cl.q += beta * (1 - cl.q)
        return None
    else:
        # Count number of non-# symbols in diff and condition part
        spec = _number_of_spec(cl.condition)
        spec_new = _number_of_spec(diff)

        child = Classifier.copy_from(cl)

        if spec == u_max:
            _remove_random_spec_element(child.condition)
            spec -= 1

            while spec + spec_new > u_max:
                if spec > 0 and random() < 0.5:
                    _remove_random_spec_element(child.condition)
                    spec -= 1
                else:
                    _remove_random_spec_element(diff)
                    spec_new -= 1
        else:
            while spec + spec_new > u_max:
                _remove_random_spec_element(diff)
                spec_new -= 1

        child.condition = diff

        if child.q < 0.5:
            child.q = 0.5

        child.exp = 1

        return child


def _get_differences(mark: list, perception: list) -> list:
    """
    The difference determination needs to distinguish between two cases.
    1. Clear differences are those where one or more attributes in the mark M
    do not contain the corresponding attribute in the perception.
    2. Fuzzy differences are those where there is no clear difference but one
    or more attributes in the mark M specify more than the one value in
    perception.

    In the first case, one random clear difference is specified while in the
    latter case all differences are specified.

    :param mark: list of sets containing marking states
    :param perception: perception obtained by the agent

    :return: list of differences
    """
    diff = get_general_perception()

    if Classifier.is_marked(mark):
        type1 = 0  # counts when mark is different from perception
        type2 = 0  # counts when mark is applied

        for i in range(len(perception)):
            if perception[i] not in mark[i]:
                type1 += 1
            if len(mark[i]) > 1:
                type2 += 1

        if type1 > 0:
            type1 = random() * type1
            for i in range(len(perception)):
                if perception[i] not in mark[i]:
                    if int(type1) == 0:
                        diff[i] = perception[i]
                    type1 -= 1
        elif type2 > 0:
            for i in range(len(perception)):
                if len(mark[i]) > 1:
                    diff[i] = perception[i]

    return diff


def _number_of_spec(condition: list) -> int:
    """
    Returns the number of non-#
    :param condition: a classifier condition or difference list
    :return: number of non-general elements
    """
    n = 0

    for i in range(len(condition)):
        if condition[i] != c.CLASSIFIER_WILDCARD:
            n += 1

    return n


def _remove_random_spec_element(condition: list) -> None:
    """
    Iterates over list and tries to replace random element
    with wildcard symbol.

    Argument is modified.

    :param condition: a classifier condition or a difference list
    """
    searching = True

    while searching:
        for i in condition:
            if i != c.CLASSIFIER_WILDCARD and random() > c.SPEC_ATT:
                i = c.CLASSIFIER_WILDCARD
                searching = False


def _unexpected_case(cl: Classifier,
                     perception: list,
                     previous_perception: list,
                     beta: float = None) -> Classifier:

    if beta is None:
        beta = c.BETA

    cl.q -= beta * cl.q
    cl.set_mark(previous_perception)

    for i in range(len(perception)):
        if cl.effect[i] != c.CLASSIFIER_WILDCARD:
            if (cl.effect[i] != perception[i] or
                    previous_perception[i] == perception[i]):
                return None

    child = Classifier.copy_from(cl)

    for i in range(len(perception)):
        if (cl.effect[i] == c.CLASSIFIER_WILDCARD and
                previous_perception[i] != perception[i]):
            child.condition[i] = previous_perception[i]
            child.effect[i] = perception[i]

    if cl.q < 0.5:
        cl.q = 0.5

    child.exp = 1

    return child


def _update_application_average(cl: Classifier, time: int, beta: float = None):
    """
    Procedure uses the moyenne adaptive modifee technique to reach
    an accurate value of the application average as soon as possible.
    Also the ALP timestamp is set in this procedure.

    :param cl: classifier to be updated
    :param time: current time
    :param beta: learning rate
    """
    if beta is None:
        beta = c.BETA

    if cl.exp < 1 / beta:
        cl.aav += (time - cl.t_alp - cl.aav) / cl.exp
    else:
        cl.aav += beta * (time - cl.t_alp - cl.aav)

    cl.t_alp = time


def _add_alp_classifier(cl: Classifier,
                        classifiers: list,
                        action_set: list,
                        beta: float = None) -> None:

    if beta is None:
        beta = c.BETA

    old_cl = None

    for cla in action_set:
        if cla.is_subsumer(cl):
            if old_cl is None or cla.is_more_general(cl):
                old_cl = cla

    if old_cl is None:
        for cla in action_set:
            if cla.condition == cl.condition and cla.effect == cl.effect:
                old_cl = cla

    if old_cl is None:
        classifiers.append(cl)
        action_set.append(cl)
    else:
        old_cl.q += beta * (1 - old_cl.q)


def _cover_triple(previous_perception: list,
                  perception: list,
                  action: int,
                  time: int) -> Classifier:
    """
    Covering generates a classifier that specifies all changes from the
    previous to current perception in condition and effect part. The action
    part of the new classifier is set to the executed action.

    :param previous_perception: previous perception
    :param perception: current perception
    :param action: new classifier action
    :param time:
    :return:
    """

    child = Classifier()
    child.action = action

    for i in range(len(perception)):
        if previous_perception[i] != perception[i]:
            child.condition[i] = previous_perception[i]
            child.effect[i] = perception[i]

    child.exp = 0
    child.r = 0
    child.aav = 0
    child.t_alp = time
    child.t_ga = time
    child.t = time
    child.q = 0.5
    child.num = 1

    return child


def _does_anticipate_correctly(classifier: Classifier,
                               perception: list,
                               previous_perception: list) -> bool:
    """
    Checks anticipation. While the pass-through symbols in the effect parąt
    of a classifier directly anticipate that these attributes stay the same
    after the execution of an action, the specified attributes anticipate
    a change to the specified value. Thus, if the perceived value did not
    change to the anticipated but actually stayed at the value, the classifier
    anticipates incorrectly.

    :param classifier: given classifier
    :param perception: current perception
    :param previous_perception: previous perception
    :return: True if classifier anticipates correctly, False otherwise
    """
    for i in range(c.CLASSIFIER_LENGTH):
        if classifier.effect[i] == c.CLASSIFIER_WILDCARD:
            if previous_perception[i] != perception[i]:
                return False
        else:
            if (classifier.effect[i] != perception[i] or
                    previous_perception[i] == perception[i]):
                return False

    return True