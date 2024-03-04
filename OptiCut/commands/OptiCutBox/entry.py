import adsk.core
import os
from ...lib import fusion360utils as futil
from ... import config
from . import logic

app = adsk.core.Application.get()
ui = app.userInterface

opti_cut_logic = logic.OptiCutLogic 


#*** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_optiCut'
CMD_NAME = 'OptiCut'
CMD_Description = 'A Fusion 360 Add-in that uses design bodies and lays them out on stock wood material'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
#Places the button in the utilities tab next to the add in 
WORKSPACE_ID = 'FusionSolidEnvironment'
TAB_ID = 'ToolsTab'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'


# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    futil.log(f'{CMD_NAME} started')

    #delete exisiting command in case it wasn't correctly deleted before
    cmdDef = ui.commandDefinitions.itemById(CMD_ID)
    if cmdDef:
        cmdDef.deleteMe()


    # Resource location for command icons, here we assume a sub folder in this directory named "resources".
    icon_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'OptiCut')

    # Create a command definition button
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, icon_folder)

    #Add image to go woth description that shows up when you hover over button 
    # Add the additional information for an extended tooltip.
    imageFilename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'Color_Logo.png')
    cmd_def.toolClipFilename = imageFilename

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    #get Utilities tab 
    tab = workspace.toolbarTabs.itemById(TAB_ID)

    # Get the panel the button will be created in.
    panel = tab.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED
    control.isPromotedByDefault = IS_PROMOTED


# Executed when add-in is stopped.
def stop():

    # General logging for debug.
    futil.log(f'{CMD_NAME} stopped')

    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    tab = workspace.toolbarTabs.itemById(TAB_ID)
    panel = tab.toolbarPanels.itemById(PANEL_ID)


    #delete the button command control
    command_control = panel.controls.itemById(CMD_ID)
    if command_control:
        command_control.deleteMe()
    
    #delete command defn 
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    if command_definition:
        command_definition.deleteMe()




# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')


    # TODO Define the dialog for your command by adding different inputs to the command.
    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    futil.log(f'{CMD_NAME} Command Created Event')

    # Setup the event handlers needed for this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_inputs, local_handlers=local_handlers)
    
    des: adsk.fusion.Design = app.activeProduct
    if des is None:
        return
    
    #create a instance of opti cut command class
    global opti_cut_logic
    opti_cut_logic = logic.OptiCutLogic(des)

    cmd = args.command
    cmd.isExecutedWhenPreEmpted = False

    #define dialog by creating command inputs
    opti_cut_logic.CreateCommandInputs(cmd.commandInputs)

# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    opti_cut_logic.HandleExecute(args)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {args.input.id}')

    opti_cut_logic.HandleInputsChanged(args)


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_inputs(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Validate Inputs Event fired.')

    opti_cut_logic.HandleValidateInputs(args)


# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
   
