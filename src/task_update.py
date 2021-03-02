from shutil import copyfile

import pytask

from src.config import BLD
from src.config import SRC


@pytask.mark.update_source
@pytask.mark.depends_on(BLD / "matchings_history.csv")
@pytask.mark.produces(SRC / "data" / "matchings_history.csv")
def task_update_source(depends_on, produces):  # noqa: D103
    copyfile(str(depends_on), str(produces))
