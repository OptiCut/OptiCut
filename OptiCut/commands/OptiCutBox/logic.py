import adsk.core
import adsk.fusion
import json
from ...lib import fusion360utils as futil

app = adsk.core.Application.get()
ui = app.userInterface
skipValidate = False


class OptiCutLogic():
    def __init__(self, des: adsk.fusion.Design):
        # Read the cached values, if they exist.
        settings = None
        settingAttribute = des.attributes.itemByName('OptiCut', 'settings')
        if settingAttribute is not None:
            jsonSettings = settingAttribute.value
            settings = json.loads(jsonSettings)              

        defaultUnits = des.unitsManager.defaultLengthUnits
            
        # Determine whether to use inches or millimeters as the intial default.
        if defaultUnits == 'in' or defaultUnits == 'ft':
            self.units = 'in'
        else:
            self.units = 'mm'
        
        # Define the default for each value and then check to see if there
        # were cached settings and override the default if a setting exists.
        if self.units == 'in':
            self.standard = 'Imperial'
        else:
            self.standard = 'Metric'
        if settings:
            self.standard = settings['Standard']
            
        if self.standard == 'Imperial':
            self.units = 'in'
        else:
            self.units = 'mm'
        
        self.kerfIn = '0.0 in'
        if settings:
            self.kerfIn = settings['KerfIn']
        
        self.kerfInCustom = 0
        if settings:
            self.kerfInCustom = float(settings['KerfInCustom'])            

        self.kerfMm = '0.0 mm'
        if settings:
            self.kerfMm = settings['KerfMm']

        self.kerfMmCustom = 0
        if settings:
            self.kerfMmCustom = float(settings['KerfMmCustom'])   
        
        self.lengthMm = '0.0 mm'
        if settings:
            self.lengthMm = settings['LengthMm']

        self.widthMm = '0.0 mm'            
        if settings:
            self.widthMm = settings['WidthMm']

        self.lengthIn = '0.0 in'
        if settings:
            self.lengthIn = settings['LengthIn']

        self.widthIn = '0.0 in'
        if settings:
            self.widthIn = settings['WidthIn']
        


    def CreateCommandInputs(self, inputs: adsk.core.CommandInputs):
        global skipValidate
        skipValidate = True

        # Create the command inputs to define the contents of the command dialog.

        self.selectInput = inputs.addSelectionInput('SelectionEventsSample', 'Faces', 'Please select faces to map')
        self.selectInput.addSelectionFilter(adsk.core.SelectionCommandInput.PlanarFaces)
        self.selectInput.setSelectionLimits(maximum=100, minimum=0)


        self.standardDropDownInput = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
        if self.standard == "Imperial":
            self.standardDropDownInput.listItems.add('Imperial', True)
            self.standardDropDownInput.listItems.add('Metric', False)
        else:
            self.standardDropDownInput.listItems.add('Imperial', False)
            self.standardDropDownInput.listItems.add('Metric', True)         
        
        self.kerfInListInput = inputs.addDropDownCommandInput('kerfIn', 'Kerf', adsk.core.DropDownStyles.TextListDropDownStyle)
        if self.kerfIn == '1/8 in':
            self.kerfInListInput.listItems.add('1/8 in', True)
        else:
            self.kerfInListInput.listItems.add('1/8 in', False)

        if self.kerfIn == '3/32 in':
            self.kerfInListInput.listItems.add('3/32 in', True)
        else:
            self.kerfInListInput.listItems.add('3/32 in', False)

        if self.kerfIn == '1/16 in':
            self.kerfInListInput.listItems.add('1/16 in', True)
        else:
            self.kerfInListInput.listItems.add('1/16 in', False)

        if self.kerfIn == 'Custom':
            self.kerfInListInput.listItems.add('Custom', True)
        else:
            self.kerfInListInput.listItems.add('Custom', False)

        self.kerfInCustomValueInput = inputs.addValueInput('kerfInCustom', 'Custom Kerf', 'in', adsk.core.ValueInput.createByReal(self.kerfInCustom))
        if self.kerfIn != 'Custom':
            self.kerfInCustomValueInput.isVisible = False

        self.kerfMmListInput = inputs.addDropDownCommandInput('kerfMm', 'Kerf', adsk.core.DropDownStyles.TextListDropDownStyle)
        if self.kerfMm == '3.175 mm':
            self.kerfMmListInput.listItems.add('3.175 mm', True)
        else:
            self.kerfMmListInput.listItems.add('3.175 mm', False)

        if self.kerfMm == '2.381 mm':
            self.kerfMmListInput.listItems.add('2.381 mm', True)
        else:
            self.kerfMmListInput.listItems.add('2.381 mm', False)

        if self.kerfMm == '1.588 mm':
            self.kerfMmListInput.listItems.add('1.588 mm', True)
        else:
            self.kerfMmListInput.listItems.add('1.588 mm', False)

        if self.kerfMm == 'Custom':
            self.kerfMmListInput.listItems.add('Custom', True)
        else:
            self.kerfMmListInput.listItems.add('Custom', False)

        self.kerfMmCustomValueInput = inputs.addValueInput('kerfMmCustom', 'Custom Kerf', 'mm', adsk.core.ValueInput.createByReal(self.kerfMmCustom))
        if self.kerfMm != 'Custom':
            self.kerfMmCustomValueInput.isVisible = False
                    
        self.lengthInValueInput = inputs.addValueInput('lengthIn', 'Stock Length', 'in', adsk.core.ValueInput.createByString(self.lengthIn))   

        self.widthInValueInput = inputs.addValueInput('widthIn', 'Stock Width', 'in', adsk.core.ValueInput.createByString(self.widthIn))   
        
        self.lengthMmValueInput = inputs.addValueInput('lengthMm', 'Stock Length', 'mm', adsk.core.ValueInput.createByString(self.lengthMm))   

        self.widthMmValueInput = inputs.addValueInput('widthMm', 'Stock Width', 'mm', adsk.core.ValueInput.createByString(self.widthMm))   
        
        if self.standard == 'Imperial':
            self.kerfMmListInput.isVisible = False
            self.lengthMmValueInput.isVisible = False
            self.widthMmValueInput.isVisible = False
        elif self.standard == 'Metric':
            self.kerfInListInput.isVisible = False
            self.lengthInValueInput.isVisible = False
            self.widthInValueInput.isVisible = False
        
        self.errorMessageTextInput = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
        self.errorMessageTextInput.isFullWidth = True

        skipValidate = False


    def HandleInputsChanged(self, args: adsk.core.InputChangedEventArgs):
        changedInput = args.input
        
        if not skipValidate:
            if changedInput.id == 'standard':
                if self.standardDropDownInput.selectedItem.name == 'Imperial':
                    self.kerfMmListInput.isVisible = False
                    self.lengthMmValueInput.isVisible = False
                    self.widthMmValueInput.isVisible = False
                    self.kerfInListInput.isVisible = True
                    self.lengthInValueInput.isVisible = True
                    self.widthInValueInput.isVisible = True
                    self.units = 'in'
                elif self.standardDropDownInput.selectedItem.name == 'Metric':
                    self.kerfMmListInput.isVisible = True
                    self.lengthMmValueInput.isVisible = True
                    self.widthMmValueInput.isVisible = True
                    self.kerfInListInput.isVisible = False
                    self.lengthInValueInput.isVisible = False
                    self.widthInValueInput.isVisible = False
                    self.units = 'mm'
                   
                
            # Update the pitch diameter value.
            length = None
            width = None
            if self.standardDropDownInput.selectedItem.name == 'Imperial':
                if self.lengthInValueInput.isValidExpression:
                    length = self.lengthInValueInput.value
                if self.widthInValueInput.isValidExpression:
                    width = self.widthInValueInput.value
            elif self.standardDropDownInput.selectedItem.name == 'Metric':
                if self.lengthMmValueInput.isValidExpression:
                    length = self.lengthMmValueInput.value
                if self.widthMmValueInput.isValidExpression:
                    width = self.widthMmValueInput.value
           

            if changedInput.id == 'kerfIn':
                if self.kerfInListInput.selectedItem.name == 'Custom':
                    self.kerfInCustomValueInput.isVisible = True
                else:
                    self.kerfInCustomValueInput.isVisible = False         

            if changedInput.id == 'kerfMm':
                if self.kerfMmListInput.selectedItem.name == 'Custom':
                    self.kerfMmCustomValueInput.isVisible = True
                else:
                    self.kerfMmCustomValueInput.isVisible = False             


    def HandleValidateInputs(self, args: adsk.core.ValidateInputsEventArgs):
        if not skipValidate:
            self.errorMessageTextInput.text = ''
                
            # Calculate some of the gear sizes to use in validation.
            if self.standardDropDownInput.selectedItem.name == 'Imperial':
                if self.lengthInValueInput.isValidExpression:
                    length = self.lengthInValueInput.value * 25.4
                else:
                    args.areInputsValid = False
                    self.errorMessageTextInput.text = 'The length is not valid.'
                    return
                if self.widthInValueInput.isValidExpression:
                    width = self.widthInValueInput.value * 25.4
                else:
                    args.areInputsValid = False
                    self.errorMessageTextInput.text = 'The width is not valid.'
                    return
            elif self.standardDropDownInput.selectedItem.name == 'Metric':
                if self.lengthMmValueInput.isValidExpression:
                    length = self.lengthMmValueInput
                else:
                    args.areInputsValid = False
                    self.errorMessageTextInput.text = 'The length is not valid.'
                    return
                if self.widthMmValueInput.isValidExpression:
                    width = self.widthMmValueInput
                else:
                    self.errorMessageTextInput.text = 'The width is not valid.'
                    args.areInputsValid = False
                    return
     
                    
            if self.kerfInListInput.selectedItem.name == 'Custom':
                kerf = self.kerfInCustomValueInput.value * 25.4
            else:
                if self.kerfInListInput.selectedItem.name == '1/8 in':
                    kerf = 3.175
                elif self.kerfInListInput.selectedItem.name == '3/32 in':
                    kerf = 2.381
                elif self.kerfInListInput.selectedItem.name == '1/16 in':
                    kerf = 1.588

            if self.kerfMmListInput.selectedItem.name == 'Custom':
                kerf = self.kerfInCustomValueInput.value 
            else:
                if self.kerfInListInput.selectedItem.name == '3.175 mm':
                    kerf = 3.175
                elif self.kerfInListInput.selectedItem.name == '2.381 mm':
                    kerf = 2.381
                elif self.kerfInListInput.selectedItem.name == '1.588 mm':
                    kerf = 1.588
            

    def HandleExecute(self, args: adsk.core.CommandEventArgs):
        if self.standardDropDownInput.selectedItem.name == 'Imperial':     
            length = self.lengthInValueInput.value * 25.4 
            width = self.widthInValueInput.value * 25.4     
        elif self.standardDropDownInput.selectedItem.name == 'Metric':
            length = self.lengthMmValueInput.value 
            width = self.widthMmValueInput.value 
        
        # Save the current values as attributes.
        settings = {'Standard': self.standardDropDownInput.selectedItem.name,
                    'KerfIn': self.kerfInListInput.selectedItem.name,
                    'KerfInCustom': str(self.kerfInCustomValueInput.value),
                    'KerfMm': self.kerfMmListInput.selectedItem.name,
                    'KerfMmCustom': str(self.kerfMmCustomValueInput.value),
                    'LengthMm': str(self.lengthMmValueInput.value),
                    'WidthMm': str(self.widthMmValueInput.value),
                    'LengthIn': str(self.lengthInValueInput.value),
                    'WidthIn': str(self.widthInValueInput.value)}

        jsonSettings = json.dumps(settings)

        for i in range(self.selectInput.selectionCount):
            bound = self.selectInput.selection(i).entity.geometry.evaluator.parametricRange()
            futil.log(f"{bound}")

            # these values are not saved, only printed.
            futil.log(f"max point = {bound.maxPoint.x},{bound.maxPoint.y}")
            futil.log(f"min point = {bound.minPoint.x},{bound.minPoint.y}")


        des = adsk.fusion.Design.cast(app.activeProduct)
        attribs = des.attributes
        attribs.add('OptiCut', 'settings', jsonSettings)

        # Get the current values.
        if self.kerfInListInput.selectedItem.name == 'Custom':
            kerf = self.kerfInCustomValueInput.value * 25.4
        else:
            if self.kerfInListInput.selectedItem.name == '1/8 in':
                kerf = 3.175
            elif self.kerfInListInput.selectedItem.name == '3/32 in':
                kerf = 2.381
            elif self.kerfInListInput.selectedItem.name == '1/16 in':
                kerf = 1.588

        if self.kerfMmListInput.selectedItem.name == 'Custom':
            kerf = self.kerfMmCustomValueInput.value 
        else:
            if self.kerfMmListInput.selectedItem.name == '3.175 mm':
                kerf = 3.175
            elif self.kerfMmListInput.selectedItem.name == '2.381 mm':
                kerf = 2.381
            elif self.kerfMmListInput.selectedItem.name == '1.588 mm':
                kerf = 1.588






