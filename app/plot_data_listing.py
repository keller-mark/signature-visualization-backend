import os
from yaml import load
from yaml import Loader
from web_constants import *
from signatures import Signatures
from project_data import ProjectData, get_all_project_data_as_json


def get_signatures_per_cancer_type():
    if not os.path.isfile(SIGS_PER_CANCER_TYPE_FILE):
      return None
    with open(SIGS_PER_CANCER_TYPE_FILE) as data_file:  
      active_sigs = load(data_file, Loader=Loader)
    result = []
    # TEMPORARY, in future just use TSV files already formatted in this way from obj store
    for sig_group in active_sigs:
      for ct in sig_group["cancer-types"]:
        for mut_type, sigs in ct["signatures"].items():
          cat_type = ""
          if mut_type == "SBS":
            cat_type = "SBS_96"
          elif mut_type == "DBS":
            cat_type = "DBS_78"
          elif mut_type == "INDEL":
            cat_type = "INDEL_Alexandrov2018_83"
          for sig in sigs:
            result.append({
              "Signature": sig,
              "Cancer Type": ct["name"],
              "Category Type": cat_type,
              "Mutation Type": mut_type,
              "Source": sig_group["group"]
            })
    return result


def plot_data_listing():
    # instantiate a signatures object for each signature type
    signature_types = dict([(mut_type, Signatures(sig_type)) for mut_type, sig_type in SIG_TYPES.items()])
    return {
      "projects": get_all_project_data_as_json(),
      "signatures": dict([(mt, st.get_metadata()) for mt, st in signature_types.items()]),
      "cancer_type_map": get_signatures_per_cancer_type()
    }