from dataclasses import dataclass
from datetime import datetime


@dataclass
class HevySet:
    weight_lbs: float
    reps: int

    @property
    def one_rep_max(self):
        return self.weight_lbs * (1 + self.reps / 30)


@dataclass
class HevyExercise:
    title: str
    sets: list[HevySet]

    def __init__(self, title: str):
        self.title = title
        self.sets = []

    def add_set(self, weight_lbs: float, reps: int):
        self.sets.append(HevySet(weight_lbs, reps))


@dataclass
class HevyWorkout:
    title: str
    start_time: datetime
    end_time: datetime
    description: str
    exercises: dict[str, HevyExercise]

    @property
    def duration(self):
        return (self.end_time - self.start_time).total_seconds()

    @property
    def volume(self):
        return sum(sum(s.weight_lbs for s in e.sets) for e in self.exercises.values())

    class Builder:
        title: str | None = None
        start_time: datetime | None = None
        end_time: datetime | None = None
        description: str | None = None
        exercises: dict[str, HevyExercise] = {}

        def __init__(self):
            self.title = None
            self.start_time = None
            self.end_time = None
            self.description = None
            self.exercises = {}

        def with_title(self, title: str):
            self.title = title
            return self

        def with_start_time(self, start_time: datetime):
            self.start_time = start_time
            return self

        def with_end_time(self, end_time: datetime):
            self.end_time = end_time
            return self

        def with_description(self, description: str):
            self.description = description
            return self

        def with_exercise(self, exercise: HevyExercise):
            self.exercises[exercise.title] = exercise
            return self

        def with_exercise_set(self, exercise_title: str, weight_lbs: float, reps: int):
            if exercise_title not in self.exercises:
                self.exercises[exercise_title] = HevyExercise(exercise_title)
            self.exercises[exercise_title].add_set(weight_lbs, reps)
            return self

        def build(self):
            if self.title is None:
                raise ValueError("Title is required")
            if self.start_time is None:
                raise ValueError("Start time is required")
            if self.end_time is None:
                raise ValueError("End time is required")

            workout = HevyWorkout(
                self.title,
                self.start_time,
                self.end_time,
                self.description,
                self.exercises,
            )
            return workout
