from loading_utils import load_tcx_workouts, load_hevy_workouts

DATA_DIR = 'data'
HEVY_FILE = 'hevy_workouts.csv'

data = load_tcx_workouts(DATA_DIR)
hevy_workouts = load_hevy_workouts(f"{DATA_DIR}/{HEVY_FILE}")
x = 1
