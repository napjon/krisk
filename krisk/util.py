
import os
from copy import deepcopy

def join_current_dir(file):
    cwd = os.path.dirname(__file__)
    return os.path.join(cwd, file)


def round_list(arr):
    try:
        return arr.values.round(3).tolist()  # Numeric Array
    except TypeError:
        try:
            return arr.unique().tolist()  #String Array
        except AttributeError:
            return (arr.apply(lambda x: x.values.round(3)  #Dataframe
                              if x.dtype.name.startswith('float') else x)
                    .values.tolist())
        
def get_series_data(data,x, chart_type, cat=None):
    elem_series = {'name': '', 'type': chart_type, 'data': []}
    series = deepcopy(elem_series)
    series['data'] = round_list(data)
    series['type'] = chart_type
    series['name'] = cat if cat else x
    
    return series