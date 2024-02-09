import streamlit as st
import pandas as pd
from urllib.error import URLError

def get_athlete_data():
    df = pd.read_csv("/Users/carmencolomer/Dropbox/2024/Titans/Drill_Predictor/output_file_average_by_period_and_position_new.csv")
    return df

try:
    st.title("Titans Drill Predictor")  # Adding the heading
    
    # Adding the logo in the top right-hand side
    st.image("/Users/carmencolomer/Dropbox/2024/Titans/Drill_Predictor/Gold-Coast-Titans-Logo.png", width=300)

    df = get_athlete_data()
    period_names = st.multiselect("Choose period names", df["Period Name"].unique())
    
    # Allow users to input durations for each selected period name
    period_durations = {}
    for period_name in period_names:
        period_durations[period_name] = st.number_input(f"Enter duration for {period_name} (minutes):",
                                                        min_value=0,
                                                        value=60)
    
    positions = st.multiselect("Choose positions", df["Position"].unique())
    
    if not period_names or not positions:
        st.error("Please select at least one period name and one position.")
    else:
        # Initialize total_metrics DataFrame to accumulate metrics
        total_metrics = pd.DataFrame(index=positions, columns=[
            "Total Distance Per Minute",
            "HSD Per Minute",
            "VHSD Per Minute",
            "Sprint Distance Per Minute",
            "Acceleration B2-3 Total Efforts (Gen 2) Per Minute",
            "Acceleration B3 Efforts (Gen 2) Per Minute"
        ]).fillna(0.0)
        
        # Calculate sum of metrics for selected period names based on their durations
        for period_name in period_names:
            period_duration = period_durations[period_name]
            period_data = df[(df["Period Name"] == period_name) & (df["Position"].isin(positions))]
            avg_metrics_per_minute = period_data.groupby("Position").agg({
                "Total Distance Per Minute": "mean",
                "HSD Per Minute": "mean",
                "VHSD Per Minute": "mean",
                "Sprint Distance Per Minute": "mean",
                "Acceleration B2-3 Total Efforts (Gen 2) Per Minute": "mean",
                "Acceleration B3 Efforts (Gen 2) Per Minute": "mean"
            })
            total_metrics = total_metrics.add(avg_metrics_per_minute * period_duration, fill_value=0)
        
        # Add the average row
        average_row = total_metrics.mean(axis=0)
        total_metrics = total_metrics.append(average_row, ignore_index=True)
        total_metrics.index = list(positions) + ["Average"]
        
        st.write("### Totals for Selected Periods and Durations", total_metrics)

        # Plot vertical bar chart for average values
        st.write("### Average Values")
        st.bar_chart(average_row)

except FileNotFoundError:
    st.error("Athlete data file not found. Please make sure the file exists.")
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )
