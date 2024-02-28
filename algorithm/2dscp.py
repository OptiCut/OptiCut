"""
2D Stock Cutting Problem: Finding Optimized Solution that Minimizes the Waste
Based on the work of @Author: Emad Ehsan 
at @Github: https://github.com/emadehsan/csp/blob/master/deployment/stock_cutter.py
More code implement at https://stackoverflow.com/questions/76547575/how-can-i-distinguish-between-right-and-wrong-solutions-in-2d-cutting-stock-prob
"""
import collections
import json
from ortools.sat.python import cp_model


def StockCutter(child_rects, parent_rects, output_json=True):

    # Create the model
    model = cp_model.CpModel()

    horizon = parent_rects[0] 
    # total_parent_area = horizon[0] * horizon[1] 
    sheet_type = collections.namedtuple('sheet_type', 'x1 y1 x2 y2 x_interval y_interval is_extra')

    # Store for all model variables
    all_vars = {}

    # sum of to save area of all small rects, to cut from parent rect
    total_child_area = 0

    # hold the widths (x) and heights (y) interval vars of each sheet
    x_intervals = []
    y_intervals = []

    # create model vars and intervals
    for rect_id, rect in enumerate(child_rects):
        width = rect[0]
        height = rect[1]
        area = width * height
        total_child_area += area

        suffix = '_%i_%i' % (width, height)

        x1_var = model.NewIntVar(0, horizon[0], 'x1' + suffix)
        x2_var = model.NewIntVar(0, horizon[0], 'x2' + suffix)
        x_interval_var = model.NewIntervalVar(x1_var, width, x2_var, 'x_interval' + suffix)

        y1_var = model.NewIntVar(0, horizon[1], 'y1' + suffix)
        y2_var = model.NewIntVar(0, horizon[1], 'y2' + suffix)
        y_interval_var = model.NewIntervalVar(y1_var, height, y2_var, 'y_interval' + suffix)

        x_intervals.append(x_interval_var)
        y_intervals.append(y_interval_var)

        all_vars[rect_id] = sheet_type(
            x1=x1_var, 
            y1=y1_var, 
            x2=x2_var, 
            y2=y2_var, 
            x_interval=x_interval_var,
            y_interval=y_interval_var,
            is_extra=False  # to keep track of 1x1 custom rects added in next step
        )

    for rect_id in range(len(child_rects)):
        model.Minimize(all_vars[rect_id].x1 + all_vars[rect_id].y1)
        model.Minimize(all_vars[rect_id].x2 + all_vars[rect_id].y2)
        model.Minimize(all_vars[rect_id].x1)
        model.Minimize(all_vars[rect_id].x2)
        model.Minimize(all_vars[rect_id].y1)
        model.Minimize(all_vars[rect_id].y2)

    model.AddNoOverlap2D(x_intervals, y_intervals)

    # Solve model
    solver = cp_model.CpSolver()

    status = solver.Solve(model)  # use for Optimization Problem
    singleSolution = getSingleSolution(solver, all_vars)
    int_solutions = [singleSolution]  # convert to array
    output = {
        "statusName": solver.StatusName(status),
        "numSolutions": '1',
        "numUniqueSolutions": '1',
        "solutions": int_solutions  # unique solutions
    }

    print('Time:', solver.WallTime())
    print('Status:', output['statusName'])
    print('Solutions found :', output['numSolutions'])
    print('Unique solutions: ', output['numUniqueSolutions'])

    if output_json:
        return json.dumps(output)        
    else:
        return int_solutions


def getSingleSolution(solver, all_vars):
    solution = []
    # extra coordinates of all rectangles for this solution 
    for rect_id in all_vars:
        rect = all_vars[rect_id]
        x1 = solver.Value(rect.x1)
        x2 = solver.Value(rect.x2)
        y1 = solver.Value(rect.y1)
        y2 = solver.Value(rect.y2)

        coords = [x1, y1, x2, y2]

        solution.append(coords)

    return solution


def str_solutions_to_int(str_solutions):

    int_solutions = []

    for idx, sol in enumerate(str_solutions):
        rect_strs = sol.split('-')
        rect_coords = []

        # convert each rectangle's coords to int
        for rect_str in rect_strs:
            coords_str = rect_str.split(',')
            coords = [int(c) for c in coords_str]
            rect_coords.append(coords)

        int_solutions.append(rect_coords)

    return int_solutions


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

        # hold the calculated solutions
        self.__solutions = []
        self.__unique_solutions = set()

    def on_solution_callback(self):
        self.__solution_count += 1

        rect_strs = []

        for rect_id in self.__variables:
            rect = self.__variables[rect_id]
            x1 = self.Value(rect.x1)
            x2 = self.Value(rect.x2)
            y1 = self.Value(rect.y1)
            y2 = self.Value(rect.y2)

            rect_str = f"{x1},{y1},{x2},{y2}"

            rect_strs.append(rect_str)    

        # sort the rectangles
        rect_strs = sorted(rect_strs)

        # single solution as a string
        solution_str = '-'.join(rect_strs)
        # print(solution_str)

        self.__solutions.append(solution_str)
        self.__unique_solutions.add(solution_str) # __unique_solutions is a set, so duplicates will get removed

    def solution_count(self):
        return self.__solution_count

    # returns all solutions  
    def get_solutions(self):
        return self.__solutions

    def get_unique_solutions(self):
        return list(self.__unique_solutions) # __unique_solutions is a Set, convert to list


def drawRectsFromCoords(rect_coords, parent_rects):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # TODO: to add support for multiple parent rects, update here
    xSize = parent_rects[0][0]
    ySize = parent_rects[0][1]

    # draw rectangle
    fig, ax = plt.subplots(1)
    plt.xlim(0,xSize)
    plt.ylim(0,ySize)
    plt.gca().set_aspect('equal', adjustable='box')

    # print coords
    coords = []
    colors = ['r', 'g', 'b', 'y', 'brown', 'black', 'violet', 'pink', 'gray', 'orange', 'b', 'y','b', 'y','b', 'y','b', 'y','r', 'g', 'b', 'y', 'brown', 'black', 'violet', 'pink', 'gray', 'orange', 'b', 'y','b', 'y','b', 'y','b', 'y']
    for idx, coords in enumerate(rect_coords):
        x1 = coords[0]
        y1 = coords[1]
        x2 = coords[2]
        y2 = coords[3]

        width = abs(x1-x2)
        height = abs(y1-y2)  # print(f"Rect#{idx}: {width}x{height}")

        # Create a Rectangle patch
        rect_shape = patches.Rectangle((x1,y1), width, height,facecolor=colors[idx])
        # Add the patch to the Axes
        ax.add_patch(rect_shape)
    plt.show()


# for testing
if __name__ == '__main__':

    child_rects1 = [    
        [15, 15],
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    
        [15, 15],    

    ]

    child_rects2 = [    
        [20, 15],
        [40, 15],    
        [50, 15],    
        [10, 15],    
        [15, 10],    
        [15, 15],    
        [40, 40],    
        [70, 30],    
        [40, 15],    
        [20, 10],    
        [50, 15],    
        [30, 60],    
        [70, 30],    
        [50, 15],    
        [40, 80],
        [40, 15],

    ]

    parent_rects = [[150, 120]]

    solutions = StockCutter(child_rects2, parent_rects, output_json=False) 
    for sol in solutions:
        print(sol)
        drawRectsFromCoords(sol, parent_rects)