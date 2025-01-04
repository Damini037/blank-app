import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data with error handling
@st.cache_data
def load_data(file):
    try:
        # Use chunking for large files
        chunk_list = []
        chunksize = 50000
        # Attempt reading with a more tolerant encoding
        for chunk in pd.read_csv(file, encoding='latin1', chunksize=chunksize, on_bad_lines='skip'):
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
st.title("NYC Taxi Data Analysis")
st.write("Upload the NYC Taxi dataset to analyze passenger count, payment type, fares, and more.")

# File uploader with size check
file = st.file_uploader("Upload CSV File (Max size: 100 KB)", type=["csv"])

if file is not None:
    if file.size > 100 * 1024:  # Convert 100 KB to bytes
        st.error("File size exceeds 100 KB. Please upload a smaller file.")
    else:
        data = load_data(file)

        if data is None or data.empty:
            st.error("No data available for analysis. Please check the dataset.")
        else:
            st.success("Data loaded successfully!")

            # Sidebar for analysis options
            st.sidebar.title("Choose an Analysis")
            analysis_option = st.sidebar.selectbox("Analysis Type", [
                "Passenger Count Distribution",
                "Payment Type Distribution",
                "Fare Amount Distribution",
                "Tip Amount Distribution",
                "Total Amount Distribution",
                "Busiest Hours",
            ])

            # Function to plot distribution
            def plot_distribution(column, title):
                if column not in data.columns:
                    st.error(f"Column '{column}' not found in the data.")
                    return
                # Ensure the column is numeric
                data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
                # Plot the distribution
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
                    ax.set_title("Busiest Hours (Pickup Times)")
                    ax.set_xlabel("Hour of the Day")
                    ax.set_ylabel("Number of Pickups")
                    st.pyplot(fig)
                else:
                    st.error("Datetime column not found in the dataset.")

            # Execute analysis based on user selection
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
                busiest_hours()

else:
    st.info("Please upload a CSV file to proceed.")

# Footer
st.write("Developed with ❤️ using Streamlit.")
