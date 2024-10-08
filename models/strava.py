from dataclasses import dataclass
from datetime import datetime


@dataclass
class MinimalRun:
    start_time: datetime
    distance: float
