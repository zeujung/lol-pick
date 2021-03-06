import cassiopeia as cass
import getpass
import random
import pickle as pkl
import os
import pandas as pd
from cassiopeia.datastores.riotapi.common import APIRequestError, APIError
from datapipelines.pipelines import NotFoundError
import argparse

key = getpass.getpass("Enter Riot API key:")
cass.set_riot_api_key(key)  # This overrides the value set in your configuration/settings.
cass.set_default_region("KR")


def get_lane(participant):
    try:
        lane = participant.lane.name
        if lane =='bot_lane':
            lane = participant.role.name
        return lane
    except AttributeError:
        return 'No info'
    
def get_data(i):
    dd = [i]
    match = cass.get_match(i)
    try:
        version = match.version
        queue = match.queue.value
    except APIRequestError:
        print('Your API key has expired.')
        key = getpass.getpass("Enter new Riot API key:")
        cass.set_riot_api_key(key)
        try:
            version = match.version
            queue = match.queue.value
        except:
            return []
    except:
        return []
        
    if queue in ['RANKED_SOLO_5x5'] and version == '9.1.257.7563':        
        for participant in match.blue_team.participants :
            try:
                lane = get_lane(participant)
                champion = participant.champion.name
                rank = participant.summoner.ranks[match.queue]
                tier = ' '.join([rank.tier.name, rank.division.name])
            except APIRequestError:
                print('Your API key has expired.')
                key = getpass.getpass("Enter new Riot API key:")
                cass.set_riot_api_key(key)
                lane = get_lane(participant)
                champion = participant.champion.name
                rank = participant.summoner.ranks[match.queue]
                tier = ' '.join([rank.tier.name, rank.division.name])
            
            dd.append((lane, participant.champion.name, tier))
            
        for ban in match.blue_team.bans:
            try:
                dd.append(ban.name)
            except AttributeError:
                dd.append('No Ban')
                
        for participant in match.red_team.participants :
            try:
                lane = get_lane(participant)
                champion = participant.champion.name
                rank = participant.summoner.ranks[match.queue]
                tier = ' '.join([rank.tier.name, rank.division.name])
            except APIRequestError:
                print('Your API key has expired.')
                key = getpass.getpass("Enter new Riot API key:")
                cass.set_riot_api_key(key)
                lane = get_lane(participant)
                champion = participant.champion.name
                rank = participant.summoner.ranks[match.queue]
                tier = ' '.join([rank.tier.name, rank.division.name])
            
            dd.append((lane, participant.champion.name, tier))
            
        for ban in match.red_team.bans:
            try:
                dd.append(ban.name)
            except AttributeError:
                dd.append('No Ban')

        dd.append(match.blue_team.win)
        print('Match id {} is valid.'.format(i))
        
    return dd




def main(args):
    start_id = args.start
    end_id = args.end
    ids = range(start_id, end_id)

    dir_name = '{}-{}'.format(start_id, end_id)
    os.mkdir(os.path.join('../data/',dir_name))

    data = []
    k=0
    
    for i in ids:
        try:
            dd = get_data(i)
            if len(dd) > 1:
                data.append(dd)
            if len(data)==args.freq:
                print("Making {}.pkl.".format(k))
                with open(os.path.join('../data/', dir_name, '{}.pkl'.format(k)), 'wb') as f:
                    pkl.dump(data, f)
                k+=1
                data = []
        except:
            print('Error occured for {}'.format(i))
            continue

    if len(data)!=0:
        with open(os.path.join('../data/', dir_name, '{}.pkl'.format(k)), 'wb') as f:
            pkl.dump(data, f)
            
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Data Crawling for LoL winrate prediction.'
    )
    parser.add_argument('--start', required=True, help='start id', type=int)
    parser.add_argument('--end', required=True, help='end id', type=int)
    parser.add_argument('--freq', default=1000, help='size of pkl', type=int)
    
    args = parser.parse_args()
    
    main(args)
        
