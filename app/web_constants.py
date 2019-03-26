import os
import re
from enum import Enum

OBJ_DIR = '../obj' if bool(os.environ.get("DEBUG", '')) else '/obj'

META_DATA_FILENAME = 'meta-data.tsv'
META_SIGS_FILENAME = 'meta-sigs.tsv'
META_PATHWAYS_FILENAME = 'meta-pathways.tsv'
META_FEATURED_FILENAME = 'meta-featured.tsv'
META_CLINICAL_FILENAME = 'meta-clinical.tsv'
META_TRICOUNTS_FILENAME = 'meta-tricounts.tsv'

ONCOTREE_FILENAME = 'oncotree-2018_11_01.json'
GENES_AGG_FILENAME = 'computed-genes_agg-{letter}.tsv'
SAMPLES_AGG_FILENAME = 'computed-samples_agg.tsv'
PROJ_TO_SIGS_FILENAME = 'computed-oncotree_proj_to_sigs_per_group.tsv'

META_DATA_FILE = os.path.join(OBJ_DIR, META_DATA_FILENAME)
META_SIGS_FILE = os.path.join(OBJ_DIR, META_SIGS_FILENAME)
META_PATHWAYS_FILE = os.path.join(OBJ_DIR, META_PATHWAYS_FILENAME)
META_FEATURED_FILE = os.path.join(OBJ_DIR, META_FEATURED_FILENAME)
META_CLINICAL_FILE = os.path.join(OBJ_DIR, META_CLINICAL_FILENAME)
META_TRICOUNTS_FILE = os.path.join(OBJ_DIR, META_TRICOUNTS_FILENAME)

GENES_AGG_FILE = os.path.join(OBJ_DIR, GENES_AGG_FILENAME)
SAMPLES_AGG_FILE = os.path.join(OBJ_DIR, SAMPLES_AGG_FILENAME)
ONCOTREE_FILE = os.path.join(OBJ_DIR, ONCOTREE_FILENAME)
PROJ_TO_SIGS_FILE = os.path.join(OBJ_DIR, PROJ_TO_SIGS_FILENAME)


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
GSTRAND = 'Genomic Strand'
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

# Special clinical variables
ICD_O_3_SITE_CODE = 'ICD-O-3 Site Code'
ICD_O_3_SITE_DESC = 'ICD-O-3 Site Description'
ICD_O_3_HISTOLOGY_CODE = 'ICD-O-3 Histology Code'
ICD_O_3_HISTOLOGY_DESC = 'ICD-O-3 Histology Description'
SURVIVAL_DAYS_TO_DEATH = 'Days to Death'
SURVIVAL_DAYS_TO_LAST_FOLLOWUP = 'Days to Last Followup'

# Column names for gene expression tables
GENE_EXPRESSION_RNA_SEQ_MRNA_Z = 'RNA Seq v2 mRNA median Zscore'


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
META_COL_PATH_MUTS_COUNTS = 'Path to Counts {cat_type} File'
META_COL_PATH_CLINICAL = 'Path to Clinical File'
META_COL_PATH_SAMPLES = 'Path to Samples File'
META_COL_PATH_GENE_MUT = 'Path to Gene Mutation File'
META_COL_PATH_GENE_EXP = 'Path to Gene Expression File'
META_COL_PATH_GENE_CNA = 'Path to Gene CNA File'

META_COL_PATH_MUTS_COUNTS_LIST = [META_COL_PATH_MUTS_COUNTS.format(cat_type=val) for val in CAT_TYPES]

META_DATA_FILE_COLS = [
  META_COL_PATH_CLINICAL,
  META_COL_PATH_SAMPLES,
  META_COL_PATH_GENE_MUT,
  META_COL_PATH_GENE_EXP,
  META_COL_PATH_GENE_CNA
] + META_COL_PATH_MUTS_COUNTS_LIST

# Pathways data columns
META_COL_PATHWAYS_GROUP = 'Pathways Group'
META_COL_PATH_PATHWAYS = 'Path to Pathways File'

META_PATHWAYS_FILE_COLS = [
  META_COL_PATH_PATHWAYS
]

# Clinical variables columns
META_COL_CLINICAL_COL = 'Clinical Column'
META_COL_CLINICAL_SCALE_TYPE = 'Scale Type'
META_COL_CLINICAL_EXTENT = 'Extent'
META_COL_CLINICAL_VALUE = 'Value'

# Tri-counts data columns
META_COL_TRICOUNTS_METHOD = 'Method'
META_COL_PATH_TRICOUNTS = 'Path to Trinucleotide Counts File'

META_TRICOUNTS_FILE_COLS = [
  META_COL_PATH_TRICOUNTS
]