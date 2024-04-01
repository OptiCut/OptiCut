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
            #get the data passed through settings, formatted as json
            settings = json.loads(jsonSettings)
            
    
        #if default units change then it could mess up design 
        #get what units fusion is already using
        defaultUnits = des.unitsManager.defaultLengthUnits   
        

        #choose in or mm
        if defaultUnits == "in" or defaultUnits == "ft":
            #set the unit for inside the add-in 
            self.units = "in"
        else:
            self.units = "mm"
        # Define the default for each value and then check to see if there
        # were cached settings and override the default if a setting exists.
        #if units is inches set standard to english or if mm set to metric
        if self.units == "in":
            self.standard = "Imperial"
        else:
            self.standard = "Metric"
        if settings:
            self.standard = settings["Standard"]
        
        if self.standard == "Imperial":
            self.units = "in"
            #self.kerf = ".125\""
            #self.thickness = "1/2\""
        else:
            self.units = "mm"
            #self.kerf = "3.175 mm"
            #self.thickness = "2.7 mm"
        #initialize kerf
        self.kerf = '.125 in'
        #if setting is not none
        if settings:
            #update kerf with value stored in cached settings 
           self.kerf = settings["Kerf"]

        self.kerfCustom = '.5 in'
        if settings:
            self.kerfCustom = settings["KerfCustom"]

        self.stockLength = '12 in'
        if settings:
            self.stockLength 






    def CreateCommandInputs(self, inputs: adsk.core.CommandInputs):
        global skipValidate
        skipValidate = True

        #create the command inputs
        selectInput = inputs.addSelectionInput('SelectionEventsSample', 'Bodies', 'Please select bodies to map')
        selectInput.addSelectionFilter(adsk.core.SelectionCommandInput.Bodies)
        selectInput.setSelectionLimits(maximum=100, minimum=0)
        self.standardDropDownInput = inputs.addDropDownCommandInput('standard', "Standard", adsk.core.DropDownStyles.TextListDropDownStyle)
        if self.standard == "Imperial":
            self.standardDropDownInput.listItems.add("Imperial", True)
            self.standardDropDownInput.listItems.add("Metric", False)    
        else:
            self.standardDropDownInput.listItems.add("Imperial", False)
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
        #elif self.kerf == "Custom":
            #self.kerfCustomValueInput.isVisible = True
       

        self.errorMessageTextInput = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
        self.errorMessageTextInput.isFullWidth = True

        skipValidate = False
        

    def HandleInputsChanged(self, args: adsk.core.InputChangedEventArgs):
        changedInput = args.input

        if not skipValidate:
            if changedInput.id == 'standard':
                if self.standardDropDownInput.selectedItem.name == 'Imperial':
                    self.units = "in"
                elif self.standardDropDownInput.selectedItem.name == 'Metric':
                    self.units = 'mm'

                # Set each one to it's current value to work around an issue where
                # otherwise if the user has edited the value, the value won't update 
                # in the dialog because apparently it remembers the units when the 
                # value was edited.  Setting the value using the API resets this.
                
                # self.kerfCustomValueInput.value = self.kerfCustomValueInput.value
                # self.kerfCustomValueInput.unitType = self.units
                # self.thicknessCustomValueInput.value = self.thicknessCustomValueInput.value
                # self.thicknessCustomValueInput.unitType = self.units
            #handles the change from kerf to kerf custom selection    
            if changedInput.id == 'kerf':
                if self.kerfListInput.selectedItem.name == 'Custom':
                    self.kerfCustomValueInput.isVisible = True
                    #should we make the kerf input no visible if they choose custom?
                    #self.kerfListInput.isVisible = False
                else:
                    self.kerfCustomValueInput.isVisible = False
            

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
                if self.kerfListInput.selectedItem.name == '1/8\"':
                    kerf = 1/8
                elif self.kerfListInput.selectedItem.name == '1/16\"':
                    kerf = 1/16
                elif self.kerfListInput.selectedItem.name == '3/32\"':
                    kerf = 3/32
            

        

    def HandleExecute(self, args: adsk.core.CommandEventArgs):
        #save current values as attributes
        settings = {'Standard': self.standardDropDownInput.selectedItem.name,
                    'Kerf': self.kerfListInput.selectedItem.name,
                    'KerfCustom': self.kerfCustomValueInput.value}
        
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

        
        
        app.log("Logged")

        





        

