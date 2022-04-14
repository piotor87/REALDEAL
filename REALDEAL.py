

import pandas as pd
import io
import requests


starting_real_deal = {"player":"Carlos Alcaraz",'date':20220101 }
url="https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv"
columns=["tourney_date","tourney_name","winner_name","winner_age",'loser_name','loser_age','round','score']

def return_data():

    s=requests.get(url).content
    c=pd.read_csv(io.StringIO(s.decode('utf-8')),index_col=None,usecols=columns)
    return c

def return_losses(df,current_real_deal=starting_real_deal):

    rd_df = filter_df(df,starting_real_deal["player"],starting_real_deal["date"])
    real_deal =[]
    while not rd_df.empty:
        #get loss with lowest age (can only be one)
        loss = rd_df.loc[rd_df['tourney_date'].idxmin()]
        real_deal.append(loss.to_dict())
        rd_df = filter_df(df,loss.winner_name,loss.tourney_date)
        
    return real_deal

def filter_df(df,name,date):
    print(f"filtering earliest loss of {name} after date {date}")
    return df[(df.loser_name == name) & (df.tourney_date > date)]
