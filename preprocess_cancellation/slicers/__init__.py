from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

from ..layers import LayerFilter
from .cura import preprocess_cura_to_klipper
from .ideamaker import preprocess_ideamaker_to_klipper
from .m486 import preprocess_m486_to_klipper
from .slic3r import preprocess_slicer_to_klipper

if TYPE_CHECKING:
    from typing import Callable, Dict, Generator, Optional, Tuple

    from mypy_extensions import Arg, DefaultNamedArg, NamedArg

    Preprocessor = Callable[
        [
            Arg(io.TextIOBase, "infile"),
            DefaultNamedArg(bool, "use_shapely"),
            NamedArg(LayerFilter, "layer_filter"),
        ],
        Generator[str, None, None],
    ]


logger = logging.getLogger(__name__)


# Note:
#   Slic3r:     does not output any markers into GCode
#   Kisslicer:  does not output any markers into GCode
#   Kiri:Moto:  does not output any markers into GCode
#   Simplify3D: I was unable to figure out multiple processes
SLICERS: Dict[
    str,
    Tuple[str, Preprocessor],
] = {
    "m486": ("M486", preprocess_m486_to_klipper),
    "superslicer": ("; generated by SuperSlicer", preprocess_slicer_to_klipper),
    "prusaslicer": ("; generated by PrusaSlicer", preprocess_slicer_to_klipper),
    "slic3r": ("; generated by Slic3r", preprocess_slicer_to_klipper),
    "cura": (";Generated with Cura_SteamEngine", preprocess_cura_to_klipper),
    "ideamaker": (";Sliced by ideaMaker", preprocess_ideamaker_to_klipper),
}


def identify_slicer_marker(line: str) -> Optional[Preprocessor]:
    for name, (marker, processor) in SLICERS.items():
        if line.strip().startswith(marker):
            logger.debug("Identified slicer %s", name)
            return processor

    return None