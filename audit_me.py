# audit_me.py
# Ronald L. Rivest
# September 26, 2018

"""
Code to simulate auditing of ME RCV contest.
"""

from consistent_sampler import sampler
import hashlib

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

    L = rcv.read_ME_data('me_votes.csv', True)

    return L


def audit():

    L = get_data()
    n = len(L)

    sample_order = list(sampler(range(n), with_replacement=False, output='id', seed=1))
    print("Sample order[:50]:", sample_order[:50])

    n_stages=50
    for stage in range(1, n_stages+1):
        print("Audit stage: {} ".format(stage), end='')

        s = min(n, stage*50)    # for efficiency
        S = [L[sample_order[i]] for i in range(s)]

        # want to do this part many times, to get win frequency
        for i in range(s, s*10):
            S.append(S[randint(0, i)])
        w = rcv.rcv_winner(S, [], printing_wanted=False)
        print("Winner:", w)

import cProfile
cProfile.run('audit()')


    
