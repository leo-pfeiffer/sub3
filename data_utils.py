import csv
import datetime
import json
import os
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Callable, Any

from tcxreader import TCXExercise, TCXTrackPoint, TCXReader

from constants import DURATIONS, DISTANCE_NAMES, PLAN_START_DATE
from models.strava import MinimalRun
from utils import get_list_of_dates_between, get_first_day_of_week, date_to_str
from enums import HeartRateZone, PaceZone
from models.hevy import HevyWorkout


class DataUtils(ABC):

    @abstractmethod
    def workout_start_times(self):
        ...

    @abstractmethod
    def load_from_source(self):
        ...

    def dates(self):
        start = min(self.workout_start_times())
        end = max(self.workout_start_times())
        return get_list_of_dates_between(start, end, 1)

    def dates_str(self):
        return [date_to_str(d) for d in self.dates()]

    def week_start_dates(self):
        start = min(self.workout_start_times())
        end = max(self.workout_start_times())
        return get_list_of_dates_between(start, end, 7)

    def _group_by_date(
            self,
            workouts: list[HevyWorkout | TCXExercise],
            value_func: Callable[[HevyWorkout | TCXExercise], Any],
            weekly=False,
            default_value: Any = 0.0,
            default_agg_func: Callable = lambda x, y: x + y
    ):
        grouped: dict[date, Any] = {}
        for workout in workouts:
            k = get_first_day_of_week(workout.start_time) if weekly else workout.start_time.date()
            if k not in grouped:
                grouped[k] = default_value
            grouped[k] = default_agg_func(grouped[k], value_func(workout))
        groups = self.week_start_dates() if weekly else self.dates()
        return [grouped.get(g, default_value) for g in groups]


class HevyUtils(DataUtils):
    DATA_DIR = "data"
    CSV_NAME = "hevy_workouts.csv"

    def __init__(self):
        self._workouts: list[HevyWorkout] | None = None

    def load_data(self):
        self._workouts = [
            w for w in self.load_from_source()
            if w.start_time >= PLAN_START_DATE
        ]

    def load_from_source(self):
        csv_lines = self._read_hevy_csv(f"{self.DATA_DIR}/{self.CSV_NAME}")
        grouped_workouts = {}
        for line in csv_lines:
            exercise_title = line[0]
            exercise_start_time = line[1]
            exercise_end_time = line[2]
            key = f"{exercise_title}_{exercise_start_time}_{exercise_end_time}"
            workout_lines = []
            if key in grouped_workouts:
                workout_lines = grouped_workouts[key]
            workout_lines.append(line)
            grouped_workouts[key] = workout_lines

        workouts = []
        for key, lines in grouped_workouts.items():
            workout = self._build_workout_from_grouped_csv_lines(lines)
            workouts.append(workout)

        return workouts

    @staticmethod
    def _build_workout_from_grouped_csv_lines(csv_lines: list[str]):
        workout_builder = HevyWorkout.Builder()

        for csv_line in csv_lines:
            [
                _title,
                _start_time_str,
                _end_time_str,
                _description,
                _exercise_title,
                _superset_id,
                _exercise_notes,
                _set_index,
                _set_type,
                _weight_lbs,
                _reps,
                _distance_miles,
                _duration_seconds,
                _rpe
            ] = csv_line

            _start_time = datetime.strptime(_start_time_str, '%d %b %Y, %H:%M')
            _end_time = datetime.strptime(_end_time_str, '%d %b %Y, %H:%M')

            if workout_builder.title is None:
                workout_builder.with_title(_title)
                workout_builder.with_start_time(_start_time)
                workout_builder.with_end_time(_end_time)
            else:
                if _title != workout_builder.title:
                    raise ValueError("Title mismatch")
                if _start_time != workout_builder.start_time:
                    raise ValueError("Start time mismatch")
                if _end_time != workout_builder.end_time:
                    raise ValueError("End time mismatch")

            workout_builder.with_exercise_set(
                _exercise_title,
                0.0 if len(_weight_lbs) == 0 else float(_weight_lbs),
                0 if len(_reps) == 0 else int(_reps),
            )

        return workout_builder.build()

    @staticmethod
    def _read_hevy_csv(filepath: str):
        csv_lines = []
        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                csv_lines.append(row)
        return csv_lines

    @property
    def workouts(self):
        return self._workouts

    def workout_start_times(self):
        return [w.start_time for w in self.workouts]

    def workout_duration(self, weekly=False):
        return self._group_by_date(
            self.workouts,
            lambda w: w.duration,
            weekly
        )

    def workout_volume(self, weekly=False):
        return self._group_by_date(
            self.workouts,
            lambda w: w.volume,
            weekly
        )

    @staticmethod
    def _get_one_rep_max_for_exercise(workout: HevyWorkout, exercise_name: str):
        exercise = workout.exercises.get(exercise_name)
        if exercise is None:
            return 0
        return max([s.one_rep_max for s in exercise.sets])

    def exercise_one_rep_max(self, exercise_name: str, weekly=False):
        return self._group_by_date(
            self.workouts,
            lambda w: self._get_one_rep_max_for_exercise(w, exercise_name),
            weekly,
            default_agg_func=lambda x, y: max(x, y)
        )


