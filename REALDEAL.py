import argparse,io,requests,os
import pandas as pd
from datetime import date
from markdownTable import markdownTable
round_order =["RR","R128","R64","R32",'R16','QF','SF','BR','F']
current_year = date.today().year

url="https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_YEAR.csv"
columns=["tourney_date","tourney_name","winner_name","winner_age",'loser_name','loser_age','round','score']
cols = [elem for elem in columns if "_age" not in elem]



def return_losses(df,real_deal,date):
    """
    Generator of the new iteration of RD. It searches for the most recent loss after a certain date.
    """
    # initalize values
    player,loss = return_earliest_loss_by_round(df,real_deal,date,round_order[0])
    while player:      
        res = {key:val for key,val in loss.to_dict().items() if key in cols}
        # now that we have a new RD, search for new losses and update conditions
        date,t_round = loss.tourney_date,loss["round"]
        player,loss = return_earliest_loss_by_round(df,player,date,t_round)


        yield res


def return_earliest_loss_by_round(df,old_player,old_date,old_round):
    """
    Returns oldest loss and, if date of loss is same as previous loss, makes sure new loss is in a later round.
    """

    # data frame with all losses >= old_date by old_player
    loss_df = filter_loss(df,old_player,old_date)
    
    # exit if no hits
    if loss_df.empty:
        return False,False

    # candidate loss!
    loss = loss_df.loc[loss_df['tourney_date'].idxmin()]
    
    # what if new loss is on same date?
    if loss.tourney_date == old_date:
        # check in the loss dataframe for all losses on that day and 
        round_df = loss_df[(loss_df.tourney_date == old_date) & (loss_df["round"] > old_round)]
        # if there are no later round losses it means we're stuck in some sort of loop, so we need to break it and rerun the function with original player but from the next day
        if round_df.empty:
            player,loss = return_earliest_loss_by_round(loss_df,old_player,old_date +1,round_order[0])            
        #otherwise grab that loss as the new loss!
        else:
            loss = round_df.loc[round_df['round'].idxmin()]

    return loss.winner_name,loss


#############################################################################################
#--------------------------------------- UTILS ---------------------------------------------#
#############################################################################################


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
        df = pd.concat([df, c], ignore_index=True)

    # assign order to rounds
    df["round"] = pd.Categorical(df['round'], round_order,ordered=True)
    tmp_date = str(max(df.tourney_date))
    last_date = f"{tmp_date[6:]}-{tmp_date[4:6]}-{tmp_date[:4]}"
    return df,last_date

    
def filter_loss(df,name,date):
    """
    Returns all losses of a player after a certain date.
    """
    return df[(df.loser_name == name) & (df.tourney_date >= date) ]

def fix_date(res):
    """
    Need to fix date in order to write it down in markdown
    """
    date = str(res["tourney_date"])
    res["tourney_date"] = f"{date[6:]}-{date[4:6]}-{date[:4]}"
    return res


def main(args):

    # read in data
    data,last_date = return_data(args.date)
    res = []   
    for entry in return_losses(data,args.real_deal,args.date):
        res.append(fix_date(entry))
        
    df = pd.DataFrame.from_dict(res)
    
    if not df.empty:
        print(df)
        with open(os.path.join(os.getcwd(),"REALDEAL.template")) as i: readme = i.read()
        readme = readme.replace("REAL_DEAL",entry["winner_name"])
        table = df.to_markdown(index=False)
        readme = readme.replace("TABLE",table)
        readme = readme.replace("LAST_DATE",last_date)
        with open(os.path.join(os.getcwd(),"README.md"),'wt') as o:o.write(readme + '\n')
    else:
          print("NO CHANGES IN THE REAL DEAL!")
          print(f"{args.real_deal} still holds the crown!")


        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description ="REAL DEAL.")
    parser.add_argument('--real_deal','--rd',type = str,help ='Name of original REAL DEAL ',default = "Carlos Alcaraz")
    parser.add_argument('--date',type = int,help ='YYYYMMDD',default = 20220401)

    args = parser.parse_args()
    main(args)
