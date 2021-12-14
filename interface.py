import sinergym
import PySimpleGUI as sg

# Layout designs
local_layout = [[sg.Text("Content for local experiments"), sg.Button("OK")]]
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
                          element_justification='center'),
                   sg.Tab('Google Cloud',
                          google_cloud_layout,
                          title_color='#ECEBB2',
                          background_color='#ECEBB2',
                          tooltip='Google Cloud executions for your experiments',
                          element_justification='center'),
                   sg.Tab('Tests',
                          test_layout,
                          title_color='Black',
                          background_color='#C1ECB2',
                          tooltip='Tests for Sinergym v{}'.format(sinergym.__version__),
                          element_justification='center')]],
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
    layout=tabexample,
    size=(500, 500))

while True:
    event, values = window.read()

    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