class TcxUtils(DataUtils):
    DATA_DIR = "data"

    def __init__(self):
        self._workouts: list[TCXExercise] | None = None

    def load_data(self):
        self._workouts = [
            w for w in self.load_from_source()
            if w.activity_type == "Running" and w.start_time >= PLAN_START_DATE
        ]

    def load_from_source(self):
        file_names = [f for f in os.listdir(self.DATA_DIR) if f.endswith('.tcx')]
        tcx_data = []
        tcx_reader = TCXReader()
        for file_name in file_names:
            print(f"Reading file: {file_name}")
            file_location = os.path.join(self.DATA_DIR, file_name)
            _data = tcx_reader.read(file_location)
            tcx_data.append(_data)
        return tcx_data

    @property
    def workouts(self):
        return self._workouts

    def total_run_distance(self):
        return sum([w.distance for w in self.workouts])

    def total_run_elevation(self):
        return sum([w.ascent for w in self.workouts])

    def total_run_calories(self):
        return sum([w.calories for w in self.workouts])

    def workout_start_times(self):
        return [w.start_time for w in self.workouts]

    def run_distances(self, weekly=False):
        return self._group_by_date(
            self.workouts,
            lambda w: w.distance,
            weekly
        )

    def run_duration(self, weekly=False):
        return self._group_by_date(
            self.workouts,
            lambda w: w.duration,
            weekly
        )

    def get_heart_rate_zone_percentages(self, zone: HeartRateZone, weekly=False):
        return self._get_zone_percentages(zone, self.heart_rate_zones(weekly))

    def get_pace_zone_percentages(self, zone: PaceZone, weekly=False):
        return self._get_zone_percentages(zone, self.pace_zones(weekly))

    @staticmethod
    def _heart_rate_zones(workout: TCXExercise):
        trackpoints = TcxUtils.get_sorted_trackpoint_deltas(workout, lambda t: t.hr_value, "time")

        # Calculate duration spent in each HeartRateZone
        zone_durations = {}
        for i in range(len(trackpoints) - 1):
            start = trackpoints[i]
            end = trackpoints[i + 1]
            duration = (end[0] - start[0]).total_seconds()
            if duration > 15:  # Durations over 15s are likely paused workouts and are skipped
                continue
            zone = HeartRateZone.zone(start[1])
            if zone not in zone_durations:
                zone_durations[zone] = 0
            zone_durations[zone] += duration

        return zone_durations

    @staticmethod
    def _pace_zones(workout: TCXExercise):
        trackpoints = TcxUtils.get_sorted_trackpoint_deltas(workout, lambda t: t.tpx_ext.get("Speed"), "time")

        # Calculate duration spent in each HeartRateZone
        zone_durations = {}
        for i in range(len(trackpoints) - 1):
            start = trackpoints[i]
            end = trackpoints[i + 1]
            duration = (end[0] - start[0]).total_seconds()
            if duration > 15:  # Durations over 45s are likely paused workouts and are skipped
                continue
            zone = PaceZone.zone(start[1])
            if zone not in zone_durations:
                zone_durations[zone] = 0
            zone_durations[zone] += duration

        return zone_durations

    @staticmethod
    def _hr_zone_agg_func(zones1, zones2):
        return {zone: zones1.get(zone, 0) + zones2.get(zone, 0) for zone in HeartRateZone}

    @staticmethod
    def _pace_zone_agg_func(zones1, zones2):
        return {zone: zones1.get(zone, 0) + zones2.get(zone, 0) for zone in PaceZone}

    def heart_rate_zones(self, weekly=False):
        return self._group_by_date(
            self.workouts,
            self._heart_rate_zones,
            weekly=weekly,
            default_value={zone: 0 for zone in HeartRateZone},
            default_agg_func=self._hr_zone_agg_func
        )

    def pace_zones(self, weekly=False):
        return self._group_by_date(
            self.workouts,
            self._pace_zones,
            weekly=weekly,
            default_value={zone: 0 for zone in PaceZone},
            default_agg_func=self._pace_zone_agg_func
        )

    @staticmethod
    def _get_zone_percentages(zone: HeartRateZone | PaceZone, zone_data: list):
        percentages = []
        for z in zone_data:
            total = sum(z.values())
            if total == 0:
                percentages.append(0)
            else:
                if zone not in z:
                    z[zone] = 0
                percentages.append(round(z[zone] / total * 100, 2))
        return percentages

    @staticmethod
    def get_sorted_trackpoint_deltas(
            workout: TCXExercise,
            key_func: Callable[[TCXTrackPoint], int | float],
            mode: str
    ) -> list[tuple[Any, int | float, int | float]]:

        if mode == "time":
            index_func = lambda x: x.time
            delta_func = lambda x, y: (y.time - x.time).total_seconds()
        elif mode == "distance":
            index_func = lambda x: x.distance
            delta_func = lambda x, y: y.distance - x.distance
        else:
            raise ValueError(f"Invalid mode: {mode}")

        raw_trackpoints = [t for t in workout.trackpoints if key_func(t) is not None]
        raw_trackpoints.sort(key=lambda x: x.time)

        trackpoints = []

        if len(raw_trackpoints) == 0:
            return trackpoints

        # Calculate duration of each trackpoint
        for i in range(len(raw_trackpoints) - 1):
            start = raw_trackpoints[i]
            end = raw_trackpoints[i + 1]
            delta = delta_func(start, end)
            trackpoints.append((index_func(start), key_func(start), delta))

        return trackpoints

    @staticmethod
    def calc_moving_average(
            dataset: list[tuple[datetime, float | int, int]],
            mode: str,
            delta: int = 60,
    ) -> list[float]:
        if mode == "time":
            delta_func = lambda x, y: (y[0] - x[0]).total_seconds()
        elif mode == "distance":
            delta_func = lambda x, y: y[0] - x[0]
        else:
            raise ValueError(f"Invalid mode: {mode}")

        left_idx = 0
        right_idx = 0
        moving_average = []
        moving_sum = 0
        normalizer = 0
        while right_idx < len(dataset):
            delta_between_trackpoints = delta_func(dataset[left_idx], dataset[right_idx])
            if delta_between_trackpoints < delta:
                moving_sum += (dataset[right_idx][1] * dataset[right_idx][2])
                normalizer += dataset[right_idx][2]
                right_idx += 1
            else:
                moving_average.append(moving_sum / normalizer)
                moving_sum -= (dataset[left_idx][1] * dataset[left_idx][2])
                normalizer -= dataset[left_idx][2]
                left_idx += 1
        return moving_average

    def _moving_average_heart_rate(self, workout: TCXExercise, duration_seconds: int = 60):
        trackpoints = self.get_sorted_trackpoint_deltas(workout, lambda t: t.hr_value, "time")
        return TcxUtils.calc_moving_average(
            trackpoints, "time", duration_seconds
        )

    def _moving_average_pace(self, workout: TCXExercise, duration_seconds: int = 60):
        trackpoints = self.get_sorted_trackpoint_deltas(workout, lambda t: t.tpx_ext.get("Speed"), "distance")
        return TcxUtils.calc_moving_average(
            trackpoints,
            "distance",
            duration_seconds
        )

    def get_peak_data(self, dataset_name: str, by_month=False):
        # Todo this got really messy after adding the by_month option. Refactor this.
        if dataset_name == "heart_rate":
            categories = DURATIONS
            ma_func = self._moving_average_heart_rate
        elif dataset_name == "pace":
            categories = [d for d in DISTANCE_NAMES.keys()]
            ma_func = self._moving_average_pace
        else:
            raise ValueError(f"Invalid dataset_name: {dataset_name}")

        monthly_data = {
            workout.start_time.month: {cat: [] for cat in categories}
            for workout in self.workouts
        }

        data = {cat: [] for cat in categories}
        for workout in self.workouts:
            workout_month = workout.start_time.month
            for cat in categories:
                moving_averages = ma_func(workout, cat)
                if len(moving_averages) > 0:
                    data[cat].append(max(moving_averages))
                    if by_month:
                        monthly_data[workout_month][cat].append(max(moving_averages))

        if by_month:
            month_data_out = {}
            for month, month_data in monthly_data.items():
                month_data_out[month] = {k: max(v) for k, v in month_data.items() if len(v) > 0}
            return month_data_out

        return {k: max(v) for k, v in data.items() if len(v) > 0}

    def get_heart_rate_pace_data(self):
        trackpoints = []
        for workout in self.workouts:
            raw_trackpoints = [t for t in workout.trackpoints if
                               t.hr_value is not None and t.tpx_ext.get("Speed") is not None]
            raw_trackpoints.sort(key=lambda x: x.time)
            group_size = 20
            for i in range(0, len(raw_trackpoints), group_size):
                group = raw_trackpoints[i:i + group_size]
                first_time = group[0].time
                hr = sum([t.hr_value for t in group]) / group_size
                speed = sum([t.tpx_ext.get("Speed") for t in group]) / group_size
                trackpoints.append((first_time.month, hr, speed))
        return trackpoints


class StravaUtils(DataUtils):

    DATA_DIR = "data"
    JSON_NAME = "strava_activities_by_gear.json"

    def __init__(self):
        self.data = None

    def load_data(self):
        self.data = self.load_from_source()

    def load_from_source(self):
        filepath = f"{self.DATA_DIR}/{self.JSON_NAME}"
        with open(filepath, 'r') as file:
            raw_json = json.load(file)
        data = {}
        for gear, activities in raw_json.items():
            gear_name = self._modify_gear_name(gear)
            data[gear_name] = [
                MinimalRun(
                    start_time=datetime.strptime(a['start_date_local'], '%Y-%m-%dT%H:%M:%SZ'),
                    distance=a['distance']
                ) for a in activities if a['sport_type'] == 'Run'
            ]
        return data

    @staticmethod
    def _modify_gear_name(gear_name: str):
        saucony_end_speed_3 = "Saucony Endorphin Speed 3"
        if gear_name.startswith(saucony_end_speed_3):
            return saucony_end_speed_3
        return gear_name

    def workout_start_times(self):
        raise NotImplementedError

    def distance_by_gear(self):
        return {gear: sum([a.distance for a in activities]) for gear, activities in self.data.items()}
