import csv
import os
from collections import deque

import numpy as np
import pytest

from sinergym.utils.common import is_wrapped
from sinergym.utils.constants import RANGES_5ZONE
from sinergym.utils.wrappers import NormalizeObservation


@pytest.mark.parametrize('env_name',
                         [('env_wrapper_normalization'),
                          ('env_all_wrappers'),
                          ])
def test_normalization_wrapper(env_name, request):
    env = request.getfixturevalue(env_name)

    # Check if new attributes have been created in environment
    assert hasattr(env, 'unwrapped_observation')
    assert hasattr(env, 'ranges')

    # Check initial values of that attributes
    assert env.unwrapped_observation is None
    assert env.ranges == RANGES_5ZONE

    # Initialize env
    obs, _ = env.reset()

    # Check observation normalization
    assert (obs >= 0).all() and (obs <= 1).all()
    # Check original observation recording
    assert env.unwrapped_observation is not None

    # Simulation random step
    a = env.action_space.sample()
    obs, _, _, _, _ = env.step(a)

    assert (obs >= 0).all() and (obs <= 1).all()
    assert env.unwrapped_observation is not None


def test_multiobjective_wrapper(env_wrapper_multiobjective):

    assert hasattr(env_wrapper_multiobjective, 'reward_terms')
    env_wrapper_multiobjective.reset()
    action = env_wrapper_multiobjective.action_space.sample()
    _, reward, _, _, info = env_wrapper_multiobjective.step(action)
    assert isinstance(reward, list)
    assert len(reward) == len(env_wrapper_multiobjective.reward_terms)


def test_datetime_wrapper(env_wrapper_datetime):

    observation_variables = env_wrapper_datetime.variables['observation']
    # Check observation varibles have been updated
    assert 'day' not in observation_variables
    assert 'month' not in observation_variables
    assert 'hour' not in observation_variables
    assert 'is_weekend' in observation_variables
    assert 'month_sin' in observation_variables
    assert 'month_cos' in observation_variables
    assert 'hour_sin' in observation_variables
    assert 'hour_cos' in observation_variables
    # Check new returned observation values are valid
    env_wrapper_datetime.reset()
    action = env_wrapper_datetime.action_space.sample()
    obs, _, _, _, _ = env_wrapper_datetime.step(action)
    obs_dict = dict(zip(observation_variables, obs))
    assert obs_dict['is_weekend'] is not None and obs_dict['month_sin'] is not None and obs_dict[
        'month_cos'] is not None and obs_dict['hour_sin'] is not None and obs_dict['hour_cos'] is not None


def test_previous_observation_wrapper(env_wrapper_previousobs):

    # Check that the original variable names with previous name added is
    # present
    previous_variable_names = [
        var for var in env_wrapper_previousobs.variables['observation'] if '_previous' in var]

    # Check previous observation stored has the correct len and initial values
    assert len(env_wrapper_previousobs.previous_observation) == 3
    assert len(previous_variable_names) == len(
        env_wrapper_previousobs.previous_observation)
    assert (env_wrapper_previousobs.previous_observation == 0.0).all()
    # Check reset and np.zeros is added in obs
    obs1, _ = env_wrapper_previousobs.reset()
    assert np.array_equal(env_wrapper_previousobs.previous_observation,
                          obs1[env_wrapper_previousobs.original_variable_index])
    # Check step and reset variables names is added in obs
    action = env_wrapper_previousobs.action_space.sample()
    obs2, _, _, _, _ = env_wrapper_previousobs.step(action)
    assert np.array_equal(env_wrapper_previousobs.previous_observation,
                          obs2[env_wrapper_previousobs.original_variable_index])
    assert np.array_equal(
        obs1[env_wrapper_previousobs.original_variable_index], obs2[-3:])


def test_incremental_wrapper(env_wrapper_incremental):

    # Check initial setpoints values is initialized
    assert len(env_wrapper_incremental.current_setpoints) > 0
    # Check if action selected is applied correctly
    env_wrapper_incremental.reset()
    action = env_wrapper_incremental.action_space.sample()
    _, _, _, _, info = env_wrapper_incremental.step(action)
    assert env_wrapper_incremental.current_setpoints == info['action']
    # Check environment clip actions
    # max values
    env_wrapper_incremental.current_setpoints = [
        env_wrapper_incremental.max_values[0] + 1,
        env_wrapper_incremental.max_values[1] + 1]
    _, _, _, _, info = env_wrapper_incremental.step(2)
    assert info['action'] == [
        env_wrapper_incremental.max_values[0],
        env_wrapper_incremental.max_values[1]]
    _, _, _, _, info = env_wrapper_incremental.step(11)
    assert info['action'] == [
        env_wrapper_incremental.max_values[0],
        env_wrapper_incremental.max_values[1]]
    # min values
    env_wrapper_incremental.current_setpoints = [
        env_wrapper_incremental.min_values[0] - 1,
        env_wrapper_incremental.min_values[1] - 1]
    _, _, _, _, info = env_wrapper_incremental.step(5)
    assert info['action'] == [
        env_wrapper_incremental.min_values[0],
        env_wrapper_incremental.min_values[1]]
    _, _, _, _, info = env_wrapper_incremental.step(16)
    assert info['action'] == [
        env_wrapper_incremental.min_values[0],
        env_wrapper_incremental.min_values[1]]


