import adsk.core
import adsk.fusion
import os
import json

app = adsk.core.Application.get()
ui = app.userInterface
skipValidate = False

class OptiCutLogic():
    def __init__(self, des:adsk.fusion.Design):
        #Read cached values if they exist
        settings = None
        settingAttribute = des.attributes.itemByName('OptiCut', 'settings')
        if settingAttribute is not None:
            jsonSettings = settingAttribute.value
            settings = json.loads(jsonSettings)

        defaultUnits = des.unitsManager.defaultLengthUnits

        #choose in or mm
        if defaultUnits == "in" or defaultUnits == "ft":
            self.units = "in"
        else:
            self.units = "mm"

        #if units is inches set standard to english or if mm set to metric
        if self.units == "in":
            self.standard = "English Standard"
        else:
            self.standard = "Metric"
        if settings:
            self.standard = settings["Standard"]
        
        if self.standard == "English Standard":
            self.units = "in"
        else:
            self.units = "mm"
        #initialize kerf
        self.kerf = "1/8"
        #if setting is not none
        if settings:
            #update kerf with value stored in cached settings 
            self.kerf = settings["Kerf"]

        self.kerfCustom = "1/8"
        if settings:
            self.kerfCustom = float(settings["kerfCustom"])

        self.thickness = "1/2"
        if settings:
            self.thickness = settings["Thickness"]

        self.thicknessCustom = "1/2"
        if settings:
            self.thicknessCustom = float(settings["thicknessCustom"])


    def CreateCommandInputs(self, inputs: adsk.core.CommandInputs):
        global skipValidate
        skipValidate = True

        #create the command inputs


        self.standardDropDownInput = inputs.addDropDownCommandInput('standard', "Standard", adsk.core.DropDownStyles.TextListDropDownStyle)
        if self.standard == "English Standard":
            self.standardDropDownInput.listItems.add("English Standard", True)
            self.standardDropDownInput.listItems.add("Metric", False)    
        else:
            self.standardDropDownInput.listItems.add("English Standard", False)
            self.standardDropDownInput.listItems.add("Metric", True)   

        self.kerfListInput = inputs.addDropDownCommandInput('kerf', "Kerf", adsk.core.DropDownStyles.TextListDropDownStyle)
        if self.kerf == "1/8\"":
            self.kerfListInput.listItems.add("1/8\"", True)
        else:
            self.kerfListInput.listItems.add("1/8\"", False)

        if self.kerf == "1/16\"":
            self.kerfListInput.listItems.add("1/16\"", True)
        else:
            self.kerfListInput.listItems.add("1/16\"", False)

        if self.kerf == "3/32\"":
            self.kerfListInput.listItems.add("3/32\"", True)
        else:
            self.kerfListInput.listItems.add("3/32\"", False)  

        if self.kerf == "Custom":
            self.kerfListInput.listItems.add("Custom", True)
        else:
            self.kerfListInput.listItems.add("Custom", False)

        self.kerfCustomValueInput = inputs.addValueInput("kerfCustom", "Custom Kerf", "in", adsk.core.ValueInput.createByReal(self.kerfCustom))
        if self.kerf != "Custom":
            self.kerfCustomValueInput.isVisible = False

    
        self.thicknessListInput = inputs.addDropDownCommandInput('thickness', "Board Thickness", adsk.core.DropDownStyles.TextListDropDownStyle)
        if self.thickness == "1/4":
            self.thicknessListInput.listItems.add("1/4", True)
        else:
            self.thicknessListInput.listItems.add("1/4", False)

        if self.thickness == "3/8":
            self.thicknessListInput.listItems.add("3/8", True)
        else:
            self.thicknessListInput.listItems.add("3/8", False)

        if self.thickness == "1/2":
            self.thicknessListInput.listItems.add("1/2", True)
        else:
            self.thicknessListInput.listItems.add("1/2", False)  

        if self.thickness == "Custom":
            self.thicknessListInput.listItems.add("Custom", True)
        else:
            self.thicknessListInput.listItems.add("Custom", False)

        self.thicknessCustomValueInput = inputs.addValueInput("thicknessCustom", "Custom Thickness", "in", adsk.core.ValueInput.createByReal(self.thicknessCustom))
        if self.thickness != "Custom":
            self.thicknessCustomValueInput.isVisible = False

        self.errorMessageTextInput = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
        self.errorMessageTextInput.isFullWidth = True

        skipValidate = False


    def HandleInputsChanged(self, args: adsk.core.InputChangedEventArgs):
        changedInput = args.input

        if not skipValidate:
            if changedInput.id == 'standard':
                if self.standardDropDownInput.selectedItem.name == 'English Standard':
                    self.units = "in"
                elif self.standardDropDownInput.selectedItem.name == 'Metric':
                    self.units = 'mm'

                # Set each one to it's current value to work around an issue where
                # otherwise if the user has edited the value, the value won't update 
                # in the dialog because apparently it remembers the units when the 
                # value was edited.  Setting the value using the API resets this.
                
                if changedInput.id == 'kerf':
                    if self.kerfListInput.selectedItem.name == 'Custom':
                        self.kerfCustomValueInput.isVisible = True
                    else:
                        self.kerfCustomValueInput.isVisible = False

                if changedInput.id == 'thickness':
                    if self.thicknessListInput.selectedItem.name == 'Custom':
                        self.thicknessCustomValueInput.isVisible = True
                    else:
                        self.thicknessCustomValueInput.isVisible = False

    def HandleValidateInputs(self, args: adsk.core.ValidateInputsEventArgs):
        if not skipValidate:
            self.errorMessageTextInput.text = ""

            if self.kerfListInput.selectedItem.name == 'Custom':
                kerf = self.kerfCustomValueInput.value
                if kerf > 2:
                    self.errorMessageTextInput.text = "Kerf entered is larger than standard kerf"
                    args.areInputsValid = False
                    return 
            else:
                if self.kerfListInput.selectedItem.name == '1/8':
                    kerf = 1/8
                elif self.kerfListInput.selectedItem.name == '1/16':
                    kerf = 1/16
                elif self.kerfListInput.selectedItem.name == '3/32':
                    kerf = 3/32
            
            if self.thicknessListInput.selectedItem.name == 'Custom':
                thickness = self.thicknessCustomValueInput.value
                if thickness > 5:
                    self.errorMessageTextInput.text = "The board thickness entered is larger than board standards"
                    args.areInputsValid = False
                    return 
            else:
                if self.thicknessListInput.selectedItem.name == '1/4':
                    thickness = 1/8
                elif self.thicknessListInput.selectedItem.name == '3/8':
                    thickness = 1/16
                elif self.thicknessListInput.selectedItem.name == '1/2':
                    thickness = 3/32

    def HandleExecute(self, args: adsk.core.CommandEventArgs):
        #save current values as attributes
        settings = {'Standard': self.standardDropDownInput.selectedItem.name,
                    'Kerf': self.kerfListInput.selectedItem.name,
                    'KerfCustom': str(self.kerfCustomValueInput.value),
                    'Thickness': self.thicknessListInput.selectedItem.name,
                    'ThicknessCustom': str(self.thicknessCustomValueInput.value)}
        
        jsonSettings = json.dumps(settings)

        des = adsk.fusion.Design.cast(app.activeProduct)
        attribs = des.attributes
        attribs.add('OptiCut', 'settings', jsonSettings)

        # Get the current values.
        if self.kerfListInput.selectedItem.name == 'Custom':
            kerf = self.kerfCustomValueInput.value
        else:
            if self.kerfListInput.selectedItem.name == '1/8':
                kerf = "1/8"
            elif self.kerfListInput.selectedItem.name == '1/16':
                kerf = "1/16"
            elif self.kerfListInput.selectedItem.name == '3/32':
                kerf = "3/32"
        
        if self.thicknessListInput.selectedItem.name == 'Custom':
            thickness = self.thicknessCustomValueInput.value
        else:
            if self.thicknessListInput.selectedItem.name == '1/4':
                thickness = "1/4"
            elif self.thicknessListInput.selectedItem.name == '3/8':
                thickness = "3/8"
            elif self.thicknessListInput.selectedItem.name == '1/2':
                thickness = "1/2"

        app.log("Logged")

        





        

