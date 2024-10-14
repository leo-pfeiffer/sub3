import math
from datetime import datetime

import altair as alt
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from streamlit.components.v1 import html, iframe
from streamlit_echarts import st_echarts, JsCode

from constants import DISTANCE_NAMES
from data_access import Reader
from utils import m_to_km_or_mi, ms_to_min_km_or_min_mi, lbs_to_kg
from enums import HeartRateZone, PaceZone, ExerciseName, RecoveryZone
from resources.resources import (
    TIMER_HTML,
    PACE_FORMATTER,
    SHOE_FORMATTER,
)


@st.cache_resource
def get_reader():
    return Reader()


def get_color(value, min_value=0, max_value=100, cmap_name="Reds"):
    cmap = plt.get_cmap(cmap_name)
    norm = plt.Normalize(min_value, max_value)
    rgba = cmap(norm(value))
    return rgb2hex(rgba)

iframe(
    "https://home.trainingpeaks.com/athlete/workout/4QC7Z7VYCECLHJR7TFGDUVLOAU",
    height=800,
    scrolling=True
)

with st.sidebar:
    st.image("resources/mcmo_solid_black.png")
    st.html("<hr>")
    weekly = st.toggle("Group by week", value=True)
    imperial = st.toggle("Imperial units", value=True)
    st.html("<hr>")
    st.write('<a href="#road-to-2-59-59">Road to 2:59:59</a>', unsafe_allow_html=True)
    st.write('<a href="#zones">Zones</a>', unsafe_allow_html=True)
    st.write(
        '<a href="#peak-heart-rate-and-pace">Peak Heart Rate and Pace</a>',
        unsafe_allow_html=True,
    )
    st.write('<a href="#shoes">Shoes</a>', unsafe_allow_html=True)
    st.write('<a href="#weightlifting">Weightlifting</a>', unsafe_allow_html=True)
    st.write(
        '<a href="#whoop-recovery-sleep-and-strain">Whoop Recovery</a>',
        unsafe_allow_html=True,
    )
    st.html("<hr>")
    st.html(
        """
        <a href="https://www.strava.com/athletes/103532570" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Strava_Logo.svg/2880px-Strava_Logo.svg.png" 
        width="50%" style="display: block; margin: 0 auto;">
        </a>
        """
    )

html(TIMER_HTML)

reader = get_reader()

st.write(
    """
    # Road to 2:59:59

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam nec purus
    eget nunc vestibulum tincidunt. Nullam nec purus eget nunc vestibulum
    tincidunt. Nullam nec purus eget nunc vestibulum tincidunt.
    """
)

iframe(
    "https://home.trainingpeaks.com/athlete/workout/4QC7Z7VYCECLHJR7TFGDUVLOAU", 
    height=800, 
    scrolling=True
)

col1, col2, col3 = st.columns(3)
col1.metric(
    "Distance",
    f"{round(m_to_km_or_mi(reader.get_tcx('total_run_distance'), imperial), 2)} {'km' if not imperial else 'mi'}",
)
col2.metric(
    "Elevation",
    f"{round(reader.get_tcx('total_run_elevation') * (3.28084 if imperial else 1), 2)} {'m' if not imperial else 'ft'}",
)
col3.metric(
    "Calories",
    f"{int(reader.get_tcx('total_run_calories'))} cal",
)

st.write(
    """
    ## Running distance
    """
)

run_duration_distance_chart = {
    "legend": {"data": [f"Distance ({'mi' if imperial else 'km'})", "Duration (min)"]},
    "xAxis": {
        "type": "category",
        "axisTick": {"alignWithLabel": True},
        # "data":
        "data": [
            f"Wk {i + 1}" for i, _ in enumerate(reader.get_tcx("week_start_dates"))
        ]
        if weekly
        else reader.get_tcx("dates_str"),
    },
    "yAxis": [
        {
            "type": "value",
            "name": f"Distance ({'mi' if imperial else 'km'})",
            "position": "left",
            "alignTicks": True,
            "axisLabel": {"formatter": "{value}" + f"{'mi' if imperial else 'km'}"},
        },
        {
            "type": "value",
            "name": "Duration (min)",
            "position": "right",
            "alignTicks": True,
            "axisLabel": {"formatter": "{value} min"},
        },
    ],
    "series": [
        {
            "name": f"Distance ({'mi' if imperial else 'km'})",
            "data": [
                round(m_to_km_or_mi(d, imperial), 2)
                for d in reader.get_tcx(
                    "run_distances_weekly" if weekly else "run_distances_daily"
                )
            ],
            "type": "line",
            "yAxisIndex": 0,
        },
        {
            "name": "Duration (min)",
            "data": [
                round(d / 60, 2)
                for d in reader.get_tcx(
                    "run_duration_weekly" if weekly else "run_duration_daily"
                )
            ],
            "type": "line",
            "yAxisIndex": 1,
        },
    ],
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross"},
    },
}
st_echarts(options=run_duration_distance_chart)

