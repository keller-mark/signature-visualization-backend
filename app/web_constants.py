import os
import re

OBJ_DIR = '../obj' if bool(os.environ.get("DEBUG", '')) else '/obj'
DATA_DIR = 'data'
DATA_META_FILE = os.path.join(DATA_DIR, 'meta.tsv')
CHROMOSOME_BANDS_FILE = os.path.join(DATA_DIR, 'chromosome_bands.tsv')
GENE_LIST_FILE = os.path.join(OBJ_DIR, 'gene_list.pickle')

CATEGORY_TYPES = {
  'SBS': ['SBS_96', 'SBS_6'],
  'DBS': ['DBS_78', 'DBS_10'], 
  'INDEL': ['INDEL_Alexandrov2018_83', 'INDEL_Alexandrov2018_16']
}

SIG_TYPES = {
  'SBS': 'SBS_96',
  'DBS': 'DBS_78',
  'INDEL': 'INDEL_Alexandrov2018_83'
}

MUT_TYPES = SIG_TYPES.keys()

SIGS_DIR = os.path.join(DATA_DIR, 'sigs')
SIGS_FILE_SUFFIX = '_signatures.tsv'
SIGS_META_FILE_SUFFIX = '_signatures_meta.tsv'
SIGS_PER_CANCER_TYPE_FILE = os.path.join(SIGS_DIR, 'per_cancer_type.yaml')

# Regular Expressions
CHROMOSOME_RE = r'^(X|Y|M|[1-9]|1[0-9]|2[0-2])$'
PROJ_RE = r'^[A-Z0-9]+-[A-Z0-9]+-[A-Z]+$'

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

CLINICAL_VARIABLES = [TOBACCO_BINARY, TOBACCO_INTENSITY, ALCOHOL_BINARY]

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
