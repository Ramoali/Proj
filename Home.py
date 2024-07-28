import streamlit as st
import pandas as pd
import plotly.express as px
from query import view_all_data
from streamlit_option_menu import option_menu
from numerize import numerize
import time
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objs as go

st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title="Dashboard", page_icon="🌍", layout="wide")
st.header("Tableau de bord analytique: Traitement, KPI, tendances et prévisions")

# Fetch data
result = view_all_data()

# Ensure that the DataFrame matches the number of columns you expect
columns = ["Date", "Production", "Cost", "Energy", "Nemploye", "Equipment", "Hours", "Sales", "Revenue", "Profit", "Quality", "Satisfaction","id"]
if len(result[0]) != len(columns):
    raise ValueError(f"Expected {len(columns)} columns but got {len(result[0])} columns in the data.")

df = pd.DataFrame(result, columns=columns)

# Sidebar
st.sidebar.image("data/logo.png", caption="Online Analytics")

# Filter options in the sidebar
region = st.sidebar.multiselect("SELECT QUALITY", options=df["Quality"].unique(), default=df["Quality"].unique())
location = st.sidebar.multiselect("SELECT Nemploye", options=df["Nemploye"].unique(), default=df["Nemploye"].unique())
construction = st.sidebar.multiselect("SELECT Equipment", options=df["Equipment"].unique(), default=df["Equipment"].unique())

# Apply filters
df_selection = df.query("Quality == @region & Nemploye == @location & Equipment == @construction")

def Home():
    with st.expander("VIEW EXCEL DATASET"):
        showData = st.multiselect(
            'Filter: ',
            df_selection.columns,
            default=columns
        )
        st.dataframe(df_selection[showData], use_container_width=True)

    # Compute top analytics
    total_production = float(df_selection['Production'].sum())
    production_mode = float(df_selection['Production'].mode()[0])
    production_mean = float(df_selection['Production'].mean())
    production_median = float(df_selection['Production'].median())
    quality = float(df_selection['Quality'].sum())

    total1, total2, total3, total4, total5 = st.columns(5, gap='small')
    with total1:
        st.info('Sum Production', icon="💰")
        st.metric(label="Sum", value=f"{total_production:,.0f}")

    with total2:
        st.info('Most Production', icon="💰")
        st.metric(label="Mode", value=f"{production_mode:,.0f}")

    with total3:
        st.info('Average Production', icon="💰")
        st.metric(label="Average", value=f"{production_mean:,.0f}")

    with total4:
        st.info('Central Production', icon="💰")
        st.metric(label="Median", value=f"{production_median:,.0f}")

    with total5:
        st.info('Quality', icon="💰")
        st.metric(label="Quality", value=numerize.numerize(quality), help=f"Total Quality: {quality}")
        style_metric_cards(
            background_color="#FFFFFF",
            border_left_color="#686664",
            border_color="#000000",
            box_shadow="#F71938"
        )

def graphs():
    total_production = df_selection["Production"].sum()
    average_quality = round(df_selection["Quality"].mean(), 2)

    # Bar graph: Production by Quality
    production_by_quality = (
        df_selection.groupby(by=["Quality"]).sum()[["Production"]].sort_values(by="Production")
    )
    fig_production = px.bar(
       production_by_quality,
       x="Production",
       y=production_by_quality.index,
       orientation="h",
       title="<b> PRODUCTION BY QUALITY </b>",
       color_discrete_sequence=["#0083B8"] * len(production_by_quality),
       template="plotly_white",
    )
    fig_production.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
    )

    # Line graph: Production by Satisfaction
    production_satisfaction = df_selection.groupby(by=["Satisfaction"]).sum()[["Production"]]
    fig_satisfaction = px.line(
       production_satisfaction,
       x=production_satisfaction.index,
       y="Production",
       title="<b> PRODUCTION BY SATISFACTION </b>",
       color_discrete_sequence=["#0083b8"] * len(production_satisfaction),
       template="plotly_white",
    )
    fig_satisfaction.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=False),
    )

    # Scatter Plot: Production vs. Cost
    fig_production_cost = px.scatter(
        df_selection, 
        x="Production", 
        y="Cost", 
        title="<b> PRODUCTION VS. COST </b>",
        color_discrete_sequence=["#0083B8"],
        template="plotly_white"
    )
    fig_production_cost.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )

    # Line Graph: Energy Consumption vs. Production
    fig_energy_production = px.line(
        df_selection, 
        x="Production", 
        y="Energy", 
        title="<b> ENERGY CONSUMPTION VS. PRODUCTION </b>",
        color_discrete_sequence=["#0083B8"],
        template="plotly_white"
    )
    fig_energy_production.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )

    left, right, center = st.columns(3)
    left.plotly_chart(fig_satisfaction, use_container_width=True)
    right.plotly_chart(fig_production, use_container_width=True)
    
    with center:
        # Pie chart: Quality by Satisfaction
        fig = px.pie(df_selection, values='Quality', names='Satisfaction', title='QUALITY BY SATISFACTION')
        fig.update_layout(legend_title="Satisfaction", legend_y=0.9)
        fig.update_traces(textinfo='percent+label', textposition='inside')

        st.plotly_chart(fig, use_container_width=True)
    
    st.plotly_chart(fig_production_cost, use_container_width=True)
    st.plotly_chart(fig_energy_production, use_container_width=True)
def Progressbar():
    st.markdown(
        """<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""",
        unsafe_allow_html=True
    )
    target = 3000000000
    current = df_selection["Production"].sum()
    percent = round((current / target * 100))
    mybar = st.progress(0)

    if percent > 100:
        st.subheader("Target achieved!")
    else:
        st.write("You have ", percent, "% of ", format(target, 'd'), " units of Production")
        for percent_complete in range(percent):
            time.sleep(0.1)
            mybar.progress(percent_complete + 1, text=" Target Percentage")

def sideBar():
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Progress"],
            icons=["house", "eye"],
            menu_icon="cast",
            default_index=0
        )
    if selected == "Home":
        st.subheader(f"Page: {selected}")
        Home()
        graphs()
    if selected == "Progress":
        st.subheader(f"Page: {selected}")
        Progressbar()
        graphs()

sideBar()

st.subheader('PICK FEATURES TO EXPLORE DISTRIBUTIONS TRENDS BY QUARTILES')
feature_x = st.selectbox('Select feature for x Qualitative data', df_selection.select_dtypes("object").columns)
feature_y = st.selectbox('Select feature for y Quantitative Data', df_selection.select_dtypes("number").columns)

fig2 = go.Figure(
    data=[go.Box(x=df_selection[feature_x], y=df_selection[feature_y])],
    layout=go.Layout(
        title=go.layout.Title(text="FEATURE BY QUARTILES"),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        font=dict(color='#cecdcd'),
    )
)
st.plotly_chart(fig2, use_container_width=True)

# Hide Streamlit style
hide_st_style = """
<style>
MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
