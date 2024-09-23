import csv
import os
from datetime import datetime

from tcxreader import TCXExercise, TCXReader

from models.hevy import HevyWorkout


def load_tcx_workouts(data_dir) -> list[TCXExercise]:
    file_names = [f for f in os.listdir(data_dir) if f.endswith('.tcx')]
    tcx_data = []
    tcx_reader = TCXReader()
    for file_name in file_names:
        file_location = os.path.join(data_dir, file_name)
        _data = tcx_reader.read(file_location)
        tcx_data.append(_data)
    return tcx_data


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


def _read_hevy_csv(filepath: str):
    csv_lines = []
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            csv_lines.append(row)
    return csv_lines


def load_hevy_workouts(filepath: str) -> list[HevyWorkout]:
    csv_lines = _read_hevy_csv(filepath)
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
        workout = _build_workout_from_grouped_csv_lines(lines)
        workouts.append(workout)

    return workouts
