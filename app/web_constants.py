import os
import re
from enum import Enum

OBJ_DIR = '../obj' if bool(os.environ.get("DEBUG", '')) else '/obj'

META_DATA_FILENAME = 'meta-data.tsv'
META_SIGS_FILENAME = 'meta-sigs.tsv'
GENES_AGG_FILENAME = 'computed-genes_agg.tsv'
ONCOTREE_FILENAME = 'oncotree-2018_11_01.json'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)
META_SIGS_FILE = os.path.join(OBJ_DIR, META_SIGS_FILENAME)
GENES_AGG_FILE = os.path.join(OBJ_DIR, GENES_AGG_FILENAME)
ONCOTREE_FILE = os.path.join(OBJ_DIR, ONCOTREE_FILENAME)


CAT_TYPES = [
  'SBS_96',
  'DBS_78',
  'INDEL_Alexandrov2018_83'
]

MUT_TYPES = [
  'SBS',
  'DBS',
  'INDEL'
]

MUT_TYPE_MAP = {
  'SBS': 'SBS_96',
  'DBS': 'DBS_78',
  'INDEL': 'INDEL_Alexandrov2018_83'
}

CAT_TYPE_MAP = dict([(val, key) for key, val in MUT_TYPE_MAP.items()])

# Regular Expressions
CHROMOSOME_RE = r'^(X|Y|M|[1-9]|1[0-9]|2[0-2])$'

# Column names for extended mutation tables
PATIENT = 'Patient'
SAMPLE = 'Sample'
CANCER_TYPE = 'Cancer Type'
PROVENANCE = 'Provenance'
COHORT = 'Cohort'
CHR = 'Chromosome'
POS_START = 'Start Position'
POS_END = 'End Position'
REF = 'Reference Sequence'
VAR = 'Variant Sequence'
GSTRAND = 'Genomic Strand' # Watson-Crick Strand
SEQ_TYPE = 'Sequencing Strategy'
MUT_TYPE = 'Mutation Type'
ASSEMBLY = 'Assembly Version'

MUT_CLASS = 'Mutation Classification'
GENE_SYMBOL = "Gene Symbol"

FPRIME = "5' Flanking Bases"
TPRIME = "3' Flanking Bases"
TSTRAND = 'Transcriptional Strand'
MUT_DIST = 'Distance to Previous Mutation'
NEAREST_MUT = 'Distance to Nearest Mutation'
MUT_DIST_ROLLING_MEAN = 'Rolling Mean of 6 Mutation Distances'
KATAEGIS = 'Kataegis'

# Column names for donor clinical data tables
TOBACCO_BINARY = 'Tobacco User'
TOBACCO_INTENSITY = 'Tobacco Intensity'
ALCOHOL_BINARY = 'Alcohol User'
ALCOHOL_INTENSITY = 'Alcohol Intensity'
DIAGNOSIS_AGE = 'Diagnosis Age'
SEX = 'Sex'
DIAGNOSIS_ICD10 = 'Diagnosis ICD10 Code'
VITAL_STATUS = 'Vital Status'
PRIOR_MALIGNANCY = 'Prior Malignancy'
NUM_RELATIVES_WITH_HISTORY = 'Number of Relatives with Cancer History'
FIRST_THERAPY_TYPE = 'First Therapy Type'
FIRST_THERAPY_RESPONSE = 'First Therapy Response'
SECOND_THERAPY_TYPE = 'Second Therapy Type'
SECOND_THERAPY_RESPONSE = 'Second Therapy Response'

CLINICAL_COLUMNS = [TOBACCO_BINARY, TOBACCO_INTENSITY, ALCOHOL_BINARY, ALCOHOL_INTENSITY, DIAGNOSIS_AGE, SEX]

CHROMOSOMES = {
  '1': 249250621,
  '2': 243199373,
  '3': 198022430,
  '4': 191154276,
  '5': 180915260,
  '6': 171115067,
  '7': 159138663,
  '8': 146364022,
  '9': 141213431,
  '10': 135534747,
  '11': 135006516,
  '12': 133851895,
  '13': 115169878,
  '14': 107349540,
  '15': 102531392,
  '16': 90354753,
  '17': 81195210,
  '18': 78077248,
  '19': 59128983,
  '20': 63025520,
  '21': 48129895,
  '22': 51304566,
  'X': 155270560,
  'Y': 59373566,
  'M': 16571
}

class MUT_CLASS_VALS(Enum):
  SILENT = "Silent"
  MISSENSE = "Missense"
  FRAMESHIFT = "Frameshift"
  SPLICE_SITE = "Splice Site"
  NONSENSE = "Nonsense"
  IN_FRAME_INDEL = "in-frame indel"
  OTHER = "Other mutation"
  NONSTOP = "Nonstop"
  TRANSLATION_START_SITE="Translation Start Site"


# Signatures columns
META_COL_SIG = 'Signature'
META_COL_ONCOTREE_CODE = 'Oncotree Code'
META_COL_CANCER_TYPE = 'Cancer Type'
META_COL_CAT_TYPE = 'Category Type'
META_COL_DESCRIPTION = 'Description'
META_COL_INDEX = 'Index'
META_COL_SIG_GROUP = 'Signature Group'
META_COL_PUBLICATION = 'Publication'
META_COL_PATH_SIGS_META = 'Path to Meta File'
META_COL_PATH_SIGS_DATA = 'Path to Signatures {cat_type} File'
META_COL_PATH_SIGS_CANCER_TYPE_MAP = 'Path to Cancer Type Map File'

META_COL_PATH_SIGS_DATA_LIST = [META_COL_PATH_SIGS_DATA.format(cat_type=val) for val in CAT_TYPES]

META_SIGS_FILE_COLS = [
  META_COL_PATH_SIGS_META,
  META_COL_PATH_SIGS_CANCER_TYPE_MAP
] + META_COL_PATH_SIGS_DATA_LIST

META_SIGS_COLS = [
  META_COL_SIG,
  META_COL_DESCRIPTION,
  META_COL_INDEX,
  META_COL_CAT_TYPE
]

META_CANCER_TYPE_MAP_COLS = [
  META_COL_SIG,
  META_COL_ONCOTREE_CODE,
  META_COL_CANCER_TYPE,
  META_COL_CAT_TYPE
]

# Mutation data columns
META_COL_PROJ = 'Project'
META_COL_PROJ_SOURCE = 'Project Source'
META_COL_PROJ_NAME = 'Project Name'
META_COL_PATH_MUTS_EXTENDED = 'Path to Extended {mut_type} File'
META_COL_PATH_MUTS_COUNTS = 'Path to Counts {cat_type} File'
META_COL_PATH_CLINICAL = 'Path to Clinical File'
META_COL_PATH_SAMPLES = 'Path to Samples File'
META_COL_PATH_GENES = 'Path to Genes File'

META_COL_PATH_MUTS_EXTENDED_LIST = [META_COL_PATH_MUTS_EXTENDED.format(mut_type=val) for val in MUT_TYPES]
META_COL_PATH_MUTS_COUNTS_LIST = [META_COL_PATH_MUTS_COUNTS.format(cat_type=val) for val in CAT_TYPES]

META_DATA_FILE_COLS = [
  META_COL_PATH_CLINICAL,
  META_COL_PATH_SAMPLES,
  META_COL_PATH_GENES
] + META_COL_PATH_MUTS_EXTENDED_LIST + META_COL_PATH_MUTS_COUNTS_LIST
