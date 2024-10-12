from enum import Enum


class ExerciseName(Enum):
    BENCH_PRESS = "Bench Press (Barbell)"
    DEADLIFT_TRAP_BAR = "Deadlift (Trap bar)"
    BOX_SQUAT = "Box Squat (Barbell)"
    PULL_UP_WEIGHTED = "Pull Up (Weighted)"


class HeartRateZone(Enum):
    ZONE_1 = "Zone 1", 0, 123
    ZONE_2 = "Zone 2", 124, 153
    ZONE_3 = "Zone 3", 154, 169
    ZONE_4 = "Zone 4", 170, 184
    ZONE_5 = "Zone 5", 185, 197

    def __init__(self, _, min_hr, max_hr):
        self.min_hr = min_hr
        self.max_hr = max_hr

    @staticmethod
    def zone(hr: int):
        """
        For a given heart rate, return the zone it falls into.
        """
        for zone in HeartRateZone:
            if zone.min_hr <= hr <= zone.max_hr:
                return zone
        return None


class PaceZone(Enum):
    ZONE_1 = "Zone 1", "> 8:36 min/mi", "> 5:21 min/km", 0, 3.12
    ZONE_2 = "Zone 2", "7:36 - 8:36 min/mi", "4:43 - 5:21 min/km", 3.12, 3.53
    ZONE_3 = "Zone 3", "7:04 - 7:35 min/mi", "4:23 - 4:42 min/km", 3.53, 3.8
    ZONE_4 = "Zone 4", "6:40 - 7:03 min/mi", "4:08 - 4:22 min/km", 3.8, 4.02
    ZONE_5 = "Zone 5", "< 6:40 min/mi", "< 4:08 min/km", 4.02, 1000

    def __init__(self, _, min_mi, min_km, min_speed, max_speed):
        self.min_mi = min_mi
        self.min_km = min_km
        self.min_speed = min_speed
        self.max_speed = max_speed

    @staticmethod
    def zone(speed: float):
        """
        For a given speed (m/s), return the zone it falls into.
        """
        for zone in PaceZone:
            if zone.min_speed <= speed <= zone.max_speed:
                return zone
        return None


class RecoveryZone(Enum):
    RED = "Red", 0, 33
    YELLOW = "Yellow", 34, 66
    GREEN = "Green", 67, 100

    def __init__(self, _, min_percent, max_percent):
        self.min_percent = min_percent
        self.max_percent = max_percent

    @staticmethod
    def zone(percent: int):
        """
        For a given percentage, return the zone it falls into.
        """
        for zone in RecoveryZone:
            if zone.min_percent <= percent <= zone.max_percent:
                return zone
        return None
