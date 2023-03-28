from tmdbv3api import Movie, Person

database = Movie()
person = Person()

# -----------------------------------------------------------------------
""" Print List In Order of Popularity """
def popularity(chains):
    new_chains = []
    for chain in chains:
        popularity = 0
        for item in range(len(chain)):
            if (item % 2 == 0):
                popularity += database.details(chain[item][0]).popularity
            else:
                popularity += person.details(chain[item][0]).popularity
        new_chains.append((chain, popularity))

    # Sort chains by popularity
    new_chains.sort(key = lambda x: x[1])
    new_chains.reverse()
    printpop(new_chains)

# -----------------------------------------------------------------------
""" Print All Chains By Popularity """
def printpop(new_chains):
    print("\nChains sorted by popularity: ")
    for item in range(len(new_chains)):
        # Print list number
        print("%i. " %(item+1), end = "")

        # Print each chain
        for step in range(len(new_chains[item][0])-1):
            print("%s -> " % new_chains[item][0][step][1], end = "")
        print(new_chains[item][0][-1][1], end = "")

        # Print popularity of each chain
        print(" | Popularity: %.2f" %new_chains[item][1])
