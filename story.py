import pandas as pd
import streamlit as st
from datetime import datetime

# Set page layout to wide
st.set_page_config(layout="wide")

def load_data(file_path):
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    
    # Ensure date columns are datetime objects and format them as DD-MM-YYYY
    data['Start Date'] = pd.to_datetime(data['Start Date'], errors='coerce').dt.strftime('%d-%m-%Y')
    data['End Date'] = pd.to_datetime(data['End Date'], errors='coerce').dt.strftime('%d-%m-%Y')
    data['Sprint Start'] = pd.to_datetime(data['Sprint Start'], errors='coerce').dt.strftime('%d-%m-%Y')
    data['Sprint End'] = pd.to_datetime(data['Sprint End'], errors='coerce').dt.strftime('%d-%m-%Y')

    # Strip any leading or trailing whitespaces from 'Status' and 'Spillover'
    data['Status'] = data['Status'].str.strip()
    data['SpillOver'] = data['SpillOver'].str.strip()

    # Calculate Spillover: only if both dates are valid strings
    def calculate_spillover(row):
        if pd.notnull(row['End Date']) and pd.notnull(row['Sprint End']):
            try:
                end_date = datetime.strptime(row['End Date'], '%d-%m-%Y')
                sprint_end = datetime.strptime(row['Sprint End'], '%d-%m-%Y')
                return 'Yes' if end_date > sprint_end else 'No'
            except ValueError:
                return 'No'  # In case of invalid date formats
        return 'No'  # Default for missing dates
    
    data['SpillOver'] = data.apply(calculate_spillover, axis=1)

    # Handle the case where 'Comments' may not exist
    data['Comments'] = data.get('Comments', '')
    
    return data

# Function to save the data
def save_data(data, file_path):
    # Convert date columns back to datetime format before saving
    data['Start Date'] = pd.to_datetime(data['Start Date'], format='%d-%m-%Y', errors='coerce')
    data['End Date'] = pd.to_datetime(data['End Date'], format='%d-%m-%Y', errors='coerce')
    data['Sprint Start'] = pd.to_datetime(data['Sprint Start'], format='%d-%m-%Y', errors='coerce')
    data['Sprint End'] = pd.to_datetime(data['Sprint End'], format='%d-%m-%Y', errors='coerce')
    data.to_excel(file_path, index=False)

# Load the data
file_path = 'Story Tracker.xlsx'
data = load_data(file_path)

# Create tabs
tab1, tab2 = st.tabs(["Current Data", "OTD"])

# Sidebar: Add/Edit User Story form
st.sidebar.subheader('Add/Edit User Story')
with st.sidebar.form(key='edit_form'):
    entity_type = st.text_input('Entity Type')
    user_story_id = st.text_input('ID')
    user_story_name = st.text_input('Name')
    effort = st.number_input('Effort', min_value=0)
    team = st.text_input('Team')
    sprint = st.text_input('Sprint')
    sprint_start = st.date_input('Sprint Start')
    sprint_end = st.date_input('Sprint End')
    status = st.selectbox('Status', ['Not Started', 'In Progress', 'Done'])
    start_date = st.date_input('Start Date')
    end_date = st.date_input('End Date')
    sprint_goal = st.text_area('Sprint Goal')
    comments = st.text_area('Comments')
    submit_button = st.form_submit_button(label='Add/Edit User Story')

    if submit_button:
        new_data = {
            'Entity Type': entity_type,
            'ID': user_story_id,
            'Name': user_story_name,
            'Effort': effort,
            'Team': team,
            'Sprint': sprint,
            'Sprint Start': sprint_start.strftime('%d-%m-%Y'),
            'Sprint End': sprint_end.strftime('%d-%m-%Y'),
            'Status': status,
            'Start Date': start_date.strftime('%d-%m-%Y'),
            'End Date': end_date.strftime('%d-%m-%Y'),
            'SpillOver': 'Yes' if end_date > sprint_end else 'No',
            'Sprint Goal': sprint_goal,
            'Comments': comments
        }
        data = data.append(new_data, ignore_index=True)
        save_data(data, file_path)
        st.sidebar.success('User Story added/edited successfully!')

# Tab 1: Display the data and make it editable
with tab1:
    st.subheader('Current Data')
    edited_data = st.data_editor(data, num_rows="dynamic")
    if st.button("Save Changes"):
        save_data(edited_data, file_path)
        st.success('Data saved successfully!')

# Tab 2: OTD (On-Time Delivery) statistics
with tab2:
    st.subheader('OTD')

    # Calculate overall OTD statistics (before filtering by sprint)
    total_tasks_all = len(data)
    done_tasks_all = len(data[data['Status'] == 'Done'])
    on_time_tasks_all = len(data[(data['Status'] == 'Done') & (data['SpillOver'] == 'No')])

    if total_tasks_all > 0:
        avg_otd_percentage = (on_time_tasks_all / total_tasks_all) * 100
    else:
        avg_otd_percentage = 0

    # Display the average OTD percentage above the sprint selection
    st.markdown(f"### Average OTD % till now: {avg_otd_percentage:.2f}%")

    # Filter by Sprint
    sprint_filter = st.selectbox('Select Sprint', options=list(data['Team Sprint'].unique()))
    filtered_data = data[data['Team Sprint'] == sprint_filter]

    # Display the filtered data for debugging purposes
    st.write("Filtered Data", filtered_data)

    # Calculate statistics for the filtered sprint
    total_efforts = filtered_data['Effort'].sum()
    total_user_stories = filtered_data['Name'].nunique()
    total_tasks = len(filtered_data)

    # Strip whitespaces from 'Status' just in case
    filtered_data['Status'] = filtered_data['Status'].str.strip()

    # Calculate done tasks, on-time tasks, and delayed tasks
    done_tasks = len(filtered_data[filtered_data['Status'] == 'Done'])
    on_time_tasks = len(filtered_data[(filtered_data['Status'] == 'Done') & (filtered_data['SpillOver'] == 'No')])
    delayed_tasks = len(filtered_data[filtered_data['SpillOver'] == 'Yes'])

    if total_tasks > 0:
        otd_percentage = (done_tasks / total_tasks) * 100
    else:
        otd_percentage = 0

    # Display statistics for the selected sprint
    st.markdown(f"### Sprint: {sprint_filter}")
    st.markdown(f"**Total Efforts**: {total_efforts}")
    st.markdown(f"**Total User Stories**: {total_user_stories}")
    st.markdown(f"**Total Tasks**: {total_tasks}")
    st.markdown(f"**Done Tasks**: {done_tasks}")
    st.markdown(f"**On-Time Tasks**: {on_time_tasks}")
    st.markdown(f"**Delayed Tasks**: {delayed_tasks}")
    st.markdown(f"**OTD %**: {otd_percentage:.2f}%")