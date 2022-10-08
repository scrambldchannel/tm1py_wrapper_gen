import configparser
from TM1py import TM1Service
from TM1py.Objects.Cube import Cube


config = configparser.ConfigParser()
config.read(r"config_local.ini")

tm1 = TM1Service(**config["planning-dev"])


def write_func(cube: Cube):

    cube_name = cube.name.lower().replace(" ", "_").replace("-", "_").replace("}", "_")

    params = ""
    intersection = ""

    for d in cube.dimensions:

        d_original_name = d

        if d[0].isnumeric():

            d = "_" + d

        d = d.lower().replace(" ", "_").replace("-", "_").replace("}", "_")
        
        params = params + f"{d.lower()}: str, " 
        intersection = intersection + "{" + d.lower() + "},"

    params = params.removesuffix(", ")
    intersection = intersection.removesuffix(",")

    measure_param = intersection.split(",")[-1].removeprefix("{").removesuffix("}")
    measures_dim = tm1.dimensions.get(d_original_name)

    string_measures = []
    for h in measures_dim.hierarchies:
        for el_name, el in h.elements.items():
            if el.element_type.__str__() == "String":
                string_measures.append(el_name)
    

    if string_measures:
        string_measures_string = "["
        return_type = "Union[float, str]"

        for m in string_measures:
            string_measures_string = string_measures_string + f'"{m}", '
    
        string_measures_string = string_measures_string + "]"
        
        return_statement = f"""if val is None:
        if {measure_param} in {string_measures_string}:
            val = ""
        else:
            val = 0
    
    return val"""
    
    else:
        return_type = "float"
        return_statement = """if val is None:
        val = 0
    
    return val"""




    return f'''
def get_value_{cube_name}(tm1: TM1Service, {params}) -> {return_type}:

    cube = "{cube_name}"

    intersection = f"{intersection}"

    val = tm1.cells.get_value(cube, intersection)

    {return_statement}
'''

imports = """from typing import Union
from TM1py import TM1Service
"""

print(imports)

for c in tm1.cubes.get_model_cubes():
    
    # write_func(c)
    print(write_func(c))



