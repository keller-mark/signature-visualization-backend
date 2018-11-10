import pandas as pd
import numpy as np
import pickle

from web_constants import *
from signatures import Signatures, get_signatures_by_mut_type
from project_data import ProjectData, get_selected_project_data

clinical_scales = {
    TOBACCO_BINARY: ["Smoker", "Non-Smoker"], 
    TOBACCO_INTENSITY: [0, 100], 
    ALCOHOL_BINARY: ["Alcohol User", "Alcohol Nonuser"], 
    ALCOHOL_INTENSITY: [0, 100], 
    DIAGNOSIS_AGE: [0, 100], 
    SEX: ["male", "female"]
}

def scale_clinical_track(clinical_var, projects):
    return clinical_scales[clinical_var]
  

