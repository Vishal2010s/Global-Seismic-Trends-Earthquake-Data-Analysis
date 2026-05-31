from sqlalchemy import create_engine, select
import pandas as pd
import streamlit as st
import pymysql

# Database connection
engine = create_engine('mysql+pymysql://root:Mwin%402028@127.0.0.1:3306/EQ')
# SQL QUERIES
queries = {
    "1.Top 10 strongest earthquakes (mag):": ""
        "SELECT id, mag, updated, country, type FROM EQ_DATA ORDER BY mag DESC LIMIT 11",
    "2.Top 10 deepest earthquakes (depth_km): ": ""
        "SELECT id, depth_km, mag, updated, country, type FROM EQ_DATA ORDER BY depth_km DESC LIMIT 11",
    "3.Shallow earthquakes < 50 km and mag > 7.5:": ""
        "SELECT id,EQ_type, depth_km, mag, updated, country FROM EQ_DATA WHERE EQ_type='SHALLOW' AND depth_km < 50 AND mag > 7.5",
    "4. Average depth per continent:":""
        "SELECT CONTINENT, AVG(DEPTH_KM) AS AVG_DEPTH FROM EQ_DATA GROUP BY CONTINENT ORDER BY AVG_DEPTH DESC",
    "5. Average magnitude per magnitude type (magType):":""
        "select magtype, AVG(mag) as avg_mag from EQ_DATA group by magtype",
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
        "select country, " \
        "sum(case when EQ_itensity='Light' then 0 when EQ_itensity='Minor' then 10 when EQ_itensity='Moderate' then 100 when EQ_itensity='Strong' then 1000 when EQ_itensity='Destructive' then 10000 else 0 end) as estimated_casualities " \
        "from EQ_data group by country order by estimated_casualities desc limit 5",
    "12. Total estimated economic loss per continent:":""
        "select continent, " \
        "sum(case when EQ_itensity='Light' then 1000 when EQ_itensity='Minor' then 5000 when EQ_itensity='Moderate' then 10000 when EQ_itensity='Strong' then 50000 when EQ_itensity='Destructive' then 100000 else 0 end) as estimated_loss " \
        "from EQ_data group by continent order by estimated_loss desc",
    "13. Average economic loss by alert level:":""
        """SELECT alert,AVG(CASE WHEN alert='green'THEN 1000 WHEN alert='yellow' THEN 5000 WHEN alert='orange' THEN 50000 WHEN alert='red' THEN 100000 ELSE 0 END) AS avg_loss
            FROM EQ_data WHERE alert!='Data_Not_available' GROUP BY alert ORDER BY alert DESC""",
    "14. Count of reviewed vs automatic earthquakes (status):":""
        "select status, count(*) as count from EQ_data group by status order by count desc",
    "15. Count by earthquake type (type):":""
        "select type, count(*) as Total_no_of_earthquakes from EQ_data group by type order by Total_no_of_earthquakes desc",
    "16. Number of earthquakes by data type (types):":""
        "select types, count(*) as Total_no_of_earthquakes from EQ_data group by types order by Total_no_of_earthquakes desc",
    "17. Average RMS and gap per continent:":""
        "select continent, avg(rms) as avg_rms, avg(gap) as avg_gap from EQ_data group by continent order by continent asc",
    "18. Events with high station coverage (nst > threshold):":""
        "select nst, count(*) as Total_Events from EQ_data where nst>10 group by nst order by Total_Events desc",
    "19. Number of tsunamis triggered per year:":""
        "select year, count(*) as tsunami_count from EQ_data where tsunami=1 group by year order by tsunami_count desc",
    "20. Count earthquakes by alert levels (red, orange, etc.):":""
        "select alert, count(*) as Total_no_of_earthquakes from EQ_data group by alert order by Total_no_of_earthquakes desc",
    "21. Find the top 5 countries with the highest average magnitude of earthquakes in the past 5 years:":""
        "select country, avg(mag) as avg_mag from EQ_data group by country order by avg_mag desc limit 5",             	
    "22. Find countries that have experienced both shallow and deep earthquakes within the same month:":""
        "SELECT country,month,year FROM EQ_data WHERE EQ_type IN ('Shallow', 'Deep') GROUP BY month,year,country HAVING COUNT(DISTINCT EQ_type) = 2 order by year",
    "23. Compute the year-over-year growth rate in the total number of earthquakes globally:":""
        "select year, count(*) as count, lag (count(*)) over( order by year) as prev_year_count, (count(*) - lag (count(*)) over(order by year)) / lag(count(*)) over(order by year) * 100 as growth_rate"
        " from EQ_data group by year order by year",
    "24. List the 3 most seismically active regions by combining both frequency and average magnitude:":""
        "select country, count(*) as count, avg(mag) as avg_mag, (count(*)*avg(mag)) as seismic_activity from EQ_data group by country order by seismic_activity desc limit 3",
    "25. For each country calculate the average depth of earthquakes within ±5° latitude range of the equator:":""
        "select country, avg(depth_km) as avg_depth, avg(latitude) as avg_latitude from Eq_data where latitude between -5 and 5 group by country order by avg_latitude",
    "26. Identify countries having the highest ratio of shallow to deep earthquakes:":""
        "select country, sum(case when EQ_type='Shallow' then 1 else 0 end) as shallow_count," \
        "sum(case when EQ_type='Deep' then 1 else 0 end) as deep_count,"\
        "(sum(case when EQ_type='Shallow' then 1 else 0 end) / sum(case when EQ_type='Deep' then 1 else 0 end)) as ratio " \
        "from EQ_data group by country order by ratio desc limit 10",
    "27. Avg magnitude difference (tsunami vs non-tsunami):":""
        "SELECT AVG(CASE WHEN tsunami=1 THEN mag END) AS avg_mag_tsunami, AVG(CASE WHEN tsunami=0 THEN mag END) AS avg_mag_no_tsunami, "
        "(AVG(CASE WHEN tsunami=1 THEN mag END) - AVG(CASE WHEN tsunami=0 THEN mag END)) AS magnitude_difference FROM EQ_data",
    "28. Using the gap and rms columns identify events with the lowest data reliability (highest average error margins):":""
        "select id, country, updated, (gap+rms) as reliability_score from EQ_data order by reliability_score desc limit 10",
    "29. Find pairs of consecutive earthquakes (by time) that occurred within 50 km of each other and within 1 hour:":"select '⚠️Required complex logic to derive from Latitude, longitude and hour columns' as note⚠️",
    "30. Determine the regions with the highest frequency of deep-focus earthquakes (depth > 300 km):":""
        "select country, count(*) as No_of_highest_frequency_deep_focus_EQ from Eq_data where depth_km>300 group by country order by No_of_highest_frequency_deep_focus_EQ desc limit 10",

}
# Streamlit UI
# st.image("assets/warning.gif", caption="Warning Animation")
st.title("🌍Global Seismic Trends-Earthquake Data Analysis Dashboard")
st.write("🔍Select any problem statement (1-30) to run the analysis of the Earthquake information for the last 5 years.")

