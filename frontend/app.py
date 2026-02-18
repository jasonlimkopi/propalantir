import requests
import streamlit as st

backend = "http://127.0.0.1:8000"

def main():
    
    st.set_page_config(
        page_title="Property Finder",
        page_icon="🏡",
        layout="wide"
    )

    st.title("Through The Looking Glass: Singapore's Property Landscape")
    
    prop_list = requests.get(backend + '/propnames').json()
    planarea_list = requests.get(backend + '/planningareas').json()
    
    form = st.sidebar.form("form", clear_on_submit=True)
    with form:
    
        st.subheader("What type of Property Transactions do you want to see?")

        propname = st.selectbox(
        label='Select Property Project',
        options=prop_list["proplists"],
        help = "If searching for a specific property, do not select Property Type or Planning Area!"
        )

        property_type = st.selectbox(
            label = "Select Property Type",
            options=('All','Condominium', 'Executive Condominium')
            )

        planarea = st.multiselect(
        label='Select Planning Area',
        options=planarea_list["planlists"],
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
        st.image('data/hk2019r.jpg')
        st.caption("Image Credits: Jason Lim 2019")
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
            stats = requests.get(
                backend + '/stats', 
                params={"propname": propname,"proptype": property_type,"planarea": planarea,"propsize_min": prop_size_min,"propsize_max": prop_size_max,"newsaleyear": min_year}).json()

        count_transactions = stats['stat_dict']['Price Differential (%)']['count']
        
        if count_transactions > 0:
            
            st.success("**Here's how your selection performed:**")
            st.subheader("Out of " + str("{:,}".format(int(count_transactions))) + " transactions")

            result_avg_col1, result_avg_col2, result_avg_col3 = st.columns(3)

            with result_avg_col1:
                st.metric(
                label="Average Profit/Loss",
                value = str(round(100*(stats['stat_dict']['Price Differential (%)']['mean']),1)) + "%"
                )
            with result_avg_col2:
                st.metric(
                label="Average Annualized Gain/Loss",
                value = str(round(100*(stats['stat_dict']['Annualized Growth']['mean']),1)) + "%"
                )
            
            with result_avg_col3:
                st.metric(
                label="Average Years Property Held",
                value = str(round(stats['stat_dict']['Property Age (Years)']['mean'],1)) + "yrs"
                )
            
            result_med_col1, result_med_col2, result_med_col3 = st.columns(3)

            with result_med_col1:
                st.metric(
                label="Median Profit/Loss",
                value = str(round(100*(stats['stat_dict']['Price Differential (%)']['50%']),1)) + "%"
                )
             
            with result_med_col2:
                st.metric(
                label="Median Annualized Gain/Loss",
                value = str(round(100*(stats['stat_dict']['Annualized Growth']['50%']),1)) + "%"
                    )

            with result_med_col3:
                st.metric(
                label="Median Years Property Held",
                value = str(round(stats['stat_dict']['Property Age (Years)']['50%'],1)) + "yrs"
                    )


            with st.spinner('Generating charts...'):

                chart1= requests.get(
                        backend + '/chartprice',
                        params={"propname": propname,"proptype": property_type,"planarea": planarea,"propsize_min": prop_size_min,"propsize_max": prop_size_max,"newsaleyear": min_year}
                        ).content

                chart2= requests.get(
                        backend + '/chartgrowth',
                        params={"propname": propname,"proptype": property_type,"planarea": planarea,"propsize_min": prop_size_min,"propsize_max": prop_size_max,"newsaleyear": min_year}
                        ).content

                st.image([chart1,chart2],width=600)

            df_top = requests.get(
                backend + '/performerstop', 
                params={"propname": propname,"proptype": property_type,"planarea": planarea,"propsize_min": prop_size_min,"propsize_max": prop_size_max,"newsaleyear": min_year}).json()
            
            with st.expander("Expand to view Top Performers for your selection (by Median Annualized Gain)"):
                st.dataframe(df_top['top_dict'], height = 350)
            
            df_bottom = requests.get(
                backend + '/performersbottom', 
                params={"propname": propname,"proptype": property_type,"planarea": planarea,"propsize_min": prop_size_min,"propsize_max": prop_size_max,"newsaleyear": min_year}).json()
            
            with st.expander("Expand to view Bottom Performers for your selection (by Median Annualized Gain)"):
                st.dataframe(df_bottom['bottom_dict'], height = 350)
            
        else:
            st.warning("No transactions found.")
    
if __name__ == "__main__":
    main()