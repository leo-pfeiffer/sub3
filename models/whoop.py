from dataclasses import dataclass
from datetime import datetime


DATETIME_STRING_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass
class WhoopCycle:
    start_time: datetime
    end_time: datetime
    cycle_timezone: str
    recovery_score: int
    resting_heart_rate: int
    heart_rate_variability: int
    skin_temp: float
    blood_oxygen: float
    day_strain: float
    energy_burned: int
    max_hr: int
    avg_hr: int
    sleep_onset: datetime
    wake_onset: datetime
    sleep_performance: int
    respiratory_rate: float
    asleep_duration: int
    in_bed_duration: int
    light_sleep_duration: int
    deep_sleep_duration: int
    rem_duration: int
    awake_duration: int
    sleep_need: int
    sleep_debt: int
    sleep_efficiency: int
    sleep_consistency: int

    def __init__(
        self,
        start_time,
        end_time,
        cycle_timezone,
        recovery_score,
        resting_heart_rate,
        heart_rate_variability,
        skin_temp,
        blood_oxygen,
        day_strain,
        energy_burned,
        max_hr,
        avg_hr,
        sleep_onset,
        wake_onset,
        sleep_performance,
        respiratory_rate,
        asleep_duration,
        in_bed_duration,
        light_sleep_duration,
        deep_sleep_duration,
        rem_duration,
        awake_duration,
        sleep_need,
        sleep_debt,
        sleep_efficiency,
        sleep_consistency,
    ):
        self.start_time = (
            datetime.strptime(start_time, DATETIME_STRING_FORMAT)
            if start_time
            else None
        )
        self.end_time = (
            datetime.strptime(end_time, DATETIME_STRING_FORMAT) if end_time else None
        )
        self.cycle_timezone = str(cycle_timezone) if cycle_timezone else None
        self.recovery_score = int(recovery_score) if recovery_score else None
        self.resting_heart_rate = (
            int(resting_heart_rate) if resting_heart_rate else None
        )
        self.heart_rate_variability = (
            int(heart_rate_variability) if heart_rate_variability else None
        )
        self.skin_temp = float(skin_temp) if skin_temp else None
        self.blood_oxygen = float(blood_oxygen) if blood_oxygen else None
        self.day_strain = float(day_strain) if day_strain else None
        self.energy_burned = int(energy_burned) if energy_burned else None
        self.max_hr = int(max_hr) if max_hr else None
        self.avg_hr = int(avg_hr) if avg_hr else None
        self.sleep_onset = (
            datetime.strptime(sleep_onset, DATETIME_STRING_FORMAT)
            if sleep_onset
            else None
        )
        self.wake_onset = (
            datetime.strptime(wake_onset, DATETIME_STRING_FORMAT)
            if wake_onset
            else None
        )
        self.sleep_performance = int(sleep_performance) if sleep_performance else None
        self.respiratory_rate = float(respiratory_rate) if respiratory_rate else None
        self.asleep_duration = int(asleep_duration) if asleep_duration else None
        self.in_bed_duration = int(in_bed_duration) if in_bed_duration else None
        self.light_sleep_duration = (
            int(light_sleep_duration) if light_sleep_duration else None
        )
        self.deep_sleep_duration = (
            int(deep_sleep_duration) if deep_sleep_duration else None
        )
        self.rem_duration = int(rem_duration) if rem_duration else None
        self.awake_duration = int(awake_duration) if awake_duration else None
        self.sleep_need = int(sleep_need) if sleep_need else None
        self.sleep_debt = int(sleep_debt) if sleep_debt else None
        self.sleep_efficiency = int(sleep_efficiency) if sleep_efficiency else None
        self.sleep_consistency = int(sleep_consistency) if sleep_consistency else None