# Dropdown
task = st.selectbox("Select any query of your choice", list(queries.keys()))
if st.button("Run Query"):
    query = queries[task]
    df = pd.read_sql(query, engine)

    # Add serial number column (1-based)
    df = df.reset_index(drop=True)
    df.insert(0, "S.No", range(1, len(df) + 1))
    

    st.subheader(f"""
    **Result:**\n
    *{task}*
""")

    st.dataframe(df, use_container_width=True, hide_index=True)
    # st.table(df)


# Special handling for queries 
    if task == "7. Month with highest number of earthquakes:":
        st.write(
            f"📊 Specific month in a year with highest number of earthquakes: "
            f"{df.iloc[0]['month']}th month in {df.iloc[0]['year']}, "
            f"Count: {df.iloc[0]['count']}"
        )

    if task == "7.1. Month with highest number of earthquakes consolidated in last 5 years:":
        st.write(
            f"📊 Month with highest number of earthquakes consolidated in last 5 years: "
            f"Month {df.iloc[0]['month']} with total Count of {df.iloc[0]['count']}"
        )
    if task=="8. Day of week with most earthquakes:":
        st.write(
            f"📊Day of the week where most Earthquakes held in last 5 years is {df.iloc[0]['day_of_week']} with total of {df.iloc[0]['count']} Earthquakes"
        )
    if task=="11. Top 5 places with highest casualties:":
        st.write(
            f"⚠️Note: This is an estimated casuality figures arrived based on intensity levels:- when EQ_itensity='Light' then 0 casualties when EQ_itensity='Minor' then 10 when EQ_itensity='Moderate' then 100 when EQ_itensity='Strong' then 1000 when EQ_itensity='Destructive' then 10000.These are not actual data, only approximations⚠️"
        )
    if task=="12. Total estimated economic loss per continent:":
         st.write(
        """⚠️Note: This is an estimated loss figure arrived based on intensity levels:
        - when EQ_itensity='Light' → loss ≈ 1000
        - when EQ_itensity='Minor' → loss ≈ 5000
        - when EQ_itensity='Moderate' → loss ≈ 10000
        - when EQ_itensity='Strong' → loss ≈ 50000
        - when EQ_itensity='Destructive' → loss ≈ 100000.
        These are not actual data, only approximations ⚠️"""
    )
    if task=="13. Average economic loss by alert level:":
        st.write(
            f"⚠️Note: This is an estimated average figures arrived based on alert levels:-when alert='green' then 1000 when alert='yellow' then 5000 when alert='orange' then 50000 when alert='red' then 100000.These are not actual data, only approximations⚠️"
        )
