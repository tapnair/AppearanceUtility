import adsk.core
import adsk.fusion
import traceback

import json
from json import dumps
from collections import defaultdict

from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase, Fusion360PaletteCommandBase
from .Fusion360Utilities.Fusion360Utilities import AppObjects


def add_appearances_to_tree(node_list):
    ao = AppObjects()

    all_appearances = ao.design.appearances
    for appearance in all_appearances:
        used_by = appearance.usedBy
        for item in used_by:

            if item.objectType == adsk.fusion.BRepBody.classType():
                body = {
                    'id': item.assemblyContext.fullPathName + " - " + item.name,
                    'name': item.name,
                    'text': item.name,
                    'parent': item.assemblyContext.name
                }
                node_list.append(body)

                body_appearance = {
                    'id': item.assemblyContext.fullPathName + " - " + item.name + " - " + appearance.name,
                    'name': appearance.name,
                    'text': appearance.name,
                    'parent': item.assemblyContext.fullPathName + " - " + item.name
                }
                node_list.append(body_appearance)

            elif item.objectType == adsk.fusion.BRepFace.classType():

                # TODO check for duplicate bodies
                body = {
                    'id': item.assemblyContext.fullPathName + " - " + item.body.name,
                    'name': item.body.name,
                    'text': item.body.name,
                    'parent': item.assemblyContext.name
                }
                node_list.append(body)

                face = {
                    'id': item.assemblyContext.fullPathName + " - " + str(item.tempId),
                    'name': "Face" + " - " + str(item.tempId),
                    'text': "Face" + " - " + str(item.tempId),
                    'parent': item.assemblyContext.fullPathName + " - " + item.body.name
                }
                node_list.append(face)

                face_appearance = {
                    'id': item.assemblyContext.fullPathName + " - " + str(item.tempId) + " - " + appearance.name,
                    'name': appearance.name,
                    'text': appearance.name,
                    'parent': item.assemblyContext.fullPathName + " - " + str(item.tempId)
                }
                node_list.append(face_appearance)

            elif item.objectType == adsk.fusion.Occurrence.classType():
                result = {
                    'id': item.name + " - " + appearance.name,
                    'name': appearance.name,
                    'text': appearance.name,
                    'parent': item.name
                }

                node_list.append(result)


def make_component_tree():
    ao = AppObjects()

    node_list = []
    root_node = {
        'id': ao.root_comp.name,
        'name': ao.root_comp.name,
        'text': ao.root_comp.name,
        'parent': "#"
    }
    node_list.append(root_node)

    if ao.root_comp.occurrences.count > 0:
        make_assembly_nodes(ao.root_comp.occurrences, node_list, ao.root_comp.name)

    return node_list


def make_assembly_nodes(occurrences: adsk.fusion.OccurrenceList, node_list, parent):

    for occurrence in occurrences:
        if occurrence.childOccurrences.count > 0:
            make_assembly_nodes(occurrence.childOccurrences, node_list, occurrence.name)

        make_node(occurrence, node_list, parent)


def make_node(occurrence: adsk.fusion.Occurrence, node_list, parent):
    node_list.append({
        'id': occurrence.name,
        'name': occurrence.name,
        'text': occurrence.name,
        'parent': parent
    })


# Class for a Fusion 360 Palette Command
class DemoPaletteShowCommand(Fusion360PaletteCommandBase):

    # Run when user executes command in UI, useful for handling extra tasks on palette like docking
    def on_palette_execute(self, palette: adsk.core.Palette):

        # Dock the palette to the right side of Fusion window.
        if palette.dockingState == adsk.core.PaletteDockingStates.PaletteDockStateFloating:
            palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

    # Run when ever a fusion event is fired from the corresponding web page
    def on_html_event(self, html_args: adsk.core.HTMLEventArgs):

        # Parse incoming message and build message for Fusion message box
        data = json.loads(html_args.data)
        msg = "An event has been fired from the html to Fusion with the following data:\n"
        msg += '    Command: {}\n    arg1: {}\n    arg2: {}'.format(html_args.action, data['arg1'], data['arg2'])

        # Display Message
        ao = AppObjects()
        ao.ui.messageBox(msg)

    # Handle any extra cleanup when user closes palette here
    def on_palette_close(self):
        pass


# This is a standard Fusion Command that will send data to the palette
class DemoPaletteSendCommand(Fusion360CommandBase):

    def __init__(self, cmd_def, debug):
        super().__init__(cmd_def, debug)

        # Pass in the palette_id as extra data in command definition
        # A generally useful technique to make commands more re-usable
        self.palette_id = cmd_def.get('palette_id', None)

    # When the command is clicked it will send this message to the HTML Palette
    def on_execute(self, command: adsk.core.Command, command_inputs: adsk.core.CommandInputs, args, input_values):

        # Get Reference to Palette
        ao = AppObjects()
        palette = ao.ui.palettes.itemById(self.palette_id)

        # Get input value from string input
        message = input_values['palette_string']

        # Send message to the HTML Page
        if palette:
            # palette.sendInfoToHTML('send', message)

            # TODO build the tree

            item1 = {
                'id': "123",
                'name': "name 1",
                'text': "balh blah",
                'parent': "#"
            }
            item2 = {
                'id': "1234",
                'name': "name 2",
                'text': "balh blahcdcdsscsdcsd",
                'parent': "123"
            }
            items_list = [item1, item2]

            node_list = make_component_tree()
            add_appearances_to_tree(node_list)
            return_json = {'core': node_list, 'root_name': "the_root"}

            palette.sendInfoToHTML('tree_update', dumps(return_json))

    # Run when the user selects your command icon from the Fusion 360 UI
    def on_create(self, command: adsk.core.Command, command_inputs: adsk.core.CommandInputs):

        command_inputs.addStringValueInput('palette_string', 'Palette Message', 'Some text to send to Palette')
