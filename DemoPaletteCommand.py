import adsk.core
import adsk.fusion
import traceback

import json
from json import dumps
from collections import defaultdict

import os

from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase, Fusion360PaletteCommandBase
from .Fusion360Utilities.Fusion360Utilities import AppObjects


def add_appearances_to_tree(node_list):
    ao = AppObjects()

    face_keys = {}

    all_appearances = ao.design.appearances
    for appearance in all_appearances:
        used_by = appearance.usedBy
        for item in used_by:

            add_node = True

            # ao.ui.messageBox(item.objectType)
            appearance_node = {"state": {"checked": True}}

            appearance_name = appearance.name
            appearance_id = appearance.id

            appearance_node["type"] = "1-appearance"
            appearance_node['text'] = appearance_name

            if item.objectType == adsk.fusion.BRepBody.classType():
                body = {
                    'text': item.name,
                    "type": "3-body",
                    "state": {"opened": True,
                              "checkbox_disabled": True
                              }
                }
                # ao.ui.messageBox(str(item.appearanceSourceType))

                if item.assemblyContext is not None:
                    body['parent'] = item.assemblyContext.name
                    body['id'] = item.assemblyContext.fullPathName + " - " + item.name

                else:
                    body['parent'] = ao.root_comp.name
                    body['id'] = ao.root_comp.name + " - " + item.name

                appearance_node['parent'] = body['id']
                appearance_node['id'] = body['id'] + " - " + appearance_name

                # Check if source is material or appearance
                if item.appearanceSourceType == adsk.core.AppearanceSourceTypes.MaterialAppearanceSource:
                    if item.material.id != ao.app.preferences.materialPreferences.defaultMaterial.id:
                        appearance_id = item.material.id
                        appearance_node["type"] = "2-material"
                    else:
                        add_node = False
                # If not a material add a node for material if it is not the default
                else:
                    if item.material.id != ao.app.preferences.materialPreferences.defaultMaterial.id:
                        appearance_node_2 = {
                            "state": {"checked": True},
                            "type": "2-material",
                            'text': item.material.name,
                            "parent": body['id'],
                            "id": body['id'] + " - " + item.material.name
                        }
                        item.attributes.add("AppearanceUtilitiesPalette", appearance_node_2['id'], item.material.id)
                        node_list.append(appearance_node_2)

                    else:
                        add_node = False

                if not face_keys.get(body['id'], False):
                    node_list.append(body)
                    face_keys[body['id']] = True

            elif item.objectType == adsk.fusion.BRepFace.classType():

                body = {
                    'text': item.body.name,
                    "type": "3-body",
                    "state": {"opened": False,
                              "checkbox_disabled": True}
                }

                face = {
                    'text': "Face" + " - " + str(item.tempId),
                    "type": "5-face",
                    "state": {"opened": True,
                              "checkbox_disabled": True}
                }

                if item.assemblyContext is not None:

                    body['parent'] = item.assemblyContext.name
                    face['parent'] = item.assemblyContext.fullPathName + " - " + item.body.name
                    appearance_node['parent'] = item.assemblyContext.fullPathName + " - " + str(item.tempId)
                    body['id'] = item.assemblyContext.fullPathName + " - " + item.body.name
                    face['id'] = item.assemblyContext.fullPathName + " - " + str(item.tempId)
                    appearance_node['id'] = face['id'] + " - " + appearance_name
                else:
                    body['parent'] = ao.root_comp.name
                    face['parent'] = ao.root_comp.name + " - " + item.body.name
                    appearance_node['parent'] = ao.root_comp.name + " - " + str(item.tempId)
                    body['id'] = ao.root_comp.name + " - " + item.body.name
                    face['id'] = ao.root_comp.name + " - " + str(item.tempId)
                    appearance_node['id'] = face['id'] + " - " + appearance_name

                if not face_keys.get(body['id'], False):
                    node_list.append(body)
                    face_keys[body['id']] = True

                node_list.append(face)

            elif item.objectType == adsk.fusion.Occurrence.classType():
                appearance_node['id'] = item.name + " - " + appearance_name
                appearance_node['parent'] = item.name

            elif item.objectType == adsk.fusion.Component.classType():
                appearance_node['id'] = item.name + " - " + appearance_name
                appearance_node['parent'] = item.name
                appearance_node["state"] = {"checkbox_disabled": True,
                                            "checked": True
                                            }
                appearance_node["type"] = "1-root_appearance"

            else:
                return

            if add_node:
                item.attributes.add("AppearanceUtilitiesPalette", appearance_node['id'], appearance_id)
                node_list.append(appearance_node)


