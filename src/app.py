"""Interactive Streamlit dashboard for Global Seismic Trends."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent
# from output1_catalog import EQ_DATA, QUERIES


# =========================================================
# ENVIRONMENT & DATA
# =========================================================

load_dotenv(PROJECT_ROOT / ".env", override=False)

EQ_DATA="eq_table1"
# SQL QUERIES
QUERIES = {
    "1.Top 10 strongest earthquakes (mag):": ""
        "SELECT id, mag, updated, country, type FROM EQ_DATA ORDER BY mag DESC,time desc LIMIT 10",
    "2.Top 10 deepest earthquakes (depth_km): ": ""
        "SELECT id, depth_km, mag, updated, country, type FROM EQ_DATA ORDER BY depth_km DESC, time desc LIMIT 10",
    "3.Shallow earthquakes < 50 km and mag > 7.5:": ""
        "SELECT id,EQ_type, depth_km, mag, updated, country FROM EQ_DATA WHERE EQ_type='SHALLOW' AND depth_km < 50 AND mag > 7.5 order by mag desc ",
    "4. Average depth per continent:":""
        "SELECT CONTINENT, AVG(DEPTH_KM) AS AVG_DEPTH FROM EQ_DATA GROUP BY CONTINENT ORDER BY AVG_DEPTH DESC",
    "5. Average magnitude per magnitude type (magType):":""
        "select magtype, ROUND(AVG(mag),3) as avg_mag from EQ_DATA group by magtype ORDER BY avg_mag desc",
    "6. Year with most earthquakes:":""
        "select year, count(*) as Highest_no_of_EQ from EQ_data group by year order by Highest_no_of_EQ desc limit 1",   
    "7. Month with highest number of earthquakes:": 
        "SELECT month, year, count(*) as Highest_no_of_EQ  FROM EQ_data GROUP BY month, year ORDER BY Highest_no_of_EQ DESC LIMIT 1",
    "7.1. Month with highest number of earthquakes consolidated in last 5 years:": 
        "SELECT month, count(*) as Highest_no_of_EQ FROM EQ_data GROUP BY month ORDER BY Highest_no_of_EQ DESC LIMIT 1",
    "8. Day of week with most earthquakes:":""
        "select day_of_week, count(*) as Highest_no_of_EQ from EQ_data group by day_of_week order by Highest_no_of_EQ desc limit 1",
    "9. Count of earthquakes per hour of day:": ""
        "select hour, count(*) as No_of_EQ_per_hour from EQ_data group by hour order by hour",
    "10. Most active reporting network (net):":""
        "select net, count(*) as Most_active_reporting_network from EQ_data group by net order by Most_active_reporting_network desc",
    "11. Top 5 places with highest casualties:":""
        "select country, COUNT(*) AS event_count, " \
        "sum(case when EQ_intensity='Minor' then 0 when EQ_intensity='Light' then 10 when EQ_intensity='Moderate' then 100 when EQ_intensity='Strong' then 1000 when EQ_intensity='Destructive' then 10000 else 0 end) as estimated_casualities " \
        "from EQ_data group by country order by estimated_casualities desc limit 5",
    "12. Total estimated economic loss per continent:":""
        "select continent, COUNT(*) AS event_count," \
        "sum(case when EQ_intensity='Minor' then 1000 when EQ_intensity='Light' then 5000 when EQ_intensity='Moderate' then 10000 when EQ_intensity='Strong' then 50000 when EQ_intensity='Destructive' then 100000 else 0 end) as estimated_loss " \
        "from EQ_data group by continent order by estimated_loss desc",
    "13. Average economic loss by alert level:":""
        """SELECT alert,COUNT(*) AS event_count,AVG(CASE WHEN alert='green'THEN 1000 WHEN alert='yellow' THEN 5000 WHEN alert='orange' THEN 50000 WHEN alert='red' THEN 100000 ELSE 0 END) AS avg_loss
            FROM EQ_data WHERE alert!='Data_Not_available' GROUP BY alert ORDER BY avg_loss DESC""",
    "14. Count of reviewed vs automatic earthquakes (status):":""
        "select status, count(*) as count from EQ_data group by status order by count desc",
    "15. Count by earthquake type (type):":""
        "select type, count(*) as Total_no_of_earthquakes from EQ_data group by type order by Total_no_of_earthquakes desc",
    "16. Number of earthquakes by data type (types):" :"""
        # "select types, count(*) as Total_no_of_earthquakes from EQ_data group by types order by Total_no_of_earthquakes desc",              
        SELECT
            TRIM(jt.product) AS product,
            COUNT(*) AS event_count
        FROM EQ_data AS e
        CROSS JOIN JSON_TABLE(
            CONCAT(
                '["',
                REPLACE(
                    TRIM(BOTH ',' FROM e.types),
                    ',',
                    '","'
                ),
                '"]'
            ),
            '$[*]' COLUMNS(
                product VARCHAR(100) PATH '$'
            )
        ) AS jt
        WHERE e.types IS NOT NULL
        AND TRIM(BOTH ',' FROM e.types) <> ''
        GROUP BY TRIM(jt.product)
        ORDER BY event_count DESC
    """,
    "17. Average RMS and gap per continent:":""
        "select continent,COUNT(*) AS event_count, ROUND(AVG(rms), 2) as avg_rms, ROUND(AVG(gap), 2) as avg_gap from EQ_data group by continent order by continent asc",
    "18. Events with high station coverage (nst > threshold):":""
        "select id,time, country,mag, nst from EQ_data where nst>100  group by id,time, country,mag, nst order by nst desc, time desc limit 100",
    "19. Number of tsunamis triggered per year:":""
        "select year, count(*) as tsunami_count from EQ_data where tsunami=1 group by year order by year",
    "20. Count earthquakes by alert levels (red, orange, etc.):":""
        "select alert, count(*) as Total_no_of_earthquakes from EQ_data group by alert order by Total_no_of_earthquakes desc",
    "21. Find the top 5 countries with the highest average magnitude of earthquakes in the past 5 years:":""
        "select country,COUNT(*) AS event_count, ROUND(avg(mag),3) as avg_mag from EQ_data group by country HAVING COUNT(*) >= 20 order by avg_mag desc limit 5",    	
    "22. Find countries that have experienced both shallow and deep earthquakes within the same month:":""
        "SELECT country,month,year FROM EQ_data WHERE EQ_type IN ('Shallow', 'Deep') GROUP BY month,year,country HAVING COUNT(DISTINCT EQ_type) = 2 order by year",
    "23. Compute the year-over-year growth rate in the total number of earthquakes globally:":""
        "select year, count(*) as count, lag (count(*)) over( order by year) as prev_year_count, (count(*) - lag (count(*)) over(order by year)) / lag(count(*)) over(order by year) * 100 as growth_rate"
        " from EQ_data group by year order by year",
    "24. List the 3 most seismically active regions by combining both frequency and average magnitude:":""
        "select country, count(*) as count, ROUND(AVG(mag), 3) as avg_mag, (count(*)*ROUND(AVG(mag), 3)) as seismic_activity from EQ_data group by country order by seismic_activity desc limit 3",
    "25. For each country calculate the average depth of earthquakes within ±5° latitude range of the equator:":""
        "select country,count(*) as event_count, ROUND(AVG(depth_km), 2) as avg_depth, ROUND(AVG(latitude), 3) as avg_latitude from Eq_data where latitude between -5 and 5 group by country having count(*)>=5 order by avg_depth desc",
    "26. Identify countries having the highest ratio of shallow to deep earthquakes:":""
        "select country, sum(case when EQ_type='Shallow' then 1 else 0 end) as shallow_count," \
        "sum(case when EQ_type='Deep' then 1 else 0 end) as deep_count,"\
        "(sum(case when EQ_type='Shallow' then 1 else 0 end) / sum(case when EQ_type='Deep' then 1 else 0 end)) as ratio " \
        "from EQ_data group by country having count(*)>=20 and deep_count>=3 order by ratio desc limit 10",
    "27. Avg magnitude difference (tsunami vs non-tsunami):":""
        "SELECT AVG(CASE WHEN tsunami=1 THEN mag END) AS avg_mag_tsunami, AVG(CASE WHEN tsunami=0 THEN mag END) AS avg_mag_no_tsunami, "
        "(AVG(CASE WHEN tsunami=1 THEN mag END) - AVG(CASE WHEN tsunami=0 THEN mag END)) AS magnitude_difference FROM EQ_data",
    "28. Using the gap and rms columns identify events with the lowest data reliability (highest average error margins):":""
        "select id, country, updated, (gap+rms) as reliability_score from EQ_data order by reliability_score desc limit 10",
    "29. Find pairs of consecutive earthquakes (by time) that occurred within 50 km of each other and within 1 hour:":"select '⚠️Required complex logic to derive from Latitude, longitude and hour columns' as note⚠️",
    "30. Determine the regions with the highest frequency of deep-focus earthquakes (depth > 300 km):":""
        "select country, count(*) as No_of_highest_frequency_deep_focus_EQ , ROUND(AVG(depth_km),2) AS avg_depth_km from Eq_data where depth_km>300 group by country order by No_of_highest_frequency_deep_focus_EQ desc limit 10",

}
# =========================================================
# STREAMLIT PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Global Seismic Trends",
    page_icon="🌍",
    layout="wide",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background: #f6f8fc;
        border: 1px solid #dce3ee;
        padding: 14px 18px;
        border-radius: 12px;
    }

    .small-note {
        color: #5d687a;
        font-size: 0.9rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_resource
def database_engine() -> Engine:
    """Create and cache the MySQL connection."""

    required = [
        "MYSQL_HOST",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
    ]
    missing = [name for name in required if not os.getenv(name)]

    if missing:
        raise RuntimeError(
            "Missing .env settings: " + ", ".join(missing)
        )

    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE"),
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


# =========================================================
# SQL QUERY EXPLORER
# =========================================================

def show_special_query_handling(task: str, result: pd.DataFrame) -> None:
    """Display an additional explanation for selected query results."""

    if result.empty:
        return

    if task == "7. Month with highest number of earthquakes:":
        st.write(
            "📊 Specific month in a year with the highest number of earthquakes: "
            f"month {int(result.iloc[0]['month'])} in {int(result.iloc[0]['year'])}, "
            f"count: {int(result.iloc[0]['Highest_no_of_EQ']):,}."
        )

    elif task == "7.1. Month with highest number of earthquakes consolidated in last 5 years:":
        st.write(
            "📊 Month with the highest number of earthquakes across the last five years: "
            f"month {int(result.iloc[0]['month'])}, with a total count of "
            f"{int(result.iloc[0]['Highest_no_of_EQ']):,}."
        )

    elif task == "8. Day of week with most earthquakes:":
        st.write(
            "📊 The day of the week with the most earthquakes during the last five years is "
            f"{result.iloc[0]['day_of_week']}, with "
            f"{int(result.iloc[0]['Highest_no_of_EQ']):,} earthquakes."
        )

    elif task == "11. Top 5 places with highest casualties:":
        st.write(
            "⚠️ Note: These casualty figures are estimates based on intensity levels: "
            "Minor = 0, Light = 10, Moderate = 100, Strong = 1,000, and "
            "Destructive = 10,000. These are approximations, not actual casualty data."
        )

    elif task == "12. Total estimated economic loss per continent:":
        st.write(
            """⚠️ Note: These estimated loss figures are based on intensity levels:

            - Minor: approximately 1,000
            - Light: approximately 5,000
            - Moderate: approximately 10,000
            - Strong: approximately 50,000
            - Destructive: approximately 100,000

            These are approximations, not actual economic-loss data."""
        )

    elif task == "13. Average economic loss by alert level:":
        st.write(
            "⚠️ Note: These average figures are estimates based on alert levels: "
            "green = 1,000, yellow = 5,000, orange = 50,000, and red = 100,000. "
            "These are approximations, not actual economic-loss data."
        )



def show_query_explorer() -> None:
    """Run the SQL analytical questions and show their special explanations."""

    st.subheader("SQL Problem Statements")
    st.write(
        "Select any question to run the analysis of the Global Seismic Trends and Earthquake Insights."
    )

    task = st.selectbox(
        "Select a query",
        options=list(QUERIES.keys()),
    )

    table_name = os.getenv("MYSQL_TABLE", EQ_DATA).strip()

    if not table_name.replace("_", "").isalnum():
        st.error("MYSQL_TABLE must contain only letters, numbers and underscores.")
        return

    query = QUERIES[task]

    for table_token in ("EQ_DATA", "EQ_data", "Eq_data"):
        query = query.replace(table_token, table_name)

    if task.startswith("29."):
        query = (
            "SELECT 'This question requires distance and timestamp logic.' AS note"
        )

    with st.expander("View SQL logic"):
        st.code(query, language="sql")

    if st.button("Run selected SQL", type="primary"):
        try:
            result = pd.read_sql_query(
                query,
                database_engine(),
            )

            result = result.reset_index(drop=True)
            result.insert(0, "S.No", range(1, len(result) + 1))

            st.success(f"Query returned {len(result):,} row(s).")
            st.subheader("Result")
            st.caption(task)
            st.dataframe(result, width="stretch", hide_index=True)

            show_special_query_handling(task, result)

            st.download_button(
                "Download result as CSV",
                result.to_csv(index=False).encode("utf-8"),
                file_name="query_result.csv",
                mime="text/csv",
            )

        except Exception as exc:
            st.error(
                "The query could not run. Confirm MySQL 8+, the .env settings and "
                f"the '{table_name}' table. Error type: {type(exc).__name__}"
            )



# =========================================================
# MAIN APPLICATION
# =========================================================

def main():
    st.title(
        "🌍 Global Seismic Trends-Earthquake Data Analysis Dashboard"
    )

    st.write(
        "Select any SQL problem statement to analyse the earthquake data."
    )

    show_query_explorer()

# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()