from typing import Dict, List, Tuple, Iterable, Optional
from dataclasses import dataclass

@dataclass
class TransformConfig:
    # horizons in days for direct multi-horizon training
    horizons: Tuple[int, ...] = (1, 3, 7, 14)
    # how many lag days/rolling windows to compute
    lag_days: Tuple[int, ...] = (1, 2, 3, 7, 14, 28)
    roll_windows: Tuple[int, ...] = (7, 14, 28)
    fourier_K: int = 2
    # min rows required per player to build features safely
    min_history_rows: int = 40
    # whether to include player_id as a categorical (works best with CatBoost; LightGBM needs care)
    include_player_id: bool = True

class Transform:
    def __init__(self, cfg: Optional[TransformConfig] = None):
        self.cfg = cfg or TransformConfig()

