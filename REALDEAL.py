

import pandas as pd
import io
import requests


starting_real_deal = {"player":"Carlos Alcaraz",'age':18.8774811773}



def return_data():
    url="https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv"
    s=requests.get(url).content
    c=pd.read_csv(io.StringIO(s.decode('utf-8')),index_col=None)
    return c



def return_losses(df,current_real_deal=starting_real_deal):

    rd = df[df["loser_name"] ==starting_real_deal['player']]
    loss_age = rd.loser_age.max()
    if loss_age < current_real_deal['age']:
        print("REAL DEAL UNCHANGED")
    return rd
    



    
