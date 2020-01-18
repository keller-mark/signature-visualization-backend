import pandas as pd

from web_constants import *
from project_data import ProjectData, get_selected_project_data


def scale_samples(projects):
    project_data = get_selected_project_data(projects)
    result_series = pd.concat([proj.get_counts_sum_series() for proj in project_data])
    result_series = result_series.sort_values(ascending=False)
    return list(result_series.index.values)