st.write(
    """
    ## Zones
    """
)

st.write(
    """
    ### Heart rate zones
    """
)

heart_rate_zone_stacked_bar_chart = {
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "legend": {
        "data": [zone.value for zone in HeartRateZone],
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "data": [
            f"Wk {i + 1}" for i, _ in enumerate(reader.get_tcx("week_start_dates"))
        ]
        if weekly
        else reader.get_tcx("dates_str"),
    },
    "yAxis": {"type": "value", "min": 0, "max": 100},
    "series": [
        {
            "name": zone,
            "type": "bar",
            "stack": "total",
            "itemStyle": {"color": get_color(i + 1, 0, len(HeartRateZone), "Reds")},
            "data": data,
        }
        for i, (zone, data) in enumerate(
            reader.get_tcx(
                "heart_rate_zone_percentages_weekly"
                if weekly
                else "heart_rate_zone_percentages_daily"
            )
        )
    ],
}

st_echarts(options=heart_rate_zone_stacked_bar_chart)

st.write(
    """
    ### Pace zones
    """
)

pace_zone_stacked_bar_chart = {
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "legend": {
        "data": [zone.min_mi if imperial else zone.min_km for zone in PaceZone],
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "data": [
            f"Wk {i + 1}" for i, _ in enumerate(reader.get_tcx("week_start_dates"))
        ]
        if weekly
        else reader.get_tcx("dates_str"),
    },
    "yAxis": {"type": "value", "min": 0, "max": 100},
    "series": [
        {
            "name": min_mi if imperial else min_km,
            "type": "bar",
            "stack": "total",
            "itemStyle": {"color": get_color(i + 1, 0, len(PaceZone), "Blues")},
            "data": data,
        }
        for i, (min_mi, min_km, data) in enumerate(
            reader.get_tcx(
                "pace_zone_percentages_weekly"
                if weekly
                else "pace_zone_percentages_daily"
            )
        )
    ],
}

st_echarts(options=pace_zone_stacked_bar_chart)


def make_peak_chart(dataset_name: str, pretty_name: str):
    data = reader.get_tcx(dataset_name)
    if dataset_name == "peak_pace":
        y_values = [ms_to_min_km_or_min_mi(d, imperial) for d in data.values()]
        categories = [
            name for val, name in DISTANCE_NAMES.items() if val in data.keys()
        ]
        inverse = True
        base_color = "Blues"
        min_value = min(y_values)
        max_value = max(y_values)
        formatter = JsCode(PACE_FORMATTER).js_code
    elif dataset_name == "peak_hr":
        y_values = [d for d in data.values()]
        categories = list(data.keys())
        inverse = False
        base_color = "Reds"
        min_value = min(y_values) - 10
        max_value = max(y_values) + 5
        formatter = "{b}: {c} BPM"
    else:
        raise ValueError(f"Unknown dataset_name: {dataset_name}")

    return {
        "xAxis": {
            "type": "category",
            "data": categories,
        },
        "yAxis": {
            "type": "value",
            "name": pretty_name,
            "inverse": inverse,
            "min": math.floor(min_value),
            "max": math.ceil(max_value),
        },
        "series": [
            {
                "data": [round(d, 2) for d in y_values],
                "type": "line",
                "itemStyle": {"color": get_color(4, 0, 5, base_color)},
            }
        ],
        "tooltip": {"trigger": "axis", "formatter": formatter},
    }


st.write(
    """
    ## Peak Heart Rate and Pace
    """
)

peak_heart_rate_col1, peak_heart_rate_col2 = st.columns(2, vertical_alignment="center")

with peak_heart_rate_col1:
    st.write(
        """
        This chart shows the highest average heart rate sustained over a given duration.
        """
    )

with peak_heart_rate_col2:
    st_echarts(options=make_peak_chart("peak_hr", "BPM"))

peak_pace_col1, peak_pace_col2 = st.columns(2, vertical_alignment="center")

with peak_pace_col1:
    st.write(
        """
        This chart shows the fastest average pace sustained over a given distance.
        """
    )

