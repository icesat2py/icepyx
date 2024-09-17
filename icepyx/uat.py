import os
from typing import Final

# HACK: For testing with UAT, we need a token to authorize ourselves to see the
#       private collections we want to test with.
EDL_ACCESS_TOKEN: Final = os.environ["EDL_TOKEN"]
