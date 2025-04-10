from collections import defaultdict

# constants.py
GOVT_DOC_DIR_PATH = "policy_docs/gov"
HOSP_DOC_DIR_PATH = "policy_docs/hospital"
FOLDER_INDEX_FILE = "index.txt"
SUMMARIZE_PDF_FILE = (
    "Summarize this PDF file chunk keeping track of every important information"
)
CHECK_INCONSISTENCTIES = "Given two policies, check if anything in one goes against the other. If No then answer No. Else start answer with Yes and provide details "
PDF_PAGE_CHUNK_SIZE = 20
GOV_POLICY_SUMMARY_MAP = defaultdict(str)
HOS_POLICY_SUMMARY_MAP = defaultdict(str)
