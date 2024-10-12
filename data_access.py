import json

from data_utils import TcxUtils, HevyUtils, StravaUtils, WhoopUtils
from enums import HeartRateZone, PaceZone, ExerciseName, RecoveryZone
from utils import date_to_str

APP_DATA = "data/app_data.json"
TCX_PREFIX = "tcx__"
HEVY_PREFIX = "hevy__"
STRAVA_PREFIX = "strava__"
WHOOP_PREFIX = "whoop__"


class Reader:
    def __init__(self):
        self.data = self.read_json()

    @staticmethod
    def read_json():
        with open(APP_DATA, "r") as file:
            return json.load(file)

    def get_tcx(self, key):
        key = key if key.startswith(TCX_PREFIX) else TCX_PREFIX + key
        return self.data[key]

    def get_hevy(self, key):
        key = key if key.startswith(HEVY_PREFIX) else HEVY_PREFIX + key
        return self.data[key]

    def get_strava(self, key):
        key = key if key.startswith(STRAVA_PREFIX) else STRAVA_PREFIX + key
        return self.data[key]

    def get_whoop(self, key):
        key = key if key.startswith(WHOOP_PREFIX) else WHOOP_PREFIX + key
        return self.data[key]


class Writer:
    def __init__(self):
        self.data = {}
        self.tcx_utils = TcxUtils()
        self.hevy_utils = HevyUtils()
        self.strava_utils = StravaUtils()
        self.whoop_utils = WhoopUtils()

    def load_data(self):
        self.tcx_utils.load_data()
        self.hevy_utils.load_data()
        self.strava_utils.load_data()
        self.whoop_utils.load_data()

    def process_data(self):
        # TCX Data
        self._add_tcx(
            "week_start_dates",
            [date_to_str(d) for d in self.tcx_utils.week_start_dates()],
        )
        self._add_tcx("dates_str", self.tcx_utils.dates_str())
        self._add_tcx("total_run_distance", self.tcx_utils.total_run_distance())
        self._add_tcx("total_run_elevation", self.tcx_utils.total_run_elevation())
        self._add_tcx("total_run_calories", self.tcx_utils.total_run_calories())
        self._add_tcx("run_distances_daily", self.tcx_utils.run_distances(weekly=False))
        self._add_tcx("run_distances_weekly", self.tcx_utils.run_distances(weekly=True))
        self._add_tcx("run_duration_daily", self.tcx_utils.run_duration(weekly=False))
        self._add_tcx("run_duration_weekly", self.tcx_utils.run_duration(weekly=True))
        self._add_tcx(
            "heart_rate_zone_percentages_daily",
            [
                (
                    zone.value,
                    self.tcx_utils.get_heart_rate_zone_percentages(
                        zone=zone, weekly=False
                    ),
                )
                for zone in HeartRateZone
            ],
        )
        self._add_tcx(
            "heart_rate_zone_percentages_weekly",
            [
                (
                    zone.value,
                    self.tcx_utils.get_heart_rate_zone_percentages(
                        zone=zone, weekly=True
                    ),
                )
                for zone in HeartRateZone
            ],
        )
        self._add_tcx(
            "pace_zone_percentages_daily",
            [
                (
                    zone.min_mi,
                    zone.min_km,
                    self.tcx_utils.get_pace_zone_percentages(zone=zone, weekly=False),
                )
                for zone in PaceZone
            ],
        )
        self._add_tcx(
            "pace_zone_percentages_weekly",
            [
                (
                    zone.min_mi,
                    zone.min_km,
                    self.tcx_utils.get_pace_zone_percentages(zone=zone, weekly=True),
                )
                for zone in PaceZone
            ],
        )
        self._add_tcx("peak_hr", self.tcx_utils.get_peak_data("heart_rate"))
        self._add_tcx("peak_pace", self.tcx_utils.get_peak_data("pace"))
        self._add_tcx("peak_pace_monthly", self.tcx_utils.get_peak_data("pace", True))
        self._add_tcx("heart_rate_pace_data", self.tcx_utils.get_heart_rate_pace_data())

        # Hevy data
        self._add_hevy(
            "week_start_dates",
            [date_to_str(d) for d in self.hevy_utils.week_start_dates()],
        )
        self._add_hevy("dates_str", self.hevy_utils.dates_str())
        self._add_hevy(
            "workout_volume_daily", self.hevy_utils.workout_volume(weekly=False)
        )
        self._add_hevy(
            "workout_volume_weekly", self.hevy_utils.workout_volume(weekly=True)
        )
        self._add_hevy(
            "workout_duration_daily", self.hevy_utils.workout_duration(weekly=False)
        )
        self._add_hevy(
            "workout_duration_weekly", self.hevy_utils.workout_duration(weekly=True)
        )
        self._add_hevy(
            "exercise_one_rep_max_daily",
            [
                (
                    exercise.value,
                    self.hevy_utils.exercise_one_rep_max(exercise.value, weekly=False),
                )
                for exercise in ExerciseName
            ],
        )
        self._add_hevy(
            "exercise_one_rep_max_monthly",
            [
                (
                    exercise.value,
                    self.hevy_utils.exercise_one_rep_max(exercise.value, weekly=True),
                )
                for exercise in ExerciseName
            ],
        )

        # Strava Data
        self._add_strava("distance_by_gear", self.strava_utils.distance_by_gear())

        # Whoop Data
        self._add_whoop(
            "week_start_dates",
            [date_to_str(d) for d in self.whoop_utils.week_start_dates()],
        )
        self._add_whoop("dates_str", self.whoop_utils.dates_str())
        self._add_whoop(
            "avg_recovery_score_daily",
            [
                (
                    zone.name,
                    self.whoop_utils.avg_recovery_score(zone=zone, weekly=False),
                )
                for zone in RecoveryZone
            ],
        )
        self._add_whoop(
            "avg_recovery_score_weekly",
            [
                (
                    zone.name,
                    self.whoop_utils.avg_recovery_score(zone=zone, weekly=True),
                )
                for zone in RecoveryZone
            ],
        )
        self._add_whoop("day_strain_daily", self.whoop_utils.day_strain())
        self._add_whoop("day_strain_weekly", self.whoop_utils.day_strain(weekly=True))
        self._add_whoop("sleep_performance_daily", self.whoop_utils.sleep_performance())
        self._add_whoop(
            "sleep_performance_weekly", self.whoop_utils.sleep_performance(weekly=True)
        )
        self._add_whoop("asleep_duration_daily", self.whoop_utils.asleep_duration())
        self._add_whoop(
            "asleep_duration_weekly", self.whoop_utils.asleep_duration(weekly=True)
        )

    def write_json(self):
        with open(APP_DATA, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def _add_tcx(self, key, value):
        key = key if key.startswith(TCX_PREFIX) else TCX_PREFIX + key
        self.data[key] = value

    def _add_hevy(self, key, value):
        key = key if key.startswith(HEVY_PREFIX) else HEVY_PREFIX + key
        self.data[key] = value

    def _add_strava(self, key, value):
        key = key if key.startswith(STRAVA_PREFIX) else STRAVA_PREFIX + key
        self.data[key] = value

    def _add_whoop(self, key, value):
        key = key if key.startswith(WHOOP_PREFIX) else WHOOP_PREFIX + key
        self.data[key] = value


if __name__ == "__main__":
    writer = Writer()
    writer.load_data()
    writer.process_data()
    writer.write_json()
