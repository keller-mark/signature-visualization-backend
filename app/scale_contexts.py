import pandas as pd
import numpy as np

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data


def scale_contexts(chosen_sigs, mut_type):
    result = []

    signatures = get_signatures_by_mut_type({mut_type: chosen_sigs})[mut_type]
    
    if len(signatures.get_chosen_names()) > 0:
        result = signatures.get_contexts()

    return result