from pathlib import Path


SRC = Path(__file__).parent
BLD = SRC.joinpath("..", "bld").resolve()