def make_component_tree():
    ao = AppObjects()

    node_list = []

    root_node = {
        'id': ao.root_comp.name,
        'text': ao.root_comp.name,
        "type": "4-root_component",
        'parent': "#",
        "state": {"opened": True,
                  "checkbox_disabled": True
                  }

    }
    node_list.append(root_node)

    if ao.root_comp.occurrences.count > 0:
        make_assembly_nodes(ao.root_comp.occurrences, node_list, ao.root_comp.name)

    return node_list


def make_assembly_nodes(occurrences: adsk.fusion.OccurrenceList, node_list, parent):
    for occurrence in occurrences:

        node = {
            'id': occurrence.name,
            'text': occurrence.name,
            'parent': parent,
            "state": {"opened": False,
                      "checkbox_disabled": True
                      }
        }

        if occurrence.childOccurrences.count > 0:

            node["type"] = "4-component_group"
            node_list.append(node)
            make_assembly_nodes(occurrence.childOccurrences, node_list, occurrence.name)

        else:
            node["type"] = "4-component"
            node_list.append(node)


def adjust_material(node_id, appearance_checked, node_type):
    ao = AppObjects()
    attributes = ao.design.findAttributes("AppearanceUtilitiesPalette", node_id)

    # ao.ui.messageBox(str(node_id) + "     " + str(appearance_checked))
    if len(attributes) > 0:
        item = attributes[0].parent

        if item is not None:
            if not appearance_checked:

                if node_type == "2-material":
                    item.material = ao.app.preferences.materialPreferences.defaultMaterial
                else:
                    item.appearance = None
            else:
                if node_type == "2-material":
                    item.material = ao.design.materials.itemById(attributes[0].value)
                else:
                    item.appearance = ao.design.appearances.itemById(attributes[0].value)


def build_data():
    node_list = make_component_tree()
    add_appearances_to_tree(node_list)
    return {'core': node_list, 'root_name': "the_root"}



# Class for a Fusion 360 Palette Command
class DemoPaletteShowCommand(Fusion360PaletteCommandBase):

    # Run when user executes command in UI, useful for handling extra tasks on palette like docking
    def on_palette_execute(self, palette: adsk.core.Palette):
        # Dock the palette to the right side of Fusion window.
        if palette.dockingState == adsk.core.PaletteDockingStates.PaletteDockStateFloating:
            palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

        ao = AppObjects()
        next_command = ao.ui.commandDefinitions.itemById("cmdID_palette_send")
        next_command.execute()

    # Run when ever a fusion event is fired from the corresponding web page
    def on_html_event(self, html_args: adsk.core.HTMLEventArgs):
        ao = AppObjects()
        # ao.ui.messageBox(html_args.action)

        if html_args.action == "check_node":
            data = json.loads(html_args.data)
            adjust_material(data["node_id"], data["remove_material"], data["node_type"])

        if html_args.action == "refresh_tree":
            data = json.loads(html_args.data)
            palette = ao.ui.palettes.itemById(self.palette_id)

            # Send message to the HTML Page
            if palette:
                return_json = build_data()
                palette.sendInfoToHTML('tree_refresh', dumps(return_json))

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
        # message = input_values['palette_string']

        # Send message to the HTML Page
        if palette:
            # palette.sendInfoToHTML('send', message)
            return_json = build_data()
            palette.sendInfoToHTML('tree_update', dumps(return_json))

    # Run when the user selects your command icon from the Fusion 360 UI
    def on_create(self, command: adsk.core.Command, command_inputs: adsk.core.CommandInputs):
        # command_inputs.addStringValueInput('palette_string', 'Palette Message', 'Some text to send to Palette')
        pass
