import streamlit as st
import pandas as pd
import psutil
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
        total_swap = swap.total / (1024 ** 3)  # Convert to GB
        used_swap = swap.used / (1024 ** 3)
        used_swap_percent = swap.percent

        # Disk space details
        partitions = psutil.disk_partitions()
        total_disk = free_disk = used_disk_percent = None

        # Iterate over partitions to find suitable disk (e.g., root or primary partition)
        for partition in partitions:
            try:
                if partition.fstype:  # Only check partitions with a valid filesystem type
                    disk_usage = psutil.disk_usage(partition.mountpoint)
                    total_disk = disk_usage.total / (1024 ** 3)  # Convert to GB
                    free_disk = disk_usage.free / (1024 ** 3)  # Convert to GB
                    used_disk_percent = disk_usage.percent
                    break  # Exit after finding the first suitable partition
            except PermissionError:
                continue  # Skip partitions that can't be accessed

        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = f"{uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds // 60) % 60} minutes"

        # Ensure total_disk values are available, otherwise set default or N/A
        if total_disk is not None:
            system_info.append({
                "ServerName": hostname,
                "Physical Memory (GB)": round(total_memory, 2),
                "In Use Memory (GB)": round(used_memory, 2),
                "Memory Usage (%)": round(used_memory_percent, 2),
                "Pagefile (Swap) (GB)": round(total_swap, 2),
                "Swap Usage (%)": round(used_swap_percent, 2),
                "Total Virtual Memory (GB)": round(total_swap + total_memory, 2),
                "Allocated Virtual Memory (GB)": round(used_swap + used_memory, 2),
                "Allocation Percent (%)": round(((used_swap + used_memory) / (total_swap + total_memory) * 100), 2),
                "Total Disk Size (GB)": round(total_disk, 2),
                "Free Disk (GB)": round(free_disk, 2),
                "Disk Usage (%)": round(used_disk_percent, 2),
                "Uptime": uptime_str
            })
        else:
            st.warning("No suitable disk partition found. Disk information will be omitted.")
            system_info.append({
                "ServerName": hostname,
                "Physical Memory (GB)": round(total_memory, 2),
                "In Use Memory (GB)": round(used_memory, 2),
                "Memory Usage (%)": round(used_memory_percent, 2),
                "Pagefile (Swap) (GB)": round(total_swap, 2),
                "Swap Usage (%)": round(used_swap_percent, 2),
                "Total Virtual Memory (GB)": round(total_swap + total_memory, 2),
                "Allocated Virtual Memory (GB)": round(used_swap + used_memory, 2),
                "Allocation Percent (%)": round(((used_swap + used_memory) / (total_swap + total_memory) * 100), 2),
                "Total Disk Size (GB)": "N/A",
                "Free Disk (GB)": "N/A",
                "Disk Usage (%)": "N/A",
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
        "Physical Memory (GB)", 
        "In Use Memory (GB)", 
        "Memory Usage (%)", 
        "Pagefile (Swap) (GB)", 
        "Swap Usage (%)", 
        "Total Virtual Memory (GB)", 
        "Allocated Virtual Memory (GB)", 
        "Allocation Percent (%)", 
        "Total Disk Size (GB)", 
        "Free Disk (GB)", 
        "Disk Usage (%)", 
        "Uptime"
    ]
    
    # Display report
    st.header(f"System Report for {hostname}")
    st.dataframe(df)

    # Filter and display data where allocated memory is greater than 50%
    filtered_df = df[df["Allocation Percent (%)"] > 50]

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
