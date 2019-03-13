# audit_me.py
# Ronald L. Rivest
# September 26, 2018

"""
Code to simulate auditing of ME RCV contest.
"""

from consistent_sampler import sampler
import hashlib
import bptool
import rcv
import numpy as np
import time
import pandas as pd

hash_count = 0

def randint(a, b):
    """
    Return pseudorandom between a (inclusive) and b (exclusive)
    """

    global hash_count
    assert a<b
    hash_input = str(hash_count)
    x = hashlib.sha256(str(hash_input).encode('utf-8')).hexdigest()
    x = int(x, 16)
    x = a + x % (b-a)
    return x
    
def get_data():

    votes_dir = "../../maine-rcv-data/"
    votes_filename = votes_dir + 'me_votes.csv'
    L = rcv.read_ME_data(votes_filename, True)

    return L

def rcv_wrapper(unique_ballots, tally_list, vote_for_n):
    #TODO(zarap): move tiebreaker to main
    tie_breaker = [] 
    tally = {}
    for index, count in tally_list:
        tally[unique_ballots[index]] = count
    return rcv.rcv_winner(tally,tie_breaker, printing_wanted=False)



def get_candidates(tally):
    candidate_names = set()
    for names in tally.keys():
        for name in names:
            candidate_names.add(name)
    return list(candidate_names)

def get_ballot_list():
    votes_dir = "../../maine-rcv-data/"
    votes_filename = votes_dir + 'me_votes.csv'
    tally = rcv.read_ME_data(votes_filename, False)
    n = sum(tally.values())
    L = rcv.convert_tally_to_ballots(tally)
    return n,L

#TODO(zarap): refactor to make faster
def get_sub_sample_tally(sample_size,sample_order):
    sample = [L[sample_order[i]] for i in range(sample_size)]
    sample_tally = rcv.convert_ballots_to_tally(sample)
    return sample_tally

def audit(simulations = 1000):
    data = []
    n,L = get_ballot_list()
    vote_for_n = 1
    num_trials = 1000
    output_file = "audit_simulations_vs_2.csv" 
    print("simulations: %d n: %d " % (num_trials,n))
    #sample size
    for seed in range(1,simulations+1):
        sample_order = list(sampler(range(n), with_replacement=False,
                            output='id', seed=seed))
        for sample_size in range(100, 3001, 100):
            print("seed: %d"%seed)
            start = time.time()
            sample_tally = get_sub_sample_tally(sample_size,sample_order)
            tie_breaker = [] 
            real_names = get_candidates(sample_tally)
            unique_ballots = list(sample_tally.keys())
            time_delta = time.time() - start
            sample_tallies = [[ sample_tally[name]  for name  in unique_ballots ],]
            win_probs = bptool.compute_win_probs_rcv(sample_tallies,
                              [n], 
                              seed,
                              num_trials,
                              unique_ballots,
                              real_names,
                              vote_for_n, rcv_wrapper)
            win_probs_with_simulation_data = {real_names[i]: prob for i , prob in win_probs }
            win_probs_with_simulation_data['seed'] = seed
            win_probs_with_simulation_data['time_delta'] = time_delta
            win_probs_with_simulation_data['sample_size'] = sample_size
            data.append(win_probs_with_simulation_data)

        if  seed % 5 == 1:
            print("At seed %d from 1 to %d"%(seed,simulations+1))
            df = pd.DataFrame(data)
            df.to_csv(output_file)
    df = pd.DataFrame(data)
    df.to_csv(output_file)  

if __name__ == '__main__':
    audit()

# import cProfile
# cProfile.run('audit()')


    