with peak_pace_col2:
    st_echarts(
        options=make_peak_chart(
            "peak_pace", "Pace (min/km)" if not imperial else "Pace (min/mi)"
        )
    )


def make_peak_pace_chart_by_month():
    data = reader.get_tcx("peak_pace_monthly")

    raw_categories = list(
        set([int(item) for sublist in data.values() for item in sublist])
    )
    categories = [name for val, name in DISTANCE_NAMES.items() if val in raw_categories]
    flat_values = [item for sublist in data.values() for item in sublist.values()]
    months = [datetime(2024, int(month), 1).strftime("%B") for month in data.keys()]

    slowest_pace = ms_to_min_km_or_min_mi(min(flat_values), imperial)
    fastest_pace = ms_to_min_km_or_min_mi(max(flat_values), imperial)

    return {
        "xAxis": {
            "type": "category",
            "data": categories,
        },
        "legend": {
            "data": [categories],
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "yAxis": {
            "type": "value",
            "name": "Pace (min/km)" if not imperial else "Pace (min/mi)",
            "inverse": True,
            "min": math.floor(fastest_pace),
            "max": math.ceil(slowest_pace),
        },
        "series": [
            {
                "name": months[i],
                "data": [
                    round(ms_to_min_km_or_min_mi(d, imperial), 2) for d in y_values
                ],
                "type": "line",
                "itemStyle": {"color": get_color(i + 1, 0, len(data.keys()), "Blues")},
            }
            for i, y_values in enumerate([d.values() for d in data.values()])
        ],
        "tooltip": {
            "trigger": "axis",
        },
    }


grouped_peak_pace_col1, grouped_peak_pace_col2 = st.columns(
    2, vertical_alignment="center"
)

with grouped_peak_pace_col1:
    st.write(
        """
        Same but grouped by month.
        """
    )

with grouped_peak_pace_col2:
    st_echarts(options=make_peak_pace_chart_by_month())

st.write(
    """
    ### Heart Rate vs Pace
    """
)

selector = alt.selection_point(fields=["Month"], bind="legend")
c = (
    alt.Chart(
        alt.Data(
            values=[
                {"Month": t, "HR": hr, "Pace": p}
                for t, hr, p in reader.get_tcx("heart_rate_pace_data")
            ]
        )
    )
    .mark_circle(size=50)
    .encode(
        x="Pace:Q",
        y="HR:Q",
        color="Month:N",
        opacity=alt.condition(selector, alt.value(1), alt.value(0.1)),
    )
    .add_params(selector)
)

st.altair_chart(c, use_container_width=True)

st.write(
    """
    ## Shoes
    """
)


def make_shoe_chart():
    data = reader.get_strava("distance_by_gear")
    categories = [x.replace(" ", "\n") for x in data.keys()]
    y_values = [round(m_to_km_or_mi(d, imperial), 2) for d in data.values()]
    return {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "formatter": JsCode(SHOE_FORMATTER).js_code,
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": categories,
        },
        "yAxis": {
            "type": "value",
            "min": 0,
            "max": math.ceil(max(y_values)),
        },
        "series": [
            {
                "type": "bar",
                "data": y_values,
            }
        ],
    }


st_echarts(options=make_shoe_chart())

st.write("## Weightlifting")

st.write("### Volume and Duration")

strength_duration_volume_chart = {
    "legend": {"data": [f"Volume ({'lbs' if imperial else 'kg'})", "Duration (min)"]},
    "xAxis": {
        "type": "category",
        "axisTick": {"alignWithLabel": True},
        "data": [
            f"Wk {i + 1}" for i, _ in enumerate(reader.get_hevy("week_start_dates"))
        ]
        if weekly
        else reader.get_hevy("dates_str"),
    },
    "yAxis": [
        {
            "type": "value",
            "name": f"Volume ({'lbs' if imperial else 'kg'})",
            "position": "left",
            "alignTicks": True,
            "axisLabel": {"formatter": "{value}" + f"{'lbs' if imperial else 'kg'}"},
        },
        {
            "type": "value",
            "name": "Duration (min)",
            "position": "right",
            "alignTicks": True,
            "axisLabel": {"formatter": "{value} min"},
        },
    ],
    "series": [
        {
            "name": f"Volume ({'lbs' if imperial else 'kg'})",
            "data": [
                round(d if imperial else lbs_to_kg(d), 2)
                for d in reader.get_hevy(
                    "workout_volume_weekly" if weekly else "workout_volume_daily"
                )
            ],
            "type": "line",
            "yAxisIndex": 0,
        },
        {
            "name": "Duration (min)",
            "data": [
                round(d / 60, 2)
                for d in reader.get_hevy(
                    "workout_duration_weekly" if weekly else "workout_duration_daily"
                )
            ],
            "type": "line",
            "yAxisIndex": 1,
        },
    ],
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross"},
    },
}
st_echarts(options=strength_duration_volume_chart)

