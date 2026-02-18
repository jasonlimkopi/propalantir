import pandas as pd
from utils import clean_table, match_newsale_resale, assign_mktsegment, convert_datetimes, add_metrics_cols

realis_data = 'backend/data/realis.csv'

df = pd.read_csv(realis_data)

df = clean_table(df)

df = match_newsale_resale(df)

df = assign_mktsegment(df)

df = convert_datetimes(df)

df = add_metrics_cols(df)

df = df[[
    'Project Name',
    'New Sale Price ($)',
    'New Sale Price (PSF)',
    'Area (SQFT)',
    'Address',
    'Property Type',
    'Tenure',
    'Postal District',
    'Planning Region',
    'Planning Area',
    'Resale Price ($)',
    'Resale Price (PSF)',
    'Market Segment',
    'New Sale Datetime',
    'Resale Datetime',
    'Property Age (Years)',
    'Price Differential (%)',
    'Annualized Growth'
]]

df.to_csv('backend/data/realis_processed.csv', index=False)