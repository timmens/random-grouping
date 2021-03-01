from src.config import BLD
from src.config import SRC
from src.read_and_write import read_config
from src.read_and_write import read_grouping_df
from src.read_and_write import read_names_df
from src.read_and_write import update_grouping_df_file
from src.read_and_write import write_pick
from src.shared import draw_groupings
from src.shared import extract_current_members
from src.shared import pick_best_candidate


def main():  # noqa: D103
    kwargs = read_config(SRC / "config.yaml")

    names = read_names_df(SRC / "data" / "names.csv")
    members = extract_current_members(names)

    grouping_df = read_grouping_df(BLD / "matchings_history.csv", names)
    candidates = draw_groupings(members, **kwargs)

    updated_grouping_df, minimum = pick_best_candidate(candidates, grouping_df)

    update_grouping_df_file(updated_grouping_df, BLD / "matchings_history.csv")
    write_pick(minimum, names, BLD / "matchings.txt")

    # write_user_output
    # perform_versioning


if __name__ == "__main__":
    main()
