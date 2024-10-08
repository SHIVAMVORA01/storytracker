import streamlit as st
import pandas as pd
from datetime import datetime

# Set page layout to wide
st.set_page_config(layout="wide")

def load_data(file_path):
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    # Ensure date columns are datetime objects
    data['Start Date'] = pd.to_datetime(data['Start Date'], errors='coerce')
    data['End Date'] = pd.to_datetime(data['End Date'], errors='coerce')
    # Ensure 'User Story' is treated as a string
    data['User Story'] = data['User Story'].astype(str)
    # Calculate Spillover
    data['Spillover'] = data.apply(lambda row: 'Yes' if row['End Date'] > row['Sprint End'] else 'No', axis=1)
    data['Comments'] = data.get('Comments', '')
    return data

# Function to save the data
def save_data(data, file_path):
    data.to_excel(file_path, index=False)

# Load the data
file_path = 'Story Tracker.xlsx'
data = load_data(file_path)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Current Data", "Add/Edit User Story", "OTD"])

# Tab 1: Display the data and make it editable
with tab1:
    st.subheader('Current Data')
    edited_data = st.data_editor(data, num_rows="dynamic")
    if st.button("Save Changes"):
        save_data(edited_data, file_path)
        st.success('Data saved successfully!')

# Tab 2: Form to add/edit data
with tab2:
    st.subheader('Add/Edit User Story')
    with st.form(key='edit_form'):
        user_story = st.text_input('User Story')
        description = st.text_area('Description')
        sprint = st.text_input('Sprint')
        sprint_start = st.date_input('Sprint Start')
        sprint_end = st.date_input('Sprint End')
        status = st.selectbox('Status', ['Not Started', 'In Progress', 'Done'])
        start_date = st.date_input('Start Date')
        end_date = st.date_input('End Date')
        efforts = st.number_input('Efforts', min_value=0)
        comments = st.text_area('Comments')
        submit_button = st.form_submit_button(label='Add/Edit User Story')

        if submit_button:
            new_data = {
                'User Story': user_story,
                'Description': description,
                'Sprint': sprint,
                'Sprint Start': sprint_start,
                'Sprint End': sprint_end,
                'Status': status,
                'Start Date': start_date,
                'End Date': end_date,
                'Efforts': efforts,
                'Spillover': 'Yes' if end_date > sprint_end else 'No',
                'Comments': comments
            }
            data = data.append(new_data, ignore_index=True)
            save_data(data, file_path)
            st.success('User Story added/edited successfully!')

# Tab 3: OTD (On-Time Delivery) statistics
with tab3:
    st.subheader('OTD')

    # Filter by Sprint
    sprint_filter = st.selectbox('Select Sprint', options=list(data['Sprint'].unique()))
    filtered_data = data[data['Sprint'] == sprint_filter]

    # Calculate statistics
    total_efforts = filtered_data['Efforts'].sum()
    total_user_stories = filtered_data['User Story'].nunique()
    total_tasks = len(filtered_data)
    done_tasks = len(filtered_data[filtered_data['Status'] == 'Done'])
    on_time_tasks = len(filtered_data[(filtered_data['Status'] == 'Done') & (filtered_data['Spillover'] == 'No')])
    delayed_tasks = len(filtered_data[filtered_data['Spillover'] == 'Yes'])

    if total_tasks > 0:
        otd_percentage = (done_tasks / total_tasks) * 100
    else:
        otd_percentage = 0

    # Display statistics
    st.markdown(f"### Sprint: {sprint_filter}")
    st.markdown(f"**Total Efforts**: {total_efforts}")
    st.markdown(f"**Total User Stories**: {total_user_stories}")
    st.markdown(f"**Total Tasks**: {total_tasks}")
    st.markdown(f"**Done Tasks**: {done_tasks}")  
    st.markdown(f"**On-Time Tasks**: {on_time_tasks}")
    st.markdown(f"**Delayed Tasks**: {delayed_tasks}")
    st.markdown(f"**OTD %**: {otd_percentage:.2f}%")

