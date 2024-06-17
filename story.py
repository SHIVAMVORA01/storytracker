import streamlit as st
import pandas as pd
import altair as alt
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


# Title of the Streamlit app
st.title('My User Story Tracker')

# Create tabs
tab1, tab2, tab3 = st.tabs(["Current Data", "Add/Edit User Story", "Gantt Chart"])

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

# Tab 3: Create Gantt chart with filters
with tab3:
    st.subheader('Gantt Chart')

    # Filter by Sprint
    sprint_filter = st.selectbox('Select Sprint', options=list(data['Sprint'].unique()))
    filtered_data = data[data['Sprint'] == sprint_filter]

    # Display sprint start and end dates once
    sprint_dates = filtered_data[['Sprint Start', 'Sprint End']].drop_duplicates().reset_index(drop=True)
    for idx, row in sprint_dates.iterrows():
        st.markdown(f"### Sprint Start: {row['Sprint Start'].strftime('%d-%m-%Y')} | Sprint End: {row['Sprint End'].strftime('%d-%m-%Y')}")

    # Create Gantt chart using Altair
    base = alt.Chart(filtered_data).encode(
        x=alt.X('Start Date:T', title='Start Date'),
        x2=alt.X2('End Date:T'),
        y=alt.Y('User Story:N', title='User Story'),
        color=alt.Color('Status:N', legend=alt.Legend(title="Status")),
        tooltip=['User Story', 'Start Date', 'End Date', 'Status']
    ).properties(
        width=800,
        height=400,
        title='User Stories Timeline'
    )

    gantt_chart = base.mark_bar().encode(
        y=alt.Y('User Story:N', sort=alt.EncodingSortField(field='Start Date', order='ascending'))
    )

    sprint_rects = alt.Chart(filtered_data).mark_rect(
        opacity=0.3,
        color='lightblue'
    ).encode(
        x=alt.X('Sprint Start:T', title='Sprint Start'),
        x2=alt.X2('Sprint End:T'),
        y=alt.Y('Sprint:N', title='Sprint')
    ).properties(
        width=800,
        height=400
    )

    combined_chart = sprint_rects + gantt_chart

    st.altair_chart(combined_chart, use_container_width=True)
