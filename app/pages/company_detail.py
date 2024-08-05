import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
from utils.visualiazations import create_bar_chart, create_pie_chart, create_histogram, create_line_chart
from utils.data_loader import get_company_details

def calculate_probability(data, low, high):
    mean = np.mean(data)
    std = np.std(data)
    z_low = (low - mean) / std
    z_high = (high - mean) / std
    probability = stats.norm.cdf(z_high) - stats.norm.cdf(z_low)
    return probability

def show(companies_df, financial_df, projects_df, company_id):
    # Add a "Back to Search" button
    if st.button("Back to Search"):
        st.session_state.page = 'search'
        st.rerun()

    company_data = get_company_details(companies_df, company_id)
    st.title(f'Company Details: {company_data["company_name_thai"]}')

    # Company Information
    st.subheader('Company Information')
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Registered No:** {company_data['registered_no']}")
        st.write(f"**Thai Name:** {company_data['company_name_thai']}")
        st.write(f"**English Name:** {company_data['company_name_english']}")
        st.write(f"**Registration Date:** {company_data['registered_date'].strftime('%Y-%m-%d')}")
    with col2:
        st.write(f"**Status:** {company_data['status']}")
        st.write(f"**Registered Type:** {company_data['registered_type']}")
        st.write(f"**Registered Capital:** ฿{company_data['registered_capital']:,.2f}")
        st.write(f"**Company Value:** ฿{company_data['company_value']:,.2f}")

    # Calculate and display company value as percentage of registered capital
    if company_data['registered_capital'] > 0:
        value_percentage = (company_data['company_value'] / company_data['registered_capital']) * 100
        st.write(f"**Company Value (% of Registered Capital):** {value_percentage:.2f}%")

    # Display address
    st.subheader('Company Address')
    st.write(company_data['address'])

    # Financial Performance
    st.subheader('Financial Performance (Thailand)')
    
    # Filter financial data for this company and Thailand
    company_financials = financial_df[(financial_df['registered_no'] == company_id) & (financial_df['category_id'] == 1)]  # Assuming category_id 1 is for Thailand
    
    if not company_financials.empty:
        # Create a line chart for Revenue and Profit/Loss over the years
        fig = create_line_chart(company_financials, x='year', y=['revenue', 'profit_loss'], 
                                title='Annual Revenue and Profit/Loss')
        st.plotly_chart(fig)

        # Display a table with detailed financial information
        st.write('Detailed Financial Information')
        st.dataframe(company_financials[['year', 'revenue', 'profit_loss', 'tax_expense', 'asset']])
    else:
        st.write("No financial data available for this company.")

    # Project Information
    company_projects = projects_df[projects_df['winner_tin'] == company_id].copy()
    
    if not company_projects.empty:
        # Calculate metrics
        total_projects = len(company_projects)
        total_value = company_projects['project_money'].sum()
        median_value = company_projects['project_money'].median()
        avg_value = company_projects['project_money'].mean()
        
        # Display key project metrics
        st.subheader('Project Metrics')
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Projects", f"{total_projects:,}")
        col2.metric("Total Project Value", f"฿{total_value:,.2f}")
        col3.metric("Avg Project Value", f"฿{avg_value:,.2f}")
        col4.metric("Median Project Value", f"฿{median_value:,.2f}")

        # Create two columns for charts
        left_column, right_column = st.columns(2)

        with left_column:
            # Project budget distribution
            st.subheader('Project Budget Distribution')
            fig_budget = create_histogram(company_projects, 'project_money', 'Project Budget Distribution', nbins=30)
            st.plotly_chart(fig_budget, use_container_width=True)

            # Province distribution
            st.subheader('Project Distribution by Province')
            province_distribution = company_projects['province'].value_counts()
            fig_province = create_pie_chart(province_distribution, names=province_distribution.index, values=province_distribution.values, title='Projects by Province')
            st.plotly_chart(fig_province, use_container_width=True)

        with right_column:
            # Project Type distribution
            st.subheader('Project Type Distribution')
            type_distribution = company_projects['project_type_name'].value_counts()
            fig_type = create_pie_chart(type_distribution, names=type_distribution.index, values=type_distribution.values, title='Projects by Type')
            st.plotly_chart(fig_type, use_container_width=True)

            # Department distribution
            st.subheader('Project Distribution by Department')
            dept_distribution = company_projects['dept_name'].value_counts()
            fig_dept = create_pie_chart(dept_distribution, names=dept_distribution.index, values=dept_distribution.values, title='Projects by Department')
            st.plotly_chart(fig_dept, use_container_width=True)

        # List of past projects won
        st.subheader('Top Projects Won (by value)')
        top_projects = company_projects.sort_values('project_money', ascending=False).head(10)
        top_projects['project_money'] = top_projects['project_money'].apply(lambda x: f"฿{x:,.2f}")
        st.dataframe(top_projects[[
            'project_name', 'project_money', 'dept_name', 'province', 
            'project_type_name', 'purchase_method_name'
        ]], height=400, use_container_width=True)

        # Probability Estimation Section
        st.markdown("---")
        st.header("Probability Estimation for Project Bidding")

        # Calculate overall stats for project budgets
        budget_mean = np.mean(company_projects['project_money'])
        budget_std = np.std(company_projects['project_money'])

        # Display overall stats
        st.write(f"**Mean project budget:** ฿{budget_mean:,.2f}")
        st.write(f"**Standard deviation of project budget:** ฿{budget_std:,.2f}")

        # Sliders for project budget range
        st.subheader("Select Project Budget Range")
        col1, col2 = st.columns(2)
        with col1:
            low_value = st.slider("Lower bound (in millions)", 
                                  min_value=0.0, 
                                  max_value=float(company_projects['project_money'].max()) / 1e6, 
                                  value=10.0, 
                                  step=0.1)
        with col2:
            high_value = st.slider("Upper bound (in millions)", 
                                   min_value=0.0, 
                                   max_value=float(company_projects['project_money'].max()) / 1e6, 
                                   value=20.0, 
                                   step=0.1)

        if st.button("Calculate Bidding Probability"):
            if low_value >= high_value:
                st.error("Error: Lower bound must be less than upper bound.")
            else:
                custom_prob = calculate_probability(company_projects['project_money'], low_value * 1e6, high_value * 1e6)
                st.success(f"Probability of bidding on a project valued between ฿{low_value:.1f}-{high_value:.1f} million: {custom_prob:.2%}")

                # Visualization of the probability
                fig = px.histogram(company_projects, x='project_money', nbins=50,
                                   title=f"Project Budget Distribution with Selected Range (฿{low_value:.1f}M - ฿{high_value:.1f}M)")
                fig.add_vline(x=low_value * 1e6, line_dash="dash", line_color="red")
                fig.add_vline(x=high_value * 1e6, line_dash="dash", line_color="red")
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No project data available for this company.")