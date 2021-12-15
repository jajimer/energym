import sinergym
import gym
import PySimpleGUI as sg
from enum import Enum
import os


class Alg(Enum):
    DQN = 1
    PPO = 2
    A2C = 3
    DDPG = 4
    SAC = 5


class Reward(Enum):
    LINEAR = 1
    EXPONENTIAL = 2


envs_id = [env_spec.id for env_spec in gym.envs.registry.all()
           if env_spec.id.startswith('Eplus')]

sg.theme("DarkAmber")

# Layout designs
# Local experiments
local_layout = [
    [sg.T('Environment:'), sg.In(visible=True, size=(
        15, 1), enable_events=True, key='ENV_INPUT')],
    [sg.Listbox(values=envs_id, size=(50, 20),
                enable_events=True, key='ENV_LIST')],
    [sg.T('Episodes:'), sg.In(default_text='5', key='EPISODES')],
    [sg.T('Algorithm:'), sg.Listbox(values=[alg.name for alg in Alg], size=(20, len(Alg)),
                                    enable_events=True, key='ALG_LIST')],
    [sg.Text('Reward function:'), sg.Listbox(values=[rwd.name for rwd in Reward], size=(20, len(Reward)),
                                             enable_events=True, key='RWD_LIST')],
    [sg.T('Normalization:'), sg.Checkbox(
        text='', key='NORMALIZATION')],
    [sg.T('Logger:'), sg.Checkbox(text='', key='LOGGER')],
    [sg.T('Evaluation:'), sg.Checkbox(text='', key='EVALUATION', enable_events=True)],
    [sg.T('Evaluation Length:', key='EVAL_LENGTH_T', visible=False), sg.In(default_text=1, key='EVAL_LENGTH_IN', visible=False)],
    [sg.T('Evaluation Frequency:', key='EVAL_FREQ_T', visible=False), sg.In(default_text=1, key='EVAL_FREQ_IN', visible=False)]
]

google_cloud_layout = [[sg.Text("Content for cloud experiments")], [
    sg.Button("OK")]]

test_layout = [[sg.Text("Content for test experiments")], [sg.Button("OK")]]

# Defining layout like tabs
tabexample = [
    [sg.TabGroup([[sg.Tab(title='Local',
                          layout=local_layout,
                          title_color='Purple',
                          border_width=10,
                          background_color='#B2B4EC',
                          tooltip='Local execution for your experiments',
                          element_justification='left'),
                   sg.Tab('Google Cloud',
                          google_cloud_layout,
                          title_color='#ECEBB2',
                          background_color='#ECEBB2',
                          tooltip='Google Cloud executions for your experiments',
                          element_justification='left'),
                   sg.Tab('Tests',
                          test_layout,
                          title_color='Black',
                          background_color='#C1ECB2',
                          tooltip='Tests for Sinergym v{}'.format(
                              sinergym.__version__),
                          element_justification='left')]],
                 tab_location='centertop',
                 title_color='Black',
                 tab_background_color='Gray',
                 selected_title_color='Green',
                 selected_background_color='Black',
                 border_width=5)],
    [sg.Button('Close')]
]


window = sg.Window(
    title="Sinergym v{}".format(
        sinergym.__version__),
    icon=os.path.abspath('images/logo.png'),
    layout=tabexample,
    size=(1000, 1000))

# Preselected values in listbox's
window['ENV_LIST'].set_value(envs_id[0])
window['ALG_LIST'].set_value(list(Alg)[0].name)
window['RWD_LIST'].set_value(list(Reward)[0].name)

while True:
    event, values = window.read()

    # Close window
    if event == sg.WIN_CLOSED:
        break

    # Environment browser
    if event == 'ENV_INPUT':
        if values['ENV_INPUT'] == '':
            window.Element('ENV_LIST').Update(values=envs_id)
        else:
            search = values['ENV_INPUT'].upper()
            env_results = [env for env in envs_id if search in env.upper()]
            window.Element('ENV_LIST').Update(values=env_results)

    if event == 'EVALUATION':
        if values['EVALUATION']:
            [element.Update(visible=True) for key,
             element in window.key_dict.items() if 'EVAL_' in key]


window.close()