def test_multiobs_wrapper(env_wrapper_multiobs, env_demo_continuous):

    # Check attributes don't exist in original env
    assert not (hasattr(
        env_demo_continuous,
        'n') or hasattr(
        env_demo_continuous,
        'ind_flat') or hasattr(
            env_demo_continuous,
        'history'))
    # Check attributes exist in wrapped env
    assert hasattr(
        env_wrapper_multiobs,
        'n') and hasattr(
        env_wrapper_multiobs,
        'ind_flat') and hasattr(
            env_wrapper_multiobs,
        'history')

    # Check history
    assert env_wrapper_multiobs.history == deque([])

    # Check observation space transformation
    original_shape = env_demo_continuous.observation_space.shape[0]
    wrapped_shape = env_wrapper_multiobs.observation_space.shape[0]
    assert wrapped_shape == original_shape * env_wrapper_multiobs.n

    # Check reset obs
    obs, _ = env_wrapper_multiobs.reset()
    assert len(obs) == wrapped_shape
    for i in range(env_wrapper_multiobs.n - 1):
        # Check store same observation n times
        assert (obs[original_shape * i:original_shape *
                    (i + 1)] == obs[0:original_shape]).all()
        # Check history save same observation n times
        assert (env_wrapper_multiobs.history[i] ==
                env_wrapper_multiobs.history[i + 1]).all()

    # Check step obs
    a = env_wrapper_multiobs.action_space.sample()
    obs, _, _, _, _ = env_wrapper_multiobs.step(a)

    # Last observation must be different of the rest of them
    assert (obs[original_shape * (env_wrapper_multiobs.n - 1):]
            != obs[0:original_shape]).any()
    assert (env_wrapper_multiobs.history[0] !=
            env_wrapper_multiobs.history[-1]).any()


@ pytest.mark.parametrize('env_name',
                          [('env_wrapper_logger'), ('env_all_wrappers'), ])
def test_logger_wrapper(env_name, request):
    env = request.getfixturevalue(env_name)
    logger = env.logger
    env.reset()

    # Check CSV's have been created and linked in simulator correctly
    assert logger.log_progress_file == env.simulator._env_working_dir_parent + '/progress.csv'
    assert logger.log_file == env.simulator._eplus_working_dir + '/monitor.csv'

    tmp_log_file = logger.log_file

    # simulating short episode
    for _ in range(10):
        env.step(env.action_space.sample())
    env.reset()

    assert os.path.isfile(logger.log_progress_file)
    assert os.path.isfile(tmp_log_file)

    # If env is wrapped with normalize obs...
    if is_wrapped(env, NormalizeObservation):
        assert os.path.isfile(tmp_log_file[:-4] + '_normalized.csv')
    else:
        assert not os.path.isfile(tmp_log_file[:-4] + '_normalized.csv')

    # Check headers
    with open(tmp_log_file, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            assert ','.join(row) == logger.monitor_header
            break
    with open(logger.log_progress_file, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            assert ','.join(row) + '\n' == logger.progress_header
            break
    if is_wrapped(env, NormalizeObservation):
        with open(tmp_log_file[:-4] + '_normalized.csv', mode='r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                assert ','.join(row) == logger.monitor_header
                break

    env.close()


def test_logger_activation(env_wrapper_logger):
    assert env_wrapper_logger.logger.flag
    env_wrapper_logger.deactivate_logger()
    assert not env_wrapper_logger.logger.flag
    env_wrapper_logger.activate_logger()
    assert env_wrapper_logger.logger.flag


def test_env_wrappers(env_all_wrappers):
    # Check history multiobs is empty
    assert env_all_wrappers.history == deque([])
    # Start env
    obs, _ = env_all_wrappers.reset()
    # Check history has obs and any more
    assert len(env_all_wrappers.history) == env_all_wrappers.n
    assert (env_all_wrappers._get_obs() == obs).all()

    # This obs should be normalize --> [0,1]
    assert (obs >= 0).all() and (obs <= 1).all()

    # Execute a short episode in order to check logger
    logger = env_all_wrappers.logger
    tmp_log_file = logger.log_file
    for _ in range(10):
        _, reward, _, _, info = env_all_wrappers.step(
            env_all_wrappers.action_space.sample())
        # reward should be a vector
        assert isinstance(reward, list)
    env_all_wrappers.reset()

    # Let's check if history has been completed succesfully
    assert len(env_all_wrappers.history) == env_all_wrappers.n
    assert isinstance(env_all_wrappers.history[0], np.ndarray)

    # check logger
    assert logger.log_progress_file == env_all_wrappers.simulator._env_working_dir_parent + '/progress.csv'
    assert logger.log_file == env_all_wrappers.simulator._eplus_working_dir + '/monitor.csv'
    assert os.path.isfile(logger.log_progress_file)
    assert os.path.isfile(tmp_log_file)
    assert os.path.isfile(tmp_log_file[:-4] + '_normalized.csv')
    # Close env
    env_all_wrappers.close()