st.write("### One Rep Max")

one_rep_max_chart = {
    "legend": {"data": [v.value for v in ExerciseName]},
    "xAxis": {
        "type": "category",
        "axisTick": {"alignWithLabel": True},
        "data": [
            f"Wk {i + 1}" for i, _ in enumerate(reader.get_hevy("week_start_dates"))
        ]
        if weekly
        else reader.get_hevy("dates_str"),
    },
    "yAxis": {
        "type": "value",
        "name": f"One Rep Max ({'lbs' if imperial else 'kg'})",
        "position": "left",
        "alignTicks": True,
        "axisLabel": {"formatter": "{value}" + f"{'lbs' if imperial else 'kg'}"},
    },
    "series": [
        {
            "name": exercise,
            "data": [round(d if imperial else lbs_to_kg(d), 2) for d in data],
            "type": "line",
        }
        for exercise, data in reader.get_hevy(
            "exercise_one_rep_max_monthly" if weekly else "exercise_one_rep_max_daily"
        )
    ],
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross"},
    },
}
st_echarts(options=one_rep_max_chart)

st.write("## Whoop Recovery, Sleep, and Strain")

st.write(
    """
    ### Recovery
    """
)

recovery_stacked_bar_chart = {
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "legend": {
        "data": [zone.value for zone in RecoveryZone],
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "data": [
            f"Wk {i + 1}" for i, _ in enumerate(reader.get_whoop("week_start_dates"))
        ]
        if weekly
        else reader.get_whoop("dates_str"),
    },
    "yAxis": {"type": "value", "min": 0, "max": 100, "name": "%"},
    "series": [
        {
            "name": zone,
            "type": "bar",
            "stack": "total",
            "itemStyle": {
                "color": {
                    RecoveryZone.RED.name: "#FF0026",
                    RecoveryZone.YELLOW.name: "#FFDE00",
                    RecoveryZone.GREEN.name: "#16EC06",
                }[zone]
            },
            "data": [round(d, 2) for d in data],
        }
        for i, (zone, data) in enumerate(
            reader.get_whoop(
                "avg_recovery_score_weekly" if weekly else "avg_recovery_score_daily"
            )
        )
    ],
}
st_echarts(options=recovery_stacked_bar_chart)

st.write(
    """
    ### Sleep and Strain
    """
)
whoop_combined_charts2 = {
    "legend": {
        "data": [
            "Sleep Performance",
            "Day Strain",
        ]
    },
    "xAxis": {
        "type": "category",
        "axisTick": {"alignWithLabel": True},
        "data": [
            f"Wk {i + 1}" for i, _ in enumerate(reader.get_whoop("week_start_dates"))
        ]
        if weekly
        else reader.get_whoop("dates_str"),
        "axisLine": {
            "onZero": False,
            "show": True,
        },
    },
    "yAxis": [
        {
            "type": "value",
            "name": "Sleep\nPerformance",
            "position": "left",
            "alignTicks": True,
            "axisLabel": {"formatter": "{value} %"},
        },
        {
            "type": "value",
            "name": "Day\nStrain",
            "position": "right",
            "alignTicks": True,
            "axisLabel": {"formatter": "{value} min"},
        },
    ],
    "series": [
        {
            "name": "Sleep Performance",
            "data": [
                round(d, 2)
                for d in reader.get_whoop(
                    "sleep_performance_weekly" if weekly else "sleep_performance_daily"
                )
            ],
            "type": "line",
            "yAxisIndex": 0,
            "itemStyle": {"color": "#7BA1BB"},
        },
        {
            "name": "Day Strain",
            "data": [
                round(d, 2)
                for d in reader.get_whoop(
                    "day_strain_weekly" if weekly else "day_strain_daily"
                )
            ],
            "type": "line",
            "yAxisIndex": 1,
            "itemStyle": {"color": "#67AEE6"},
        },
    ],
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross"},
    },
    "grid": {"containLabel": True},
}
st_echarts(options=whoop_combined_charts2)
