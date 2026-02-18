import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime
import re

'''
Server Functions
'''

def get_prop_list(csv_file="data/realis_processed.csv"):
     '''Reads from source data and outputs list of all Project names'''
     df = pd.read_csv(csv_file)
     prop_list = df['Project Name'].tolist()
     prop_list = sorted(list(set(prop_list)))

     return prop_list

def get_planarea_list(csv_file="data/realis_processed.csv"):
     '''Reads from source data and outputs list of all Planning Area names'''
     df = pd.read_csv(csv_file)
     planarea_list = df['Planning Area'].tolist()
     planarea_list = sorted(list(set(planarea_list)))

     return planarea_list

def get_filtered_table(propname,proptype,planarea,propsize_min,propsize_max,newsaleyear,csv_file="data/realis_processed.csv"):
    '''Filters the source table to user-selected parameters'''
    df = pd.read_csv(csv_file)
    
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
    '''Describe statistics of the filtered table e.g. count, mean, median gain/loss'''
    df.astype({'Price Differential (%)': 'float', 'Annualized Growth': 'float','Property Age (Years)':'float'})
    df_stats = df[['Price Differential (%)','Annualized Growth','Property Age (Years)']].describe()
    dict_stats = df_stats.fillna(0).to_dict()
    
    return dict_stats

def get_chart_pricediff(df):
    '''Generate PyPlot histogram of Price Differential column'''
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
    '''Generate PyPlot histogram of Annualized Growth column'''
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
    '''Aggregates filtered table to get (to be continued)'''
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

'''
Data Prep Functions
'''

def clean_table(df):
    df = df.replace(',','', regex=True)
    df = df.astype({'Transacted Price ($)': 'int64',
                    'Area (SQFT)': 'float64',
                    'Unit Price ($ PSF)': 'int64'
                    })

    df = df.loc[df['Type of Area']=='Strata']
    df= df.replace({'Property Type':{'Apartment' : 'Condominium'}})
    df['project_address']= df['Project Name']+df['Address']

    return df

def match_newsale_resale(df):
    #Create New Sale table
    df_newsale = df.loc[df['Type of Sale'] == 'New Sale']
    df_newsale = df_newsale.drop(columns=['Type of Sale'])
    df_newsale['project_address']= df_newsale['Project Name']+df_newsale['Address']

    #Create Resale Table
    df_resale = df.loc[df['Type of Sale'].isin(['Resale'])]
    df_resale = df_resale[["Transacted Price ($)", "Unit Price ($ PSF)", "Sale Date","project_address"]]

    df_combine = pd.merge(df_newsale, df_resale, how = "inner", on = 'project_address')
    df_combine = df_combine.drop(columns=['project_address'])

    df_combine.rename(columns={'Transacted Price ($)_x': 'New Sale Price ($)', 
                            'Unit Price ($ PSF)_x': 'New Sale Price (PSF)',
                            'Sale Date_x': 'New Sale Date',
                            'Transacted Price ($)_y': 'Resale Price ($)',
                            'Unit Price ($ PSF)_y': 'Resale Price (PSF)',
                            'Sale Date_y': 'Resale Date'
                            }, inplace=True)
    
    return df_combine

def assign_mktsegment(df):
    CCR = [9,10,11,1,2,6]
    RCR = [3,4,5,7,8,12,13,14,15,20]
    OCR = [16,17,18,19,21,22,23,24,25,26,27,28]

    def segment(x):
        if x in CCR:
            return 'CCR'
        elif x in RCR:
            return 'RCR'
        elif x in OCR:
            return 'OCR'
        else:
            return 'Null'

    df['Market Segment'] = df.apply(lambda row:
                                                        segment(row['Postal District'])
                                                        , axis = 1)

    return df

def convert_datetimes(df):
    df['New Sale Datetime'] = df['New Sale Date'].apply(lambda x: datetime.strptime(x,'%d/%m/%Y'))
    df['Resale Datetime'] = df['Resale Date'].apply(lambda x: datetime.strptime(x,'%d/%m/%Y'))
    df = df.drop(columns=['New Sale Date','Resale Date'])
    df = df.loc[df['New Sale Datetime'] < df['Resale Datetime']]

    return df

def add_metrics_cols(df):
    def year_convertor(x):
        y = round(int((x.split()[0]))/365,1)
        return y

    df['Property Age (Years)'] = df.apply(lambda row:
                                                        year_convertor(str(row['Resale Datetime'] - row['New Sale Datetime']))
                                                        , axis = 1)


    df['Price Differential (%)'] = df.apply(lambda row:
                                                        (row['Resale Price (PSF)'] - row['New Sale Price (PSF)'])/row['New Sale Price (PSF)']
                                                        , axis = 1)


    df['Annualized Growth'] = df.apply(lambda row:
                                                        ((1+row['Price Differential (%)'])**(1/row['Property Age (Years)']))-1
                                                        , axis = 1)
    
    return df            