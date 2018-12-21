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


def delete_double_undervotes(L):
    """
    Delete all double undervotes from a ballot list L

    If a double undervote occurs, delete it and all
    subsequent positions from ballot.

    Args:
        L (list): list of ballots

    Returns:
        (list): list of possibly modified ballots

    Example:
        >>> L = [('undervote','undervote', 'a'), ('b', 'undervote', 'undervote', 'c'), ('d', 'undervote')]
        >>> delete_double_undervotes(L)
        [(), ('b',), ('d', 'undervote')]
    """

    LL = []
    for ballot in L:
        double_uv_at = len(ballot)
        for i in range(len(ballot)-1):
            if ballot[i] == 'undervote' \
                and ballot[i+1] == 'undervote' \
                and double_uv_at == len(ballot):
                    double_uv_at = i
        new_ballot = ballot[:double_uv_at]
        LL.append(new_ballot)
    return LL


def delete_name(L, name, delete_following = False):
    """
    Remove all occurrences of name from any ballot in L.

    When used to remove undervotes, make sure double undervotes
    have already been handled (since following votes are then
    also eliminated).
    
    Args:
        L (list): list of ballots
        name (str): name of choice to be eliminated
        delete_following (bool): True if all following positions on ballot
            are also to be eliminated

    Returns:
        (list): list of possibly modified ballots

    Examples:
        >>> L = [('a', 'undervote', 'b'), ('undervote',), ('c',), ()]
        >>> delete_name(L, 'undervote')
        [('a', 'b'), (), ('c',), ()]
    """

    LL = []
    for ballot in L:
        if name in ballot:
            new_ballot = []
            for c in ballot:
                if c != name:
                    new_ballot.append(c)
                elif delete_following:
                    break
        else:
            new_ballot = ballot
        LL.append(tuple(new_ballot))

    return LL


def delete_undervotes(L):
    """
    Delete undervotes from every ballot in L, making sure
    that if there is a double undervote (i.e. two in sequence), 
    then all following votes are removed too.

    Args:
        L (list): list of ballots

    Returns:
        (list): list of possibly modified ballots

    Example:
        >>> L = [('undervote', 'a'), ('undervote', 'undervote', 'b'), ('c', 'undervote')]
        >>> delete_undervotes(L)
        [('a',), (), ('c',)]
    """

    L = delete_double_undervotes(L)
    L = delete_name(L, 'undervote')
    return L


def delete_overvotes(L):
    """
    Delete all overvotes from ballots in a ballot list L.

    If an overvote occurs, deletes it and all following positions from ballot.

    Args:
        L (list): list of ballots

    Returns:
        list: list of possibly modified ballots

    Example:
        >>> L = [('a', 'overvote', 'b'), ('c', 'overvote'), ('d',), ('overvote',) ]
        >>> delete_overvotes(L)
        [('a',), ('c',), ('d',), ()]
    """

    return delete_name(L, 'overvote', True)


def count_first_choices(L):
    """
    Return dict giving count of all first choices in ballot list L.
    
    Args:
        L (list): list of ballots
        
    Returns:
        (dict): dictionary mapping all choices that occur at least once
            as a first choice to count of their number of choices.

    Example:
        >>> L = [('a', 'b'), ('c'), (), ('d'), ('a')]
        >>> count_first_choices(L)
        {'a': 2, 'b': 0, 'c': 1, 'd': 1}
    """

    d = dict()
    for ballot in L:
        for choice in ballot:
            if choice not in d:
                d[choice] = 0
        if len(ballot)>0:
            first_choice = ballot[0]
            d[first_choice] = 1 + d[first_choice]

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


def rcv_round(L, tie_breaker):
    """
    Return winner of RCV (IRV) contest for ballot list L.
    
    Args:
        L (list): list of ballots
        tie_breaker: list of choices, used to break ties
            in favor of choice earlier in tie list
   
    Returns: 
        (w, d, e, LL)
        where w is either winning choice or None, 
        where d is dict mapping choices to counts,
        where e is candidate eliminated (if w is None),
        where LL is list of ballots eliminating e if w is None.

    Examples:

        >>> L = [('a', 'b'), ('c', 'd'), ('c', 'e'), ('f', 'a')]
        >>> rcv_round(L, ('a', 'b', 'c', 'd', 'e', 'f'))
        (None, {'a': 1, 'b': 0, 'c': 2, 'd': 0, 'e': 0, 'f': 1}, 'e', [('a', 'b'), ('c', 'd'), ('c',), ('f', 'a')])

        >>> L = [('a', 'b'), ('c', 'd'), ('c', 'e'), ('f', 'a'), ('f', 'b')]
        >>> rcv_round(L, ('a', 'b', 'c', 'd', 'e', 'f'))
        (None, {'a': 1, 'b': 0, 'c': 2, 'd': 0, 'e': 0, 'f': 2}, 'e', [('a', 'b'), ('c', 'd'), ('c',), ('f', 'a'), ('f', 'b')])

        >>> L = [('a', 'b'), ('a', 'c')]
        >>> rcv_round(L, ('a', 'b', 'c'))
        ('a', {'a': 2, 'b': 0, 'c': 0}, None, None)

    """

    d = count_first_choices(L)
    
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

    LL = delete_name(L, e)
    return (None, d, e, LL)


def rcv_winner(L, tie_breaker, printing_wanted=True):
    """
    Return RCV (aka IRV) winner for ballot list L.

    Args:
        L (list): list of ballots (this should be a "cleaned" list)
        tie_breaker: list of all choices, most-favored first
        printing_wanted (bool): True if printing desired

    Returns:
        (str): name of winning choice

    Example:
        >>> L = [('a', 'b'), ('b', 'a'), ('b', 'undervote')]
        >>> tie_breaker = ['a', 'b']
        >>> rcv_winner(clean(L), tie_breaker)
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

        (w, d, e, LL) = rcv_round(L, tie_breaker)
        
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

        L = delete_name(LL, e)
        

def clean(L):
    """
    Clean list L of ballots of undervotes, overvotes

    Args:
        L (list): list of ballots to be cleaned

    Returns:
        (list): list of cleaned ballots
    """
    
    L = delete_overvotes(L)
    L = delete_undervotes(L)
    return L


def read_ME_data(filename, printing_wanted=True):
    """
    Read CSV file and return list of ballots.

    Args:
       filename (str): must be a CSV format file.
       printing_wanted (bool): True for printing basic info.

    Returns:
       (list): list of ballots:

    Example:
    """

    if printing_wanted:
        print("Reading file `{}'...".format(filename))
    tally = dict()
    # In next line, utf-8-sig needed to get rid of starting BOM \ufeff
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        ballot_reader = csv.reader(csvfile)
        L = []
        for ballot in ballot_reader:
            ballot_tuple = tuple(ballot)
            L.append(ballot_tuple)
            tally[ballot_tuple] = 1 + tally.get(ballot_tuple, 0)

    if printing_wanted:
        print("Number of ballots read: {}".format(len(L)))
        print("Number of distinct ballots read: {}".format(len(tally)))
        C = choices_on_ballots(L)
        print("Choices shown on ballots (in any position) with count:")
        for choice in C:
            print("    {}: {}".format(choice, C[choice]))

    L = clean(L)
    return(L)
    

def main():
    L = read_ME_data('me_votes.csv')
    tie_breaker = []        
    rcv_winner(L, tie_breaker)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    main()
    








