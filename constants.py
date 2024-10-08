from datetime import datetime

PLAN_START_DATE = datetime(2024, 7, 1)
SLOWEST_SUPPORTED_PACE = 15
DURATIONS = [5, 10, 12, 20, 30, 60, 120, 360, 600, 720, 1800, 3600, 5400]
DISTANCE_NAMES = {
    800: "800 m",
    1000: "1 km",
    1609: "1 mi",
    5000: "5 km",
    10000: "10 km",
    16093: "10 mi",
    21098: "HM",
    30000: "30 km",
    42195: "M"
}