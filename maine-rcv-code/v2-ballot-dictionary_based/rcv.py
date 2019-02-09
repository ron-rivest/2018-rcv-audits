# Implementation of Maine's RCV rules
# Ronald L. Rivest
# September 26, 2018

# Basic data structure is a list of ballots.
# Each ballot is a tuple of strings (of variable length, perhaps empty.
# String is candidate name (aka choice).


import csv


def choices_on_ballots(L, printing_wanted=False):
    """
    Return a dict of the choices shown on ballot list L, with counts.

    Args:
        L (list): list of ballots
        
    Returns:
        C (dict): dict of distinct strings appearing in ballots in L,
                  each with count of number of occurrences.

    Example:
        
    """

    C = dict()
    ballot_no = 0
    for ballot in L:
        ballot_no += 1
        for choice in ballot:
            if False and choice not in C:
                print("Choice {} first seen in ballot {}"
                      .format(choice, ballot_no))
            C[choice] = 1 + C.get(choice, 0)
    return C


def delete_double_undervotes(tally):
    """
    Delete all double undervotes from a ballot dictionary tally

    If a double undervote occurs, delete it and all
    subsequent positions from ballot.

    Args:
        dictionary {tally}: dictionary  of ballots

    Returns:
        dictionary {tally}: dictionary list of possibly modified ballots

    Example:
        >>> tally = {('undervote','undervote', 'a'):1, ('b', 'undervote', 'undervote', 'c'):1, ('d', 'undervote'):1}
        >>> delete_double_undervotes(tally)
        {(): 1, ('b',): 1, ('d', 'undervote'): 1}
    """

    new_tally = {}
    for ballot , ballot_tally in tally.items():
        double_uv_at = len(ballot)
        for i in range(len(ballot)-1):
            if ballot[i] == 'undervote' \
                and ballot[i+1] == 'undervote' \
                and double_uv_at == len(ballot):
                    double_uv_at = i
        new_ballot = ballot[:double_uv_at]
        new_tally[new_ballot] = new_tally[new_ballot] +  ballot_tally if new_ballot in new_tally.keys() else ballot_tally
    return new_tally


def delete_name(tally, name, delete_following = False):
    """
    Remove all occurrences of name from any ballot in tally.

    When used to remove undervotes, make sure double undervotes
    have already been handled (since following votes are then
    also eliminated).
    
    Args:
        dictionary {tally}: dictionary  of ballots
        name (str): name of choice to be eliminated
        delete_following (bool): True if all following positions on ballot
            are also to be eliminated

    Returns:
        dictionary {tally}: dictionary of possibly modified ballots

    Examples:
        >>> tally = {('undervote', 'a'):1, ('undervote', 'undervote', 'b'):1, ('c', 'undervote'):1}
        >>> delete_undervotes(tally)
        {('a',): 1, (): 1, ('c',): 1}
    """
    new_tally  = {}
    for ballot , ballot_tally in tally.items():
        if name in ballot:
            new_ballot = []
            for c in ballot:
                if c != name:
                    new_ballot.append(c)
                elif delete_following:
                    break
            new_ballot = tuple(new_ballot)
        else:
            new_ballot = ballot
        
        new_tally[new_ballot] = new_tally[new_ballot] +  ballot_tally if new_ballot in new_tally.keys() else ballot_tally
      
    return new_tally


def delete_undervotes(tally):
    """
    Delete undervotes from every ballot in dictionary tally, making sure
    that if there is a double undervote (i.e. two in sequence), 
    then all following votes are removed too.

    Args:
        dictionary {tally}: dictionary  of ballots

    Returns:
        dictionary {tally}: dictionary of possibly modified ballots

    Example:
        >>> tally = {('undervote', 'a'):1, ('undervote', 'undervote', 'b'):1, ('c', 'undervote'):1}
        >>> delete_undervotes(tally)
        {('a',): 1, (): 1, ('c',): 1}
    """

    tally = delete_double_undervotes(tally)
    tally = delete_name(tally, 'undervote')
    return tally


def delete_overvotes(tally):
    """
    Delete all overvotes from ballots in a ballot dictionary tally.

    If an overvote occurs, deletes it and all following positions from ballot.

    Args:
        dictionary {tally}: dictionary  of ballots

    Returns:
        dictionary {tally}: dictionary of possibly modified ballots

    Example:
        >>> tally = {('a', 'overvote', 'b'): 4, ('c', 'overvote') :2 , ('d',) :1 , ('overvote',) : 1 }
        >>> delete_overvotes(tally)
        {('a',): 4, ('c',): 2, ('d',): 1, (): 1}
    """

    return delete_name(tally, 'overvote', True)


def count_first_choices(tally):
    """
    Return dict giving count of all first choices in ballot dictionary tally.
    
    Args:
        tally (dictionary): dictionary of ballots
        
    Returns:
        (dict): dictionary mapping all choices that occur at least once
            as a first choice to count of their number of choices.

    Example:
        >>> tally = {('a', 'b'):1, ('c'):1, ():1, ('d'):1, ('a'):1}
        >>> count_first_choices(tally)
        {'a': 2, 'c': 1, 'd': 1}
    """

    d = dict()
    for ballot , count in tally.items():
        if len(ballot)>0:
            first_choice = ballot[0]
            if first_choice in d:
                d[first_choice] = count + d[first_choice]
            else:
                d[first_choice] = count

    return d


def tie_breaker_index(tie_breaker, name):
    """
    Return the index of name in tie_breaker, if it is present
    there, else return the length of list tie_breaker.

    Args:
        tie_breaker (list): list of choices (strings)
                            list may be incomplete or empty
        name (str): the name of a choice
  
    Returns:
        (int): the position of name in tie_breaker, if present;
               otherwise the length of tie_breaker.

    Example:
        >>> tie_breaker = ['a', 'b']
        >>> tie_breaker_index(tie_breaker, 'a')
        0
        >>> tie_breaker_index(tie_breaker, 'c')
        2
    """

    if name in tie_breaker:
        return tie_breaker.index(name)
    return len(tie_breaker)


def rcv_round(tally, tie_breaker):
    """
    Return winner of RCV (IRV) contest for ballot list L.
    
    Args:
        tally (dictionary): dictionary of ballots to counts
        tie_breaker: list of choices, used to break ties
            in favor of choice earlier in tie list
   
    Returns: 
        (w, d, e, LL)
        where w is either winning choice or None, 
        where d is dict mapping choices to counts,
        where e is candidate eliminated (if w is None),
        where LL is list of ballots eliminating e if w is None.

    Examples:

        >>> tally = {('a', 'b'):1, ('c', 'd'):1, ('c', 'e'):1, ('f', 'a'):1}
        >>> rcv_round(tally, ('a', 'b', 'c', 'd', 'e', 'f'))
        (None, {'a': 1, 'c': 2, 'f': 1}, 'f', {('a', 'b'): 1, ('c', 'd'): 1, ('c', 'e'): 1, ('a',): 1})

        >>> tally = {('a', 'b'):1, ('c', 'd'):1, ('c', 'e'):1, ('f', 'a'):1, ('f', 'b'):1}
        >>> rcv_round(tally, ('a', 'b', 'c', 'd', 'e', 'f'))
        (None, {'a': 1, 'c': 2, 'f': 2}, 'a', {('b',): 1, ('c', 'd'): 1, ('c', 'e'): 1, ('f',): 1, ('f', 'b'): 1})

        >>> tally = {('a', 'b'):1, ('a', 'c'):1}
        >>> rcv_round(tally, ('a', 'b', 'c'))
        ('a', {'a': 2}, None, None)
    """

    d = count_first_choices(tally)
    #TODO(zarap): continue here
    assert len(d)>0, 'Error: all candidates eliminated!!'

    if len(d) == 1:
        w = list(d.keys())[0]
        return (w, d, None, None)

    total_first_choices = sum([d[choice] for choice in d])
    for choice in d:
        if d[choice]==total_first_choices:
            # winner!
            w = choice
            return (w, d, None, None)

    E = [(d[k], -tie_breaker_index(tie_breaker, k), k) for k in d]
    E = sorted(E)
    e = E[0][2]          # choice to be eliminated

    LL = delete_name(tally, e)
    return (None, d, e, LL)


def rcv_winner(tally, tie_breaker, printing_wanted=True):
    """
    Return RCV (aka IRV) winner for ballot list L.

    Args:
        dictionary {tally}: dictionary of ballots (this should be a "cleaned" list)
        tie_breaker: list of all choices, most-favored first
        printing_wanted (bool): True if printing desired

    Returns:
        (str): name of winning choice

    Example:
        >>> tally = {('a', 'b'):1, ('b', 'a'):1, ('b', 'undervote'):1}
        >>> tie_breaker = ['a', 'b']
        >>> rcv_winner(clean(tally), tie_breaker)
        tie_breaker list: ['a', 'b']
        Round: 1
          First Choice Counts:
            a: 1
            b: 2
          Choice eliminated: a
        Round: 2
          Choice b wins!
          Count: 3
        'b'
    """

    round_number = 0

    if printing_wanted:
        print("tie_breaker list: {}".format(tie_breaker))

    while True:

        round_number += 1

        if printing_wanted:
            print("Round: {}".format(round_number))

        #TODO(zarap): fix from here on
        (w, d, e, LL) = rcv_round(tally, tie_breaker)
        
        if w is not None:
            if printing_wanted:
                print("  Choice {} wins!".format(w))
                print("  Count: {}".format(d[w]))
            return w

        if printing_wanted:
            print("  First Choice Counts:")
            choices = sorted(d.keys())
            for choice in choices:
                print("    {}".format(choice), end='')
                print(": {}".format(d[choice]))
            print("  Choice eliminated: {}".format(e))

        tally = delete_name(LL, e)
        

def clean(tally):
    """
    Clean tally of ballots of undervotes, overvotes

    Args:
        dctionary {tally} : dictionary of ballots to be cleaned

    Returns:
        dctionary {clean_tally}: list of cleaned ballots
    """
    
    tally = delete_overvotes(tally)
    tally = delete_undervotes(tally)
    return tally


def read_ME_data(filename, printing_wanted=True):
    """
    Read CSV file and return list of ballots.

    Args:
       filename (str): must be a CSV format file.
       printing_wanted (bool): True for printing basic info.

    Returns:
       {tally}: dictionary of ballot

    Example:
    """

    if printing_wanted:
        print("Reading file `{}'...".format(filename))
    tally = dict()
    # In next line, utf-8-sig needed to get rid of starting BOM \ufeff
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        ballot_reader = csv.reader(csvfile)
        for ballot in ballot_reader:
            ballot_tuple = tuple(ballot)
            tally[ballot_tuple] = 1 + tally.get(ballot_tuple, 0)

    clean_tally = clean(tally)

    if printing_wanted:
        print("Number of ballots read: {}".format(sum(clean_tally.values())))
        print("Number of distinct ballots read: {}".format(sum(clean_tally.values())))
        print("Choices shown on ballots (in any position) with count:")
        for choice, count in clean_tally.items():
            print("    {}: {}".format(choice, count))

    return clean_tally
    

def main():
    votes_dir = "../../maine-rcv-data/"
    votes_filename = votes_dir + 'me_votes.csv'
    tally = read_ME_data(votes_filename)
    tie_breaker = []        
    rcv_winner(tally, tie_breaker)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()
    








