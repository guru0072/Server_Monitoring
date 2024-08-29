import streamlit as st
import pandas as pd
import psutil
import socket
from datetime import datetime

# Set page title and layout
st.set_page_config(page_title="System Monitor Dashboard", page_icon="💻", layout="wide")

# Function to get system information based on hostname
def get_system_info(hostname):
    system_info = []
    
    try:
        # Physical memory details
        memory = psutil.virtual_memory()
        total_memory = memory.total / (1024 ** 3)  # Convert to GB
        used_memory = memory.used / (1024 ** 3)
        used_memory_percent = memory.percent

        # Swap memory (similar to virtual memory)
        swap = psutil.swap_memory()
        total_swap = swap.total / (1024 ** 3)
        used_swap = swap.used / (1024 ** 3)
        used_swap_percent = swap.percent

        # Disk space details
        partitions = psutil.disk_partitions()
        total_disk = free_disk = free_disk_percent = None  # Initialize variables
        
        for partition in partitions:
            if partition.mountpoint == "C:\\" or partition.device.startswith("/"):  # Adjusting for different OS
                disk_usage = psutil.disk_usage(partition.mountpoint)
                total_disk = disk_usage.total / (1024 ** 3)
                free_disk = disk_usage.free / (1024 ** 3)
                free_disk_percent = disk_usage.percent
                break  # Exit after finding the first suitable partition

        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days} days {uptime.seconds // 3600} hours {(uptime.seconds // 60) % 60} minutes"

        # Append system info if disk information is available
        if total_disk is not None:
            system_info.append({
                "ServerName": hostname,
                "Physical Memory(GB)": round(total_memory, 2),
                "INuse(GB)": round(used_memory, 2),
                "INuse(%)": round(used_memory_percent, 2),
                "Pagefile(GB)": round(total_swap, 2),
                "vsphy(%)": round(used_swap_percent, 2),
                "virtual_Total(%)": round(total_swap + total_memory, 2),
                "virtual_allocated(GB)": round(used_swap + used_memory, 2),
                "allocPercent": round((used_swap + used_memory) / (total_swap + total_memory) * 100, 2),
                "Total C Drive Size(GB)": round(total_disk, 2),
                "Free C Drive(%)": round(free_disk_percent, 2),
                "Uptime": uptime_str
            })
        else:
            st.warning("No suitable disk partition found. Disk information will be omitted.")
            system_info.append({
                "ServerName": hostname,
                "Physical Memory(GB)": round(total_memory, 2),
                "INuse(GB)": round(used_memory, 2),
                "INuse(%)": round(used_memory_percent, 2),
                "Pagefile(GB)": round(total_swap, 2),
                "vsphy(%)": round(used_swap_percent, 2),
                "virtual_Total(%)": round(total_swap + total_memory, 2),
                "virtual_allocated(GB)": round(used_swap + used_memory, 2),
                "allocPercent": round((used_swap + used_memory) / (total_swap + total_memory) * 100, 2),
                "Total C Drive Size(GB)": "N/A",
                "Free C Drive(%)": "N/A",
                "Uptime": uptime_str
            })
        
    except Exception as e:
        st.error(f"An error occurred while fetching the system information: {e}")
    
    return pd.DataFrame(system_info)

# Streamlit app layout
st.title("System Monitor Dashboard")

# Input for hostname
hostname = st.text_input("Enter the Hostname:", "")

# Display the report only if the hostname is provided
if hostname:
    df = get_system_info(hostname)
    
    # Rename columns
    df.columns = [
        "ServerName", 
        "Physical Memory(GB)", 
        "INuse(GB)", 
        "INuse(%)", 
        "Pagefile(GB)", 
        "vsphy(%)", 
        "virtual_Total(%)", 
        "virtual_allocated(GB)", 
        "allocPercent", 
        "Total C Drive Size(GB)", 
        "Free C Drive(%)", 
        "Uptime"
    ]
    
    # Display report
    st.header(f"System Report for {hostname}")
    st.dataframe(df)

    # Filter and display data where allocated memory is greater than 50%
    filtered_df = df[df["allocPercent"] > 50]

    st.header("Filtered Report (Memory Allocation > 50%)")
    st.dataframe(filtered_df)

    # Option to download report as CSV
    st.header("Download Report")
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Full Report as CSV",
        data=csv,
        file_name=f"system_report_{hostname}.csv",
        mime="text/csv",
    )
