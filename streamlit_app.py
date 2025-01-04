import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data with error handling
@st.cache_data
def load_data(file):
    try:
        chunk_list = []
        chunksize = 50000
        for chunk in pd.read_csv(file, encoding='latin1', engine='python', chunksize=chunksize, on_bad_lines='skip', sep=','):
            chunk_list.append(chunk)
        data = pd.concat(chunk_list, axis=0)
        
        # Convert datetime columns
        data['tpep_pickup_datetime'] = pd.to_datetime(data['tpep_pickup_datetime'], errors='coerce')
        data['tpep_dropoff_datetime'] = pd.to_datetime(data['tpep_dropoff_datetime'], errors='coerce')

        # Calculate trip duration if applicable
        data['trip_duration_minutes'] = (
            (data['tpep_dropoff_datetime'] - data['tpep_pickup_datetime']).dt.total_seconds() / 60
        )
        return data
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None

# Streamlit App
st.title("🚖 NYC Taxi Data Analysis")
st.write("Upload the NYC Taxi dataset to analyze passenger count, payment type, fares, and more. 📊")

# File uploader with size check
file = st.file_uploader("Upload CSV File (Max size: 100 KB) 📂", type=["csv"])

if file is not None:
    if file.size > 100 * 1024:  # Convert 100 KB to bytes
        st.error("❌ File size exceeds 100 KB. Please upload a smaller file.")
    else:
        data = load_data(file)

        if data is None or data.empty:
            st.error("❌ No data available for analysis. Please check the dataset.")
        else:
            st.success("✅ Data loaded successfully!")

            # Display the columns and the first few rows to check the data
            st.write("📋 Columns in the dataset:", data.columns)
            st.write(data.head())  # Display the first few rows of data

            # Check for missing data
            st.write("🔍 Missing values in dataset:", data.isnull().sum())

            # Sidebar for analysis options
            st.sidebar.title("📊 Choose an Analysis")
            analysis_option = st.sidebar.selectbox("Select Analysis Type", [
                "📊 Passenger Count Distribution",
                "💳 Payment Type Distribution",
                "💵 Fare Amount Distribution",
                "💰 Tip Amount Distribution",
                "💸 Total Amount Distribution",
                "⏰ Top 5 Busiest Hours",
                "🏙️ Top 3 Boroughs",
                "🚖 Top 5 Routes in Manhattan",
                "🌍 Inter Borough Transition (Heatmap)",
                "🗺️ Traffic Heatmap (Avg Rides Per Weekday Hour)",
                "💰 Revenue Share by Pickup Zones (Percentage Bar Chart)",
                "⏳ Hourly Total Amount and Tips"
            ])

            # Function to plot distribution
            def plot_distribution(column, title):
                if column not in data.columns:
                    st.error(f"❌ Column '{column}' not found in the data.")
                    return
                data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
                fig = px.histogram(data, x=column, title=title)
                st.plotly_chart(fig)

            # Top 5 Busiest Hours
            def busiest_hours():
                if 'tpep_pickup_datetime' in data.columns:
                    data['hour'] = data['tpep_pickup_datetime'].dt.hour
                    busiest = data['hour'].value_counts().sort_index().head(5)
                    fig = px.bar(busiest, x=busiest.index, y=busiest.values, title="⏰ Top 5 Busiest Hours")
                    st.plotly_chart(fig)
                else:
                    st.error("❌ Datetime column not found in the dataset.")

            # Top 3 Boroughs
            def top_boroughs():
                if 'PULocationID' in data.columns:
                    borough_counts = data['PULocationID'].value_counts().head(3)
                    fig = px.bar(borough_counts, x=borough_counts.index, y=borough_counts.values, title="🏙️ Top 3 Boroughs")
                    st.plotly_chart(fig)
                else:
                    st.error("❌ Pickup borough column not found in the dataset.")

            # Top 5 Routes in Manhattan
            def top_routes():
                if 'PULocationID' in data.columns and 'DOLocationID' in data.columns:
                    manhattan_data = data[data['PULocationID'] == 'Manhattan']  # Adjust with correct Manhattan code
                    route_counts = manhattan_data.groupby(['PULocationID', 'DOLocationID']).size().reset_index(name='count')
                    top_routes = route_counts.nlargest(5, 'count')
                    fig = px.bar(top_routes, x='PULocationID', y='count', color='DOLocationID', title="🚖 Top 5 Routes in Manhattan")
                    st.plotly_chart(fig)
                else:
                    st.error("❌ Location columns not found in the dataset.")

            # Inter Borough Transition Heatmap
            def inter_borough_transition():
                if 'PULocationID' in data.columns and 'DOLocationID' in data.columns:
                    transition_data = pd.crosstab(data['PULocationID'], data['DOLocationID'])
                    fig = px.imshow(transition_data, title="🌍 Inter Borough Transition (Heatmap)", labels={'x': 'Dropoff Location', 'y': 'Pickup Location'})
                    st.plotly_chart(fig)
                else:
                    st.error("❌ Location columns not found in the dataset.")

            # Traffic Heatmap (Avg Rides Per Weekday Hour)
            def traffic_heatmap():
                if 'tpep_pickup_datetime' in data.columns:
                    data['weekday'] = data['tpep_pickup_datetime'].dt.weekday
                    data['hour'] = data['tpep_pickup_datetime'].dt.hour
                    weekday_hour_counts = data.groupby(['weekday', 'hour']).size().reset_index(name='count')
                    fig = px.density_heatmap(weekday_hour_counts, x='hour', y='weekday', z='count', title="🗺️ Traffic Heatmap - Avg Rides Per Weekday Hour")
                    st.plotly_chart(fig)
                else:
                    st.error("❌ Datetime column not found in the dataset.")

            # Revenue Share by Pickup Zones (Percentage Bar Chart)
            def revenue_share_by_pickup_zones():
                if 'PULocationID' in data.columns and 'total_amount' in data.columns:
                    revenue_by_zone = data.groupby('PULocationID')['total_amount'].sum().reset_index()
                    revenue_by_zone['percentage'] = 100 * revenue_by_zone['total_amount'] / revenue_by_zone['total_amount'].sum()
                    fig = px.bar(revenue_by_zone, x='PULocationID', y='percentage', title="💰 Revenue Share by Pickup Zones", labels={'percentage': 'Percentage'})
                    st.plotly_chart(fig)
                else:
                    st.error("❌ Pickup location or total amount columns not found in the dataset.")

            # Hourly Total Amount and Tips
            def hourly_total_and_tips():
                if 'tpep_pickup_datetime' in data.columns and 'total_amount' in data.columns and 'tip_amount' in data.columns:
                    data['hour'] = data['tpep_pickup_datetime'].dt.hour
                    hourly_totals = data.groupby('hour')[['total_amount', 'tip_amount']].sum().reset_index()
                    fig = px.line(hourly_totals, x='hour', y=['total_amount', 'tip_amount'], title="⏳ Hourly Total Amount and Tips")
                    st.plotly_chart(fig)
                else:
                    st.error("❌ Required columns not found in the dataset.")

            # Execute the selected analysis
            if analysis_option == "📊 Passenger Count Distribution":
                plot_distribution("passenger_count", "📊 Passenger Count Distribution")
            elif analysis_option == "💳 Payment Type Distribution":
                plot_distribution("payment_type", "💳 Payment Type Distribution")
            elif analysis_option == "💵 Fare Amount Distribution":
                plot_distribution("fare_amount", "💵 Fare Amount Distribution")
            elif analysis_option == "💰 Tip Amount Distribution":
                plot_distribution("tip_amount", "💰 Tip Amount Distribution")
            elif analysis_option == "💸 Total Amount Distribution":
                plot_distribution("total_amount", "💸 Total Amount Distribution")
            elif analysis_option == "⏰ Top 5 Busiest Hours":
                busiest_hours()
            elif analysis_option == "🏙️ Top 3 Boroughs":
                top_boroughs()
            elif analysis_option == "🚖 Top 5 Routes in Manhattan":
                top_routes()
            elif analysis_option == "🌍 Inter Borough Transition (Heatmap)":
                inter_borough_transition()
            elif analysis_option == "🗺️ Traffic Heatmap (Avg Rides Per Weekday Hour)":
                traffic_heatmap()
            elif analysis_option == "💰 Revenue Share by Pickup Zones (Percentage Bar Chart)":
                revenue_share_by_pickup_zones()
            elif analysis_option == "⏳ Hourly Total Amount and Tips":
                hourly_total_and_tips()

else:
    st.info("📂 Please upload a CSV file to proceed.")
