import adsk.core
import adsk.fusion
import traceback

from collections import defaultdict

import string

from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase




def get_appearances_dict():
    ao = AppObjects()

    all_appearances = ao.design.appearances
    results = defaultdict(list)

    translator = str.maketrans('', '', string.punctuation)


    for appearance in all_appearances:
        used_by = appearance.usedBy
        # ao.ui.messageBox(str(appearance.id).translate(translator))
        for item in used_by:
            result = {}
            result['item'] = item
            result['id'] = str(appearance.id).translate(translator)

            if item.objectType == adsk.fusion.BRepBody.classType():
                result['type'] = "Body"
                result['appearance'] = appearance.name
                result['overide'] = item.appearanceSourceType
                if item.assemblyContext is not None:

                    result['parent'] = item.assemblyContext.fullPathName
                    result['name'] = item.assemblyContext.fullPathName + " - " + item.name
                else:
                    result['parent'] = ao.root_comp.name
                    result['name'] = ao.root_comp.name + " - " + item.name

            elif item.objectType == adsk.fusion.BRepFace.classType():
                result['type'] = "Face"
                result['appearance'] = appearance.name
                result['overide'] = item.appearanceSourceType

                if item.assemblyContext is not None:
                    result['parent'] = item.body.assemblyContext.fullPathName
                    result['name'] = item.assemblyContext.fullPathName + " - " + item.body.name + " - Face"
                else:
                    result['parent'] = ao.root_comp.name
                    result['name'] = ao.root_comp.name + " - " + item.body.name + " - Face"

            elif item.objectType == adsk.fusion.Occurrence.classType():
                result['type'] = "Occurrence"
                result['name_short'] = item.name
                result['name'] = item.fullPathName

                result['appearance'] = appearance.name
                if item.appearance is None:
                    result['overide'] = False
                else:
                    result['overide'] = True

            elif item.objectType == adsk.fusion.Component.classType():
                result['type'] = "Component"
                result['name_short'] = item.name
                result['name'] = item.name

                result['appearance'] = appearance.name


            results[appearance.name].append(result)

    return results


# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says "pass" for any method you want to use
class AppearanceRemoverCommand(Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):

        ao = AppObjects()
        for cmd_input in inputs:
            if cmd_input.objectType == adsk.core.BoolValueCommandInput.classType():

                attributes = ao.design.findAttributes("AppearanceUtilities", cmd_input.id)
                item = attributes[0].parent

                if not cmd_input.value:
                    item.appearance = None
                else:
                    item.appearance = ao.design.appearances.itemById(attributes[0].value)

        args.isValidResult = True

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        pass

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()

        appearances_dict = get_appearances_dict()

        # for item in results.items():
        #     ao.ui.messageBox(str(item))

    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    # The following is a basic sample of a dialog UI
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = AppObjects()

        appearances_dict = get_appearances_dict()

        index = 0
        for appearance_name, item_list in appearances_dict.items():
            # ao.ui.messageBox(appearance_name)
            group_inputs = inputs.addGroupCommandInput(item_list[0]['id'], appearance_name)
            sub_index = 0
            for item in item_list:
                bool_id = "bool_input_" + str(index) + "_" + str(sub_index)

                ao.ui.messageBox(str(item))
                bool_input = group_inputs.children.addBoolValueInput(bool_id, item['name'], True, "", True)
                bool_input.isEnabledCheckBoxDisplayed = True
                item['item'].attributes.add("AppearanceUtilities", bool_id, item['id'])
                sub_index += 1

            index += 1


class AppearanceRemoveAllCommand(Fusion360CommandBase):
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        all_appearances = ao.design.appearances

        for appearance in all_appearances:
            used_by = appearance.usedBy
            for item in used_by:
                item.appearance = None
