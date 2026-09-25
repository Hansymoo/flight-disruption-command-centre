from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_generator import generate_all_data
from src.database import (
    initialise_database,
    load_table,
    save_dataframe,
)
from src.risk_engine import assess_connections
from src.priority_engine import (
    calculate_priority_score,
    classify_priority,
)


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Flight Disruption & Connection Rescue Command Centre",
    page_icon="✈️",
    layout="wide",
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ---------------------------------------------------------
# Data loading
# ---------------------------------------------------------

@st.cache_data
def load_csv_data():
    """Load the synthetic source datasets."""

    flights = pd.read_csv(
        DATA_DIR / "flights.csv",
        parse_dates=[
            "scheduled_departure",
            "scheduled_arrival",
            "actual_arrival",
        ],
    )

    connections = pd.read_csv(
        DATA_DIR / "connections.csv"
    )

    transfer_times = pd.read_csv(
        DATA_DIR / "airport_transfer_times.csv"
    )

    return flights, connections, transfer_times


def sync_data_to_database(
    flights: pd.DataFrame,
    connections: pd.DataFrame,
    transfer_times: pd.DataFrame,
) -> None:
    """Store source datasets in SQLite."""

    initialise_database()

    save_dataframe(
        flights,
        "flights",
    )

    save_dataframe(
        connections,
        "connections",
    )

    save_dataframe(
        transfer_times,
        "airport_transfer_times",
    )


def build_connection_assessment(
    flights: pd.DataFrame,
    connections: pd.DataFrame,
    transfer_times: pd.DataFrame,
) -> pd.DataFrame:
    """Build risk and priority information."""

    risk_results = assess_connections(
        flights=flights,
        connections=connections,
        transfer_times=transfer_times,
    )

    inbound_delays = flights[
        [
            "flight_id",
            "delay_minutes",
            "status",
        ]
    ].rename(
        columns={
            "flight_id": "inbound_flight_id",
            "delay_minutes": "inbound_delay_minutes",
            "status": "inbound_status",
        }
    )

    results = risk_results.merge(
        inbound_delays,
        on="inbound_flight_id",
        how="left",
    )

    results["priority_score"] = results.apply(
        lambda row: calculate_priority_score(
            status=row["status"],
            delay_minutes=int(
                row["inbound_delay_minutes"]
            ),
            available_minutes=int(
                row["available_minutes"]
            ),
            required_minutes=int(
                row["required_minutes"]
            ),
        ),
        axis=1,
    )

    results["priority"] = results[
        "priority_score"
    ].apply(classify_priority)

    results["buffer_minutes"] = (
        results["available_minutes"]
        - results["required_minutes"]
    )

    return results


def save_assessments_to_database(
    assessment: pd.DataFrame,
) -> None:
    """Persist calculated connection assessments."""

    assessment_columns = [
        "connection_id",
        "passenger_id",
        "inbound_flight_id",
        "onward_flight_id",
        "available_minutes",
        "required_minutes",
        "status",
        "priority_score",
        "priority",
        "buffer_minutes",
    ]

    save_dataframe(
        assessment[assessment_columns],
        "connection_assessments",
    )


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title(
    "✈️ Flight Disruption & Connection Rescue Command Centre"
)

st.caption(
    "Fictional airline operations-control prototype "
    "using synthetic data."
)

st.info(
    "Educational portfolio project only. "
    "No real airline, passenger or operational data is used."
)


# ---------------------------------------------------------
# Ensure source data exists
# ---------------------------------------------------------

required_files = [
    DATA_DIR / "flights.csv",
    DATA_DIR / "connections.csv",
    DATA_DIR / "airport_transfer_times.csv",
]

if not all(file.exists() for file in required_files):

    generate_all_data()

    st.cache_data.clear()


flights, connections, transfer_times = (
    load_csv_data()
)


# ---------------------------------------------------------
# SQLite persistence
# ---------------------------------------------------------

sync_data_to_database(
    flights,
    connections,
    transfer_times,
)


# ---------------------------------------------------------
# Connection assessment
# ---------------------------------------------------------

assessment = build_connection_assessment(
    flights,
    connections,
    transfer_times,
)

save_assessments_to_database(
    assessment
)


# ---------------------------------------------------------
# Database status
# ---------------------------------------------------------

with st.sidebar:

    st.header("System Status")

    st.success("SQLite database connected")

    st.caption(
        "Synthetic operational data is persisted "
        "locally for this session."
    )


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------

st.sidebar.header("Dashboard Filters")

priority_options = [
    "ALL",
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
]

selected_priority = st.sidebar.selectbox(
    "Priority",
    priority_options,
)

status_options = [
    "ALL",
    "MISSED",
    "AT_RISK",
    "SAFE",
]

selected_status = st.sidebar.selectbox(
    "Connection Risk",
    status_options,
)


filtered = assessment.copy()

if selected_priority != "ALL":

    filtered = filtered[
        filtered["priority"] == selected_priority
    ]

if selected_status != "ALL":

    filtered = filtered[
        filtered["status"] == selected_status
    ]


# ---------------------------------------------------------
# Executive KPIs
# ---------------------------------------------------------

total_connections = len(assessment)

missed_connections = (
    assessment["status"] == "MISSED"
).sum()

at_risk_connections = (
    assessment["status"] == "AT_RISK"
).sum()

critical_connections = (
    assessment["priority"] == "CRITICAL"
).sum()


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Connections",
    total_connections,
)

col2.metric(
    "Missed",
    missed_connections,
)

