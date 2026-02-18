import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime
import re

def get_prop_list(df):
     prop_list = df['Project Name'].tolist()
     prop_list = sorted(list(set(prop_list)))

     return prop_list

def get_planarea_list(df):
     planarea_list = df['Planning Area'].tolist()
     planarea_list = sorted(list(set(planarea_list)))

     return planarea_list

def get_filtered_table(propname,proptype,planarea,propsize_min,propsize_max,newsaleyear,df):
    
    if propname != "All":
        df = df.loc[(df['Project Name']==propname)]

    if proptype != "All":
        df = df.loc[(df['Property Type']==proptype)]
    
    if planarea != "All":
        df = df.loc[(df['Planning Area'].isin(planarea.split(",")))]

    if newsaleyear != "All":
        df['New Sale Datetime'] = pd.to_datetime(df['New Sale Datetime'])
        df = df.loc[(df['New Sale Datetime'].dt.year>=int(newsaleyear))]

    df['Area (SQFT)'].astype(int)
    df = df.loc[(df['Area (SQFT)'].between(int(propsize_min), int(propsize_max)))]
    
    return df

def get_stats(df):
    df.astype({'Price Differential (%)': 'float', 'Annualized Growth': 'float','Property Age (Years)':'float'})
    df_stats = df[['Price Differential (%)','Annualized Growth','Property Age (Years)']].describe()
    dict_stats = df_stats.fillna(0).to_dict()
    
    return dict_stats

def get_chart_pricediff(df):
    
    df = df[["Project Name", "Area (SQFT)","Postal District","Market Segment","Property Age (Years)","Price Differential (%)"]]
    df_visual = df.copy()
    df_visual['Price Differential (%)'] = df_visual['Price Differential (%)'].apply(lambda x: x*100)
    
    
    plt.hist(df_visual['Price Differential (%)'], color = '#b35900', edgecolor = 'black',
            bins = int(1/0.01))

    plt.title('Range of Capital Gains/Losses')
    plt.xlabel('Gain/Loss on Sale (%)')
    plt.ylabel('No. of Transactions')

    chart_pricediff = io.BytesIO()
    plt.savefig(chart_pricediff, format='png')
    plt.clf()
    chart_pricediff.seek(0)

    return chart_pricediff

def get_chart_anngrowth(df):
    
    df = df[["Project Name", "Area (SQFT)","Postal District","Market Segment","Property Age (Years)","Annualized Growth"]]
    df_visual = df.copy()
    df_visual['Annualized Growth'] = df_visual['Annualized Growth'].apply(lambda x: x*100)

    plt.hist(df_visual['Annualized Growth'], color = '#007399', edgecolor = 'black',
            bins = int(0.5/0.005), range=(df_visual['Annualized Growth'].min(), df_visual['Annualized Growth'].max() if df_visual['Annualized Growth'].max()<=100 else 100))

    plt.title('Range of Annualized Growth')
    plt.xlabel('Price Growth/Year (%)')
    plt.ylabel('No. of Transactions')

    chart_anngrowth = io.BytesIO()
    plt.savefig(chart_anngrowth, format='png')
    plt.clf()
    chart_anngrowth.seek(0)

    return chart_anngrowth

def get_performers(df):
    df = df.groupby(['Project Name','Property Type','Planning Area']).agg(
        {
        'Project Name':['count'],
        'Annualized Growth': ['median'],
        'Resale Price (PSF)':['median'],
        'Resale Datetime':['max']
        })

    df.columns = df.columns.map('_'.join)
    df = df.reset_index()
    df = df.rename(
        {'Project Name_count': 'No. of Resale Transactions',
        'Annualized Growth_median': 'Median Annualized Growth (%)',
        'Resale Price (PSF)_median': 'Median Resale Price',
        'Resale Datetime_max': 'Last Resale Transaction',
        }, axis=1)

    df["Median Annualized Growth (%)"] = df["Median Annualized Growth (%)"].apply(lambda x: round(x*100,1))
    df["Median Resale Price"] = df["Median Resale Price"].apply(lambda x: int(x))
    df["Last Resale Transaction"] = df["Last Resale Transaction"].apply(lambda x: re.search(r'\b\d{4}\b', x).group())
    df = df.sort_values(by=['Median Annualized Growth (%)'],ascending=False)
    df = df.set_index('Project Name')

    return df