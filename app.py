import streamlit as st
import plotly.figure_factory as ff
import pandas as pd
from datetime import datetime, timedelta

def load_data_from_csv():
    try:
        df = pd.read_csv("all_data.csv", index_col=0)
        df['Start'] = pd.to_datetime(df['Start'])
        df['Finish'] = pd.to_datetime(df['Finish'])
        return df
    except FileNotFoundError:
        st.warning("El archivo all_data.csv no existe.")
        return pd.DataFrame(columns=["Task", "Start", "Finish", "Resource"])

def save_data_to_csv(df):
    df.to_csv("all_data.csv")

def update_and_save_tasks():
    df = pd.DataFrame(st.session_state.tasks)
    save_data_to_csv(df)

df = load_data_from_csv()

if "tasks" not in st.session_state:
    st.session_state.tasks = df.to_dict(orient="records")

st.dataframe(df)

def create_gantt(df):
    colors = {'Not Started': 'rgb(220, 0, 0)',
              'Incomplete': 'rgb(255, 229, 41)',
              'Complete': 'rgb(0, 255, 100)'}

    fig = ff.create_gantt(df, colors=colors, index_col='Resource', show_colorbar=True,
                          group_tasks=True, showgrid_x=True, showgrid_y=True)

    fig.update_xaxes(type='date', tickformat="%d-%m-%Y %H:%M")

    st.plotly_chart(fig, use_container_width=True)

create_gantt(df)

with st.form("add_task"):
    task = st.text_input('Task')
    start_date = st.date_input('Start date')
    start_time = st.time_input('Start time')
    finish_date = st.date_input('Finish date')
    finish_time = st.time_input('Finish time')
    resource = st.selectbox('Resource', ['Not Started', 'Incomplete', 'Complete'])

    submitted = st.form_submit_button("Add Task")
    if submitted:
        if start_date and start_time and finish_date and finish_time:
            start_datetime = datetime.combine(start_date, start_time)
            finish_datetime = datetime.combine(finish_date, finish_time)
            new_task = {
                "Task": task,
                "Start": start_datetime,
                "Finish": finish_datetime,
                "Resource": resource
            }
            st.session_state.tasks.append(new_task)
            update_and_save_tasks()  
            st.experimental_rerun()
        else:
            st.error("Por favor, completa todas las fechas y horas.")

#eliminar o cambiar el estado de una tarea
def delete_or_update_task(task_index, new_resource=None):
    if new_resource:
        st.session_state.tasks[task_index]["Resource"] = new_resource
        update_and_save_tasks()  
    else:
        del st.session_state.tasks[task_index]
        update_and_save_tasks()  
    st.experimental_rerun()

st.subheader("Eliminar Tareas o Cambiar Estado")
for i, task in enumerate(st.session_state.tasks):
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 0.1, 0.1])
    col1.write(task['Task'])
    col2.write(task['Start'])
    col3.write(task['Finish'])
    current_resource = task['Resource']
    selectbox_key = f"selectbox_{i}"
    new_resource = col4.selectbox("Estado", ['Not Started', 'Incomplete', 'Complete'], index=['Not Started', 'Incomplete', 'Complete'].index(current_resource), key=selectbox_key)
    delete_button = col5.button("Eliminar", key=f"delete_{i}")
    if delete_button:
        delete_or_update_task(i)
    else:
        update_button = col6.button("Actualizar", key=f"update_{i}")
        if update_button and new_resource != current_resource:
            delete_or_update_task(i, new_resource)


