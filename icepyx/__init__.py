from warnings import warn

deprecation_msg = """icepyx v1.x is deprecated; the back-end systems on which is relies
are being shut down. Please upgrade to icepyx v2.x which uses the new NASA Harmony
back-end.
"""
# IMPORTANT: This is being done before the other icepyx imports because the imported
# code changes warning filters. If this is done after the imports, the warning won't
# work.
warn(deprecation_msg, DeprecationWarning, stacklevel=2)


from _icepyx_version import version as __version__

from icepyx.core.query import GenQuery, Query
from icepyx.core.read import Read
from icepyx.core.variables import Variables
from icepyx.quest.quest import Quest
