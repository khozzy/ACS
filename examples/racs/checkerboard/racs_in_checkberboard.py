import logging

import gym
# noinspection PyUnresolvedReferences
import gym_checkerboard

from examples.racs.checkerboard.metrics import checkerboard_metrics
from lcs.agents.racs import Configuration, RACS
from lcs.representations.RealValueEncoder import RealValueEncoder

# Configure logger
logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':

    # Load desired environment
    chckb = gym.make('checkerboard-2D-3div-v0')

    # Create agent
    encoder = RealValueEncoder(resolution_bits=4)
    cfg = Configuration(chckb.observation_space.shape[0],
                        chckb.action_space.n,
                        encoder=encoder,
                        user_metrics_collector_fcn=checkerboard_metrics,
                        epsilon=0.5,
                        do_ga=True,
                        theta_r=0.9,
                        theta_i=0.2,
                        theta_ga=100,
                        chi=0.5,
                        mu=0.15)

    agent = RACS(cfg)
    population, metrics = agent.explore_exploit(chckb, 100)

    # print reliable classifiers
    reliable = [cl for cl in population if cl.is_reliable()]
    for cl in reliable:
        logging.info(cl)

    # print metrics
    for m in metrics:
        logging.info(m)