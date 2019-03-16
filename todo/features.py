HAS_AUTOCOMPLETE = True
try:
    import dal
except ImportError:
    HAS_AUTOCOMPLETE = False

HAS_TASK_MERGE = False
if HAS_AUTOCOMPLETE:
    import dal.autocomplete
    if getattr(dal.autocomplete, 'Select2QuerySetView', None) is not None:
        HAS_TASK_MERGE = True
