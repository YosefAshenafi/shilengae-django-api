from model_utils import Choices

# The type of this AD
TYPE = Choices('REGULAR', 'PROMOTED')
REPORT_CATEGORIES = Choices(
    'HARASSMENT', 
    'INADEQUATE LANGUAGE', 
    'FAKE',
    'FRAUD',
    'OVERCHARGED',
    'DUPLICATE',
    'ILLEGAL'
)