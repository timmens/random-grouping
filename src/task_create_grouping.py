from src.config import BLD
from src.config import SRC
from src.read_and_write import read_config_kwargs
from src.read_and_write import read_grouping_df
from src.read_and_write import read_names_df
from src.read_and_write import update_grouping_df_file
from src.read_and_write import write_pick
from src.shared import draw_groupings
from src.shared import extract_current_members
from src.shared import pick_best_candidate


def main():  # noqa: D103
    # create new grouping
    depends_on = {
        "config": SRC / "config.yaml",
        "names": SRC / "data" / "names.csv",
        "groupings": SRC / "data" / "previous_groupings.csv",
    }
    produces = BLD / "grouping.txt"

    kwargs = read_config_kwargs(depends_on["config"])

    names = read_names_df(depends_on["names"])
    members = extract_current_members(names)

    grouping_df = read_grouping_df(depends_on["groupings"], names)
    candidates = draw_groupings(members, **kwargs)

    updated_grouping_df, minimum = pick_best_candidate(candidates, grouping_df)

    update_grouping_df_file(updated_grouping_df, depends_on["groupings"])
    write_pick(minimum, names, produces)

    # versioning


if __name__ == "__main__":
    main()
