import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
@st.cache_data
def load_data():
    try:
        # Try reading the CSV file with specific encoding and handle bad lines
        data = pd.read_csv("nyc_taxi_data.csv", encoding='utf-8', low_memory=False, on_bad_lines='skip')
        
        # Convert datetime columns
        data['tpep_pickup_datetime'] = pd.to_datetime(data['tpep_pickup_datetime'])
        data['tpep_dropoff_datetime'] = pd.to_datetime(data['tpep_dropoff_datetime'])

        # Calculate trip duration in minutes
        data['trip_duration_minutes'] = (data['tpep_dropoff_datetime'] - data['tpep_pickup_datetime']).dt.total_seconds() / 60
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# Load the data
data = load_data()

# Sidebar options
st.sidebar.title("NYC Taxi Data Analysis")
analysis_option = st.sidebar.selectbox("Choose an Analysis", [
    "Passenger Count Distribution",
    "Payment Type Distribution",
    "Fare Amount Distribution",
    "Tip Amount Distribution",
    "Total Amount Distribution",
    "Busiest Hours",
    "Top Boroughs",
    "Top Routes in Manhattan",
    "Inter-Borough Heatmap",
    "Traffic Heatmap (Avg Rides per Weekday Hour)",
    "Revenue Share by Pickup Zones",
    "Hourly Total Amount and Tips"
])

# Analysis Functions
def plot_distribution(column, title):
    if column not in data.columns:
        st.error(f"Column '{column}' not found in data.")
        return

    # Ensure the column is numeric
    data[column] = pd.to_numeric(data[column], errors='coerce')  # Coerce invalid values to NaN
    data[column] = data[column].fillna(0)  # Handle NaN values by filling with 0

    # Plot the histogram
    fig, ax = plt.subplots()
    sns.histplot(data[column], kde=False, ax=ax)
    ax.set_title(title)
    st.pyplot(fig)    
    

def busiest_hours(data):
    st.title("Top 5 Busiest Hours")
    data['hour'] = data['tpep_pickup_datetime'].dt.hour
    busiest = data['hour'].value_counts().head(5)
    st.bar_chart(busiest)

def top_boroughs(data):
    st.title("Top 3 Boroughs")
    # Add mapping of Location IDs to Borough names here
    st.write("This requires mapping `PULocationID` and `DOLocationID` to Borough names.")

def top_routes(data):
    st.title("Top 5 Routes in Manhattan")
    # Filter data for Manhattan and calculate routes
    st.write("This requires filtering and route calculation.")

def inter_borough_heatmap(data):
    st.title("Inter-Borough Transition Heatmap")
    # Add heatmap logic for transitions
    st.write("Requires mapping `PULocationID` and `DOLocationID` to Borough names.")

def traffic_heatmap(data):
    st.title("Traffic Heatmap - Avg Rides Per Weekday Hour")
    data['weekday_hour'] = data['tpep_pickup_datetime'].dt.strftime('%A-%H')
    avg_rides = data.groupby('weekday_hour').size().mean(level='weekday_hour')
    st.line_chart(avg_rides)

def revenue_share(data):
    st.title("Revenue Share by Pickup Zones")
    revenue = data.groupby('PULocationID')['total_amount'].sum()
    revenue_share = (revenue / revenue.sum()) * 100
    st.bar_chart(revenue_share)

def hourly_analysis(data):
    st.title("Hourly Total Amount and Tips")
    data['hour'] = data['tpep_pickup_datetime'].dt.hour
    hourly_totals = data.groupby('hour')[['total_amount', 'tip_amount']].sum()
    st.line_chart(hourly_totals)

# Analysis Execution
if analysis_option == "Passenger Count Distribution":
    plot_distribution("passenger_count", "Passenger Count Distribution")
elif analysis_option == "Payment Type Distribution":
    plot_distribution("payment_type", "Payment Type Distribution")
elif analysis_option == "Fare Amount Distribution":
    plot_distribution("fare_amount", "Fare Amount Distribution")
elif analysis_option == "Tip Amount Distribution":
    plot_distribution("tip_amount", "Tip Amount Distribution")
elif analysis_option == "Total Amount Distribution":
    plot_distribution("total_amount", "Total Amount Distribution")
elif analysis_option == "Busiest Hours":
    busiest_hours(data)
elif analysis_option == "Top Boroughs":
    top_boroughs(data)
elif analysis_option == "Top Routes in Manhattan":
    top_routes(data)
elif analysis_option == "Inter-Borough Heatmap":
    inter_borough_heatmap(data)
elif analysis_option == "Traffic Heatmap (Avg Rides per Weekday Hour)":
    traffic_heatmap(data)
elif analysis_option == "Revenue Share by Pickup Zones":
    revenue_share(data)
elif analysis_option == "Hourly Total Amount and Tips":
    hourly_analysis(data)
