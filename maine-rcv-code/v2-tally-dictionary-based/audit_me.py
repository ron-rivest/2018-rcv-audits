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
    tie_breaker = [] 
    tally = {}
    for index, count in tally_list:
        tally[unique_ballots[index]] = count
    return rcv.rcv_winner(tally,tie_breaker, printing_wanted=False)

def compute_win_probs_rcv(sample_tallies,
                      total_num_votes,
                      seed,
                      num_trials,
                      unique_ballots,
                      real_names,
                      vote_for_n):
    """

    Runs num_trials simulations of the Bayesian audit to estimate
    the probability that each candidate would win a full recount.

    In particular, we run a single iteration of a Bayesian audit
    (extend each county's sample to simulate all the votes in the
    county and calculate the overall winner across counties)
    num_trials times.

    Input Parameters:

    -sample_tallies is a list of lists. Each list represents the sample tally
    for a given county. So, sample_tallies[i] represents the tally for county
    i. Then, sample_tallies[i][j] represents the number of votes candidate
    j receives in county i.

    -total_num_votes is a list of integers representing the number of
    ballots that were cast in this election. Each integer represents the total
    number of votes cast in a given county. So, total_num_votes[i] represents
    the total votes for county i. The sum of all total_num_votes[i] is the
    total number of votes in the entire election.

    -seed is an integer or None. Assuming that it isn't None, we
    use it to seed the random state for the audit.

    -num_trials is an integer which represents how many simulations
    of the Bayesian audit we run, to estimate the win probabilities
    of the candidates.

    -unique_ballots is an ordered list of tuples with ranked ballots
         this corresponds to "candidate names" for a plurality election

    --real_names ordered list of strings with candidate names

    -vote_for_n is an integer, parsed from the command-line args. Its default
    value is 1, which means we only calculate a single winner for the election.
    For other values n, we simulate the unnsampled votes and define a win
    for candidate i as any time they are in the top n candidates in the final
    tally.

    Returns:

    -win_probs is a list of pairs (i, p) where p is the fractional
    representation of the number of trials that candidate i has won
    out of the num_trials simulations.
    """

    num_candidates = len(unique_ballots)
    win_count =  {name : 0 for name in real_names} 
    for i in range(num_trials):
        # We want a different seed per trial.
        # Adding i to seed caused correlations, as numpy apparently
        # adds one per trial, so we multiply i by 314...
        seed_i = seed + i*314159265
        winner = bptool.compute_winner(sample_tallies,
                                total_num_votes,
                                vote_for_n,
                                seed_i, unique_ballots, voting_method=rcv_wrapper)
        win_count[winner] = win_count[winner] + 1
    total_count = float(sum(win_count.values()))
    win_probs = {name : win_count[name]/total_count for name in win_count.keys()}
    return win_probs

def get_candidates(tally):
    candidate_names = set()
    for names in tally.keys():
        for name in names:
            candidate_names.add(name)
    return list(candidate_names)
def audit():

    tally = get_data()
    n = sum(tally.values())

    #TODO: better sampling
    sample_tally = {}
    for key, count in tally.items():
        new_count = int(count/1000.0)
        if new_count > 0:
            sample_tally[key] = new_count
    sample_size = sum(sample_tally.values())
    print("Sample size: %d" % sample_size)
   
    tie_breaker = [] 
    real_names = get_candidates(sample_tally)

    unique_ballots = list(sample_tally.keys())

    vote_for_n = 1

    num_trials = 100
    print("Num trials: %d" % num_trials)

    seed = 1
    print("Seed: %s" %str(seed))

    sample_tallies = [[ sample_tally[name]  for name  in unique_ballots ]]
    win_probs = compute_win_probs_rcv(sample_tallies,
                      [n], 
                      seed,
                      num_trials,
                      unique_ballots,
                      real_names,
                      vote_for_n)
    print("Win probs: %s" % str( win_probs))

if __name__ == '__main__':
    audit()
#import cProfile
#cProfile.run('audit()')


    
