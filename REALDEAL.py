import argparse,io,requests,os
import pandas as pd
from datetime import date
from markdownTable import markdownTable

current_year = date.today().year

url="https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_YEAR.csv"
columns=["tourney_date","tourney_name","winner_name","winner_age",'loser_name','loser_age','round','score']
cols = [elem for elem in columns if "_age" not in elem]

def return_data(date):
    """
    Starting from the year of the selected date, the results are imported in a datafarme.
    """
    starting_year = int(str(date)[:4])
    years = range(starting_year,current_year+1)
    df = pd.DataFrame()
    for year in years:
        s=requests.get(url.replace("YEAR",str(year))).content
        c=pd.read_csv(io.StringIO(s.decode('utf-8')),index_col=None,usecols=columns)
        df = df.append(c,ignore_index = True)
    return df

def return_losses(df,real_deal,date):
    """
    Generator of the new iteration of RD. It searches for the most recent loss after a certain date.
    """
    rd_df = filter_df(df,real_deal,date)
    while not rd_df.empty:
        #get loss with lowest age (can only be one)
        loss = rd_df.loc[rd_df['tourney_date'].idxmin()]
        rd_df = filter_df(df,loss.winner_name,loss.tourney_date)
        res = {key:val for key,val in loss.to_dict().items() if key in cols}
        yield res



def fix_date(res):
    """
    Need to fix date in order to write it down in markdown
    """
    date = str(res["tourney_date"])
    y,m,d = date[:4],date[4:6],date[6:]
    res["tourney_date"] = f"{d}-{m}-{y}"
    return res



def filter_df(df,name,date):
    """
    Returns all losses of a player after a certain date.
    """
    return df[(df.loser_name == name) & (df.tourney_date > date)]


def main(args):

    # read in data
    data = return_data(args.date)

    
    res = []   
    for entry in return_losses(data,args.real_deal,args.date):
        res.append(fix_date(entry))
        
    df = pd.DataFrame.from_dict(res)
    print(df)
    
    with open(os.path.join(os.getcwd(),"REALDEAL.template")) as i: readme = i.read()
    readme = readme.replace("REAL_DEAL",entry["winner_name"])
    table = df.to_markdown(index=False)
    readme = readme.replace("TABLE",table)
    with open(os.path.join(os.getcwd(),"README.md"),'wt') as o:o.write(readme + '\n')
    


        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description ="Recursive conditional analysis for regenie.")
    parser.add_argument('--real_deal','--rd',type = str,help ='Name of original REAL DEAL ',default = "Carlos Alcaraz")
    parser.add_argument('--date',type = int,help ='YYYYMMDD',default = 20220401)

    args = parser.parse_args()
    main(args)
