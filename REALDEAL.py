import argparse,io,requests,os
import pandas as pd
from tabulate import tabulate
from datetime import date

current_year = date.today().year

url="https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_YEAR.csv"
columns=["tourney_date","tourney_name","winner_name","winner_age",'loser_name','loser_age','round','score']
cols = [elem for elem in columns if "_age" not in elem]

def return_data(date):

    starting_year = int(str(date)[:4])
    years = range(starting_year,current_year+1)
    df = pd.DataFrame()
    for year in years:
        s=requests.get(url.replace("YEAR",str(year))).content
        c=pd.read_csv(io.StringIO(s.decode('utf-8')),index_col=None,usecols=columns)
        df = df.append(c,ignore_index = True)
    return df

def return_losses(df,real_deal,date):

    rd_df = filter_df(df,real_deal,date)
    while not rd_df.empty:
        #get loss with lowest age (can only be one)
        loss = rd_df.loc[rd_df['tourney_date'].idxmin()]
        rd_df = filter_df(df,loss.winner_name,loss.tourney_date)
        res = loss.to_dict()
        print('\t'.join([str(res[elem]) for elem in cols]))
        yield res


def filter_df(df,name,date):
    return df[(df.loser_name == name) & (df.tourney_date > date)]



def main(args):


    html = os.path.join(os.getcwd(),"REALDEAL.template.html")
    with open(html) as i: site = i.read()
    data = return_data(args.date)
    
    out_file = os.path.join(os.getcwd(),"REALDEAL.txt")
    table_data = [cols]

    real_deal = return_losses(data,args.real_deal,args.date)
    for entry in real_deal:
        table_data.append([str(entry[elem]) for elem  in cols ])
    table = tabulate(table_data, tablefmt='html')

    html = html.replace(".template","")
    with open(html,'wt') as o:
        o.write(site.replace("TABLE",table))

        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description ="Recursive conditional analysis for regenie.")
    parser.add_argument('--real_deal','--rd',type = str,help ='Name of original REAL DEAL ',default = "Carlos Alcaraz")
    parser.add_argument('--date',type = int,help ='YYYYMMDD',default = 20220401)

    args = parser.parse_args()
    main(args)