col3.metric(
    "At Risk",
    at_risk_connections,
)

col4.metric(
    "Critical Priority",
    critical_connections,
)


# ---------------------------------------------------------
# Disruption Monitor
# ---------------------------------------------------------

st.subheader("Disruption Monitor")

disrupted_flights = flights[
    flights["status"].isin(
        ["DELAYED", "CANCELLED"]
    )
].copy()

disrupted_flights["affected_connections"] = (
    disrupted_flights["flight_id"]
    .map(
        assessment[
            "inbound_flight_id"
        ].value_counts()
    )
    .fillna(0)
    .astype(int)
)


monitor_col1, monitor_col2, monitor_col3 = (
    st.columns(3)
)

monitor_col1.metric(
    "Disrupted Flights",
    len(disrupted_flights),
)

monitor_col2.metric(
    "Delayed Flights",
    (
        disrupted_flights["status"] == "DELAYED"
    ).sum(),
)

monitor_col3.metric(
    "Cancelled Flights",
    (
        disrupted_flights["status"] == "CANCELLED"
    ).sum(),
)


disruption_col1, disruption_col2 = (
    st.columns(2)
)


with disruption_col1:

    disruption_counts = (
        disrupted_flights["status"]
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )

    fig_disruptions = px.bar(
        disruption_counts,
        x="status",
        y="count",
        title="Flight Disruptions",
        labels={
            "status": "Flight Status",
            "count": "Flights",
        },
    )

    st.plotly_chart(
        fig_disruptions,
        use_container_width=True,
    )


with disruption_col2:

    delayed_flights = disrupted_flights[
        disrupted_flights["status"] == "DELAYED"
    ].copy()

    delayed_flights = delayed_flights.sort_values(
        "delay_minutes",
        ascending=False,
    )

    fig_delay = px.bar(
        delayed_flights.head(10),
        x="flight_id",
        y="delay_minutes",
        title="Largest Flight Delays",
        labels={
            "flight_id": "Flight",
            "delay_minutes": "Delay (minutes)",
        },
    )

    st.plotly_chart(
        fig_delay,
        use_container_width=True,
    )


st.write("### Disrupted Flight Details")

disruption_columns = [
    "flight_id",
    "airline",
    "origin",
    "destination",
    "scheduled_arrival",
    "actual_arrival",
    "delay_minutes",
    "status",
    "affected_connections",
]

st.dataframe(
    disrupted_flights[
        disruption_columns
    ].sort_values(
        "delay_minutes",
        ascending=False,
    ),
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Operational Overview
# ---------------------------------------------------------

st.subheader("Operational Overview")

chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    status_counts = (
        assessment["status"]
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )

    fig_status = px.bar(
        status_counts,
        x="status",
        y="count",
        title="Connection Risk Status",
        labels={
            "status": "Risk Status",
            "count": "Connections",
        },
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True,
    )


with chart_col2:

    priority_counts = (
        assessment["priority"]
        .value_counts()
        .rename_axis("priority")
        .reset_index(name="count")
    )

    fig_priority = px.bar(
        priority_counts,
        x="priority",
        y="count",
        title="Operational Priority",
        labels={
            "priority": "Priority",
            "count": "Connections",
        },
    )

    st.plotly_chart(
        fig_priority,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Connection Rescue Queue
# ---------------------------------------------------------

st.subheader("🚨 Connection Rescue Queue")

st.write(
    "Passengers are ordered by operational priority. "
    "Higher scores indicate greater urgency."
)


rescue_queue = filtered[
    filtered["priority"].isin(
        ["CRITICAL", "HIGH"]
    )
].copy()

rescue_queue = rescue_queue.sort_values(
    by=[
        "priority_score",
        "buffer_minutes",
    ],
    ascending=[
        False,
        True,
    ],
)


queue_col1, queue_col2, queue_col3 = (
    st.columns(3)
)

queue_col1.metric(
    "Rescue Cases",
    len(rescue_queue),
)

queue_col2.metric(
    "Critical",
    (
        rescue_queue["priority"] == "CRITICAL"
    ).sum(),
)

queue_col3.metric(
    "High",
    (
        rescue_queue["priority"] == "HIGH"
    ).sum(),
)


rescue_columns = [
    "connection_id",
    "passenger_id",
    "inbound_flight_id",
    "onward_flight_id",
    "inbound_delay_minutes",
    "available_minutes",
    "required_minutes",
    "buffer_minutes",
    "status",
    "priority_score",
    "priority",
]


if rescue_queue.empty:

    st.success(
        "No critical or high-priority rescue cases "
        "match the current filters."
    )

else:

    st.dataframe(
        rescue_queue[
            rescue_columns
        ],
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Connection Assessment Queue
# ---------------------------------------------------------

st.subheader("Connection Assessment Queue")

display_columns = [
    "connection_id",
    "passenger_id",
    "inbound_flight_id",
    "onward_flight_id",
    "inbound_delay_minutes",
    "available_minutes",
    "required_minutes",
    "buffer_minutes",
    "status",
    "priority_score",
    "priority",
]

display_data = filtered.sort_values(
    by="priority_score",
    ascending=False,
)[display_columns]

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Database preview
# ---------------------------------------------------------

with st.expander("Database Records"):

    database_assessments = load_table(
        "connection_assessments"
    )

    st.write(
        f"Stored assessment records: "
        f"{len(database_assessments)}"
    )

    st.dataframe(
        database_assessments.head(10),
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "Synthetic data • Python • Pandas • Pydantic • "
    "SQLite • Streamlit • Plotly"
)