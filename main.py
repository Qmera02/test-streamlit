import pandas as pd 
import streamlit as st
import altair as alt
from datetime import datetime

df1 = pd.read_csv('task_1504_recordValue.csv')
df2 = pd.read_csv('df_groupmembers.csv')


df1['createdAt'] = pd.to_datetime(df1['createdAt'])
df1['created_at (formatted: YYYY-MMM-DD)'] = pd.to_datetime(df1['created_at (formatted: YYYY-MMM-DD)'])


df1 = df1.sort_values(by=['user_id', 'group_id', 'type_value', 'createdAt'], ascending=True)


df_merge1 = pd.merge(df1[['user_id', 'type_value', 'rep_value', 'created_at (formatted: YYYY-MMM-DD)',
                          'score', 'title', 'instance', 'app_user_id', 'name']],
                     df2[['group_id', 'user_id']],
                     on='user_id', how='inner')

df_merge1 = df_merge1.pivot_table(index=['group_id', 'title', 'instance', 'created_at (formatted: YYYY-MMM-DD)',
                                          'user_id', 'app_user_id', 'name'],
                                   columns='type_value', values=['rep_value', 'score'], aggfunc='first', fill_value=0)
df_merge1.columns = [f"{col[0]}_{col[1]}" for col in df_merge1.columns]
df_merge1 = df_merge1.reset_index()


df_merge1 = df_merge1.rename(columns={'created_at (formatted: YYYY-MMM-DD)': 'Date'})
df_merge1.drop_duplicates(subset=['user_id', 'group_id', 'Date'], keep='first', inplace=True)


start_date = '2023-01-01'
end_date = '2024-12-31'
df_filtered = df_merge1[(df_merge1['Date'] >= start_date) & (df_merge1['Date'] <= end_date)]


df = df_filtered.drop_duplicates(subset=['title', 'Date', 'user_id'], keep='first')


column_mapping = {
    'group_id': 'group id',
    'title': 'group name',
    'instance': 'instance',
    'Date': 'date',
    'user_id': 'user_id',
    'app_user_id': 'app user id',
    'name': 'student name',
    'rep_value_PULL_UP': 'pull rep',
    'score_PULL_UP': 'pull score',
    'rep_value_PUSH_UP': 'push rep',
    'score_PUSH_UP': 'push score',
    'rep_value_RUN': 'run rep',
    'score_RUN': 'run score',
    'rep_value_SHUTTLE': 'shuttle rep',
    'score_SHUTTLE': 'shuttle score',
    'rep_value_SIT_UP': 'sit rep',
    'score_SIT_UP': 'sit score',
    'rep_value_SWIM': 'swim rep',
    'score_SWIM': 'swim score'
}


df = df.rename(columns=column_mapping)


df['score_a'] = df['run score']
df['score_b'] = df[['push score', 'sit score', 'shuttle score']].mean(axis=1)
df['score_b'] = df['score_b'].round(1)


df['final_score'] = df[['score_a', 'score_b']].mean(axis=1)

# ================WEB LAYOUT=====================

st.set_page_config(
    page_title="TASK STREAMLIT",
    page_icon="💢",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")
title_text = "MY DASHBOARD"


st.markdown(
    f"""
    <style>
        .title-text {{
            text-align: center;
        }}
    </style>
    <h1 class="title-text">{title_text}</h1>
    """,
    unsafe_allow_html=True
)


start =datetime(2023,1,1)
first_date = st.date_input('Start Date' ,value= start)
last_date = st.date_input('End Date ' , datetime.today() )

selected_columns = ['group name', 'student name', 'date', 'push score', 'shuttle score', 
                    'pull score', 'run score', 'sit score', 'swim score', 'final_score']

filtered_df = df[(df['date'] >= str(first_date)) & (df['date'] <= str(end_date))]
showColumn =  filtered_df[selected_columns]
st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)

st.write(showColumn)



avg_scores_per_group = df.groupby('group name')['final_score'].mean().reset_index().round(1)


chart = alt.Chart(avg_scores_per_group).mark_bar().encode(
    x=alt.X('group name', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('final_score', title='Average Final Score', scale=alt.Scale(domain=[0, 100])),
    color=alt.Color('group name',title='Group Name : '),
    tooltip=['group name', 'final_score']
).properties(
    width=600,
    height=400,
    title='Rata - rata per group'
)
st.markdown('<div style="height: 45px;"></div>', unsafe_allow_html=True)
options = st.multiselect(
    'Insert Group Name :  ',
    df['group name'].unique(),  
    placeholder = 'Masukan grup'
    )


filtered_chart = chart.transform_filter(
    alt.FieldOneOfPredicate(field='group name', oneOf=options)
)
st.altair_chart(filtered_chart, use_container_width=True)
