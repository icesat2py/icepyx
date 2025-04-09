<<<<<<< HEAD
import sys
sys.path.append("/home/jovyan/")

from icepyx_personal.icepyx.core.query import Query, GenQuery
from icepyx_personal.icepyx.core.read import Read
from icepyx_personal.icepyx.quest.quest import Quest
=======
from warnings import warn

deprecation_msg = """icepyx v1.x is being deprecated; the back-end systems on which it relies
will be shut down as of late 2024. At that time, upgrade to icepyx v2.x, which uses the
new NASA Harmony back-end, will be required. Please see
<https://icepyx.readthedocs.io/en/latest/user_guide/changelog/v1.3.0.html> for more
information!
"""
# IMPORTANT: This is being done before the other icepyx imports because the imported
# code changes warning filters. If this is done after the imports, the warning won't
# work.
warn(deprecation_msg, FutureWarning, stacklevel=2)

>>>>>>> 386d73f69512d13ebb92ef32bb9e83006ada29f1

from _icepyx_version import version as __version__

from icepyx.core.query import GenQuery, Query
from icepyx.core.read import Read
from icepyx.core.variables import Variables
from icepyx.quest.quest import Quest
