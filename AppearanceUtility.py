# Importing sample Fusion Command
# Could import multiple Command definitions here
from .Demo1Command import Demo1Command
from .AppearanceRemoverCommand import AppearanceRemoverCommand, AppearanceRemoveAllCommand
from .DemoPaletteCommand import DemoPaletteShowCommand, DemoPaletteSendCommand

commands = []
command_definitions = []

# # Define parameters for 1st command
# cmd = {
#     'cmd_name': 'Fusion Demo Command 1',
#     'cmd_description': 'Fusion Demo Command 1 Description',
#     'cmd_id': 'cmdID_demo_1',
#     'cmd_resources': './resources',
#     'workspace': 'FusionSolidEnvironment',
#     'toolbar_panel_id': 'SolidScriptsAddinsPanel',
#     'class': Demo1Command
# }
# command_definitions.append(cmd)

# Define parameters for 2nd command
cmd = {
    'cmd_name': 'Appearance Remover',
    'cmd_description': 'Displays all appearance over rides in the model and allows you to remove them',
    'cmd_id': 'cmdID_AppearanceRemoverCommand',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'Appearances',
    'command_visible': True,
    'command_promoted': False,
    'class': AppearanceRemoverCommand
}
command_definitions.append(cmd)

# Define parameters for 2nd command
cmd = {
    'cmd_name': 'Remove All Appearances',
    'cmd_description': 'Removes all appearance overrides in the design',
    'cmd_id': 'cmdID_AppearanceRemoveAllCommand',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'Appearances',
    'command_visible': True,
    'command_promoted': False,
    'class': AppearanceRemoveAllCommand
}
command_definitions.append(cmd)

# Define parameters for 2nd command
cmd = {
    'cmd_name': 'Appearance Tree',
    'cmd_description': 'Fusion Appearance Utility to visualize and remove material and appearance over rides',
    'cmd_id': 'cmdID_appearance_tree',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'Appearances',
    'command_visible': True,
    'command_promoted': True,
    'palette_id': 'palette_id_appearance_tree',
    'palette_name': 'Appearance Tree',
    'palette_html_file_url': 'demo.html',
    'palette_is_visible': True,
    'palette_show_close_button': True,
    'palette_is_resizable': True,
    'palette_width': 450,
    'palette_height': 900,
    'class': DemoPaletteShowCommand
}
command_definitions.append(cmd)

# Define parameters for 2nd command
cmd = {
    'cmd_name': 'Fusion Palette Send Command',
    'cmd_description': 'Send info to Fusion 360 Palette',
    'cmd_id': 'cmdID_palette_send',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'Appearances',
    'command_visible': False,
    'command_promoted': False,
    'palette_id': 'palette_id_appearance_tree',
    'class': DemoPaletteSendCommand
}
command_definitions.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False

# Don't change anything below here:
for cmd_def in command_definitions:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)


def run(context):
    for run_command in commands:
        run_command.on_run()


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()
