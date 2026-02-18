import streamlit as st
from src.st_utils import get_prop_list,get_planarea_list, get_filtered_table, get_stats, get_chart_pricediff, get_chart_anngrowth, get_performers
import pandas as pd

def main():
    
    st.set_page_config(
        page_title="Property Finder",
        page_icon="🏙",
        layout="wide"
    )

    st.title("Through The Looking Glass: Singapore's Property Landscape")
    
    def read_data(csv_file="streamlit_cloud_demo/data/realis_processed.csv"):
        df = pd.read_csv(csv_file)
        return df

    df_realis = read_data()

    prop_list = get_prop_list(df_realis)
    prop_list.insert(0,"All")

    planarea_list = get_planarea_list(df_realis)
    
    form = st.sidebar.form("form", clear_on_submit=True)
    with form:
    
        st.subheader("What type of Property Transactions do you want to see?")

        propname = st.selectbox(
        label='Select Property Project',
        options=prop_list,
        help = "If searching for a specific property, do not select Property Type or Planning Area!"
        )

        property_type = st.selectbox(
            label = "Select Property Type",
            options=('All','Condominium', 'Executive Condominium')
            )

        planarea = st.multiselect(
        label='Select Planning Area',
        options=planarea_list,
        help = "Optional; Multiple Areas can be selected"
        )

        prop_size_min = st.number_input(
            label = "Select Property Size (SQFT)",
            min_value = 100,
            max_value = 8000,
            value=200,
            step=100
        )

        prop_size_max = st.number_input(
            label = "to",
            min_value = 100,
            max_value = 8000,
            value=2000,
            step=100
        )

        min_year = st.selectbox(
            label = "Properties Purchased from Year",
            options=['All']+[str(n) for n in range(2000,2016)],
            help = "See only properties purchased after a certain year; this date can be either the date of OTP granted, or execution of the S&P agreement"
            )

        submit = st.form_submit_button("See Results")

    if submit==False:
        st.warning("_Note: This site is still undergoing development. We are accepting suggestions for additional data display elements - contact whoever sent you this URL._")
        st.image('streamlit_cloud_demo/data/hk2019r.jpg')
        st.caption("Image Credits: J.Lim 2019")
        st.info("Select parameters on the left to get started, or simply click **See Results**!")

    if submit == True:
        
        planarea = (','.join(str(s) for s in planarea) if planarea!=[] else 'All')

        st.info("**You've Selected:**")
        
        select_col1, select_col2, select_col3, select_col4, select_col5 = st.columns(5)

        with select_col1:
            st.write("**Property Name**")
            st.subheader(propname)
        with select_col2:
            st.write("**Property Type**")
            st.subheader(property_type)
        with select_col3:
            st.write("**Planning Area**")
            st.subheader(planarea)
        with select_col4:
            st.write("**Property Size**")
            st.subheader(str(prop_size_min) + "sqft to " + str(prop_size_max)+"sqft")
        with select_col5:
            st.write("**Year of Purchase From**")
            st.subheader(min_year)
        
        with st.spinner('Retrieving relevant transactions...'):
            df = get_filtered_table(propname,property_type,planarea,prop_size_min,prop_size_max,min_year,df_realis)
            stats = get_stats(df)
        
        count_transactions = stats['Price Differential (%)']['count']
        
        if count_transactions > 0:
            
            st.success("**Here's how your selection performed:**")
            st.subheader("Out of " + str("{:,}".format(int(count_transactions))) + " transactions")

            result_avg_col1, result_avg_col2, result_avg_col3 = st.columns(3)

            with result_avg_col1:
                st.metric(
                label="Average Profit/Loss",
                value = str(round(100*(stats['Price Differential (%)']['mean']),1)) + "%"
                )
            with result_avg_col2:
                st.metric(
                label="Average Annualized Gain/Loss",
                value = str(round(100*(stats['Annualized Growth']['mean']),1)) + "%"
                )
            
            with result_avg_col3:
                st.metric(
                label="Average Years Property Held",
                value = str(round(stats['Property Age (Years)']['mean'],1)) + "yrs"
                )
            
            result_med_col1, result_med_col2, result_med_col3 = st.columns(3)

            with result_med_col1:
                st.metric(
                label="Median Profit/Loss",
                value = str(round(100*(stats['Price Differential (%)']['50%']),1)) + "%"
                )
             
            with result_med_col2:
                st.metric(
                label="Median Annualized Gain/Loss",
                value = str(round(100*(stats['Annualized Growth']['50%']),1)) + "%"
                    )

            with result_med_col3:
                st.metric(
                label="Median Years Property Held",
                value = str(round(stats['Property Age (Years)']['50%'],1)) + "yrs"
                    )


            with st.spinner('Generating charts...'):

                chart1= get_chart_pricediff(df)

                chart2= get_chart_anngrowth(df)

                st.image([chart1,chart2],width=600)

            df_top = get_performers(df)
            df_top = df_top.head(10).fillna(0)
            
            with st.expander("Expand to view Top Performers for your selection (by Median Annualized Gain)"):
                st.dataframe(df_top, height = 350)
            
            df_bottom = get_performers(df)
            df_bottom = df_bottom.tail(10).fillna(0)
            df_bottom = df_bottom.sort_values(by=['Median Annualized Growth (%)'],ascending=True).to_dict()
                        
            with st.expander("Expand to view Bottom Performers for your selection (by Median Annualized Gain)"):
                st.dataframe(df_bottom, height = 350)
            
        else:
            st.warning("No transactions found matching your selections.")
    
if __name__ == "__main__":
    main()