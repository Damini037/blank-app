import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load the data with error handling
@st.cache_data
def load_data(file):
    try:
        chunk_list = []
        chunksize = 50000
        for chunk in pd.read_csv(
            file, 
            encoding='latin1', 
            engine='python', 
            chunksize=chunksize, 
            on_bad_lines='skip',  
            sep=',',  
        ):
            chunk_list.append(chunk)
        data = pd.concat(chunk_list, axis=0)
        
        # Convert datetime columns if available
        if 'tpep_pickup_datetime' in data.columns:
            data['tpep_pickup_datetime'] = pd.to_datetime(data['tpep_pickup_datetime'], errors='coerce')
        if 'tpep_dropoff_datetime' in data.columns:
            data['tpep_dropoff_datetime'] = pd.to_datetime(data['tpep_dropoff_datetime'], errors='coerce')
        
        # Calculate trip duration if applicable
        if 'tpep_pickup_datetime' in data.columns and 'tpep_dropoff_datetime' in data.columns:
            data['trip_duration_minutes'] = (
                (data['tpep_dropoff_datetime'] - data['tpep_pickup_datetime']).dt.total_seconds() / 60
            )
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Streamlit App
st.title("🚖 NYC Taxi Data Analysis 🗽")
st.write("Upload the NYC Taxi dataset to analyze passenger count, payment type, fares, and more! 📊")

# File uploader with size check
file = st.file_uploader("Upload CSV File 📥", type=["csv"])

if file is not None:
    data = load_data(file)

    if data is None or data.empty:
        st.error("No data available for analysis. Please check the dataset. ❌")
    else:
        st.success("Data loaded successfully! ✅")
        st.write("Columns in the dataset 🗂️:", data.columns)
        st.write(data.head())

        # Check for missing data
        st.write("Missing values in dataset: ❓", data.isnull().sum())

        # Sidebar for analysis options
        st.sidebar.title("Choose an Analysis 📈")
        analysis_option = st.sidebar.selectbox("Analysis Type 🔍", [
            "Passenger Count Distribution 📊",
            "Payment Type Distribution 💳",
            "Fare Amount Distribution 💸",
            "Tip Amount Distribution 💰",
            "Total Amount Distribution 💵",
            "Busiest Hours 🕒",
            "Top 3 Boroughs 🏙️",
            "Top 5 Routes in Manhattan 🚖",
            "Inter Borough Transition (Heatmap) 🌉",
            "Traffic Heatmap - Avg Rides per Weekday Hour 🗓️",
            "Revenue Share by Pickup Zones 📊",
            "Hourly Total Amount and Tips ⏰",
        ])

        # Function to plot distribution
        def plot_distribution(column, title):
            if column not in data.columns:
                st.error(f"Column '{column}' not found in the data. 🚨")
                return
            data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
            fig, ax = plt.subplots()
            sns.histplot(data[column], kde=True, ax=ax)
            ax.set_title(title)
            ax.set_xlabel(column)
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

        # Function for busiest hours
        def busiest_hours():
            if 'tpep_pickup_datetime' in data.columns:
                data['hour'] = data['tpep_pickup_datetime'].dt.hour
                busiest = data['hour'].value_counts().sort_index()
                fig, ax = plt.subplots()
                busiest.plot(kind='bar', ax=ax)
                ax.set_title("Busiest Hours (Pickup Times) ⏰")
                ax.set_xlabel("Hour of the Day 🕐")
                ax.set_ylabel("Number of Pickups 🚖")
                st.pyplot(fig)
            else:
                st.error("Datetime column not found in the dataset. 📅")

        # Function for Top 3 Boroughs
        def top_boroughs():
            if 'PULocationID' in data.columns:
                borough_counts = data['PULocationID'].value_counts().head(3)
                st.write("Top 3 Boroughs 🏙️:", borough_counts)
            else:
                st.error("Location data not found in the dataset. 📍")

        # Function for Traffic Heatmap
        def traffic_heatmap():
            if 'hour' in data.columns:
                hourly_data = data.groupby(['hour', data['tpep_pickup_datetime'].dt.weekday]).size().reset_index(name="count")
                fig = px.density_heatmap(hourly_data, x='hour', y='tpep_pickup_datetime', z='count',
                                         labels={'hour': 'Hour of the Day 🕒', 'tpep_pickup_datetime': 'Weekday 📅'})
                fig.update_layout(title="Traffic Heatmap - Avg Rides per Weekday Hour 🗓️")
                st.plotly_chart(fig)
            else:
                st.error("Data for generating heatmap not found. 🔥")

        # Function for Revenue Share by Pickup Zones
        def revenue_share_by_pickup_zones():
            if 'PULocationID' in data.columns:
                revenue_data = data.groupby('PULocationID')['total_amount'].sum().reset_index()
                total_revenue = revenue_data['total_amount'].sum()
                revenue_data['percentage'] = (revenue_data['total_amount'] / total_revenue) * 100
                fig, ax = plt.subplots()
                sns.barplot(x='PULocationID', y='percentage', data=revenue_data, ax=ax)
                ax.set_title("Revenue Share by Pickup Zones 📊")
                ax.set_xlabel("Pickup Zones 🗺️")
                ax.set_ylabel("Percentage (%) 💯")
                st.pyplot(fig)
            else:
                st.error("Pickup zone data not available. 🏙️")

        # Function for Hourly Total Amount and Tips
        def hourly_total_and_tips():
            if 'tpep_pickup_datetime' in data.columns:
                data['hour'] = data['tpep_pickup_datetime'].dt.hour
                hourly_data = data.groupby('hour').agg({'total_amount': 'sum', 'tip_amount': 'sum'}).reset_index()
                fig, ax = plt.subplots()
                ax.plot(hourly_data['hour'], hourly_data['total_amount'], label='Total Amount 💵', color='b')
                ax.plot(hourly_data['hour'], hourly_data['tip_amount'], label='Tips 💰', color='g')
                ax.set_title("Hourly Total Amount and Tips ⏰💵💰")
                ax.set_xlabel("Hour of the Day 🕒")
                ax.set_ylabel("Amount ($) 💲")
                ax.legend()
                st.pyplot(fig)
            else:
                st.error("Data for calculating hourly amounts not found. 💸")

        # Execute analysis based on user selection
        if analysis_option == "Passenger Count Distribution 📊":
            plot_distribution("passenger_count", "Passenger Count Distribution 📊")

        elif analysis_option == "Payment Type Distribution 💳":
            plot_distribution("payment_type", "Payment Type Distribution 💳")

        elif analysis_option == "Fare Amount Distribution 💸":
            plot_distribution("fare_amount", "Fare Amount Distribution 💸")

        elif analysis_option == "Tip Amount Distribution 💰":
            plot_distribution("tip_amount", "Tip Amount Distribution 💰")

        elif analysis_option == "Total Amount Distribution 💵":
            plot_distribution("total_amount", "Total Amount Distribution 💵")

        elif analysis_option == "Busiest Hours 🕒":
            busiest_hours()

        elif analysis_option == "Top 3 Boroughs 🏙️":
            top_boroughs()

        elif analysis_option == "Traffic Heatmap - Avg Rides per Weekday Hour 🗓️":
            traffic_heatmap()

        elif analysis_option == "Revenue Share by Pickup Zones 📊":
            revenue_share_by_pickup_zones()

        elif analysis_option == "Hourly Total Amount and Tips ⏰":
            hourly_total_and_tips()

else:
    st.info("Please upload a CSV file to proceed. 📂")

# Footer
st.write("Developed with ❤️ using Streamlit 🚀")
