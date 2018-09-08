import pandas as pd

from web_constants import *
from project_data import ProjectData, get_selected_project_data


def plot_samples(projects):
    result = []
    project_data = get_selected_project_data(projects)
    for proj in project_data:
        result += proj.get_samples_list()
    return result