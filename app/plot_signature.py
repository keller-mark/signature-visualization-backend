import pandas as pd
import numpy as np
from web_constants import *
from signatures import Signatures


def plot_signature(name, sig_type):
    signatures = Signatures(sig_type)
    return signatures.get_sig_as_dict(name)