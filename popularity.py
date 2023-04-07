from tmdbv3api import Movie, Person
import datetime

database = Movie()
person = Person()

# -----------------------------------------------------------------------
""" Print List In Order of Popularity """
def popularity(chains, file):

    start_time = datetime.datetime.now()

    new_chains = []
    for chain in chains:
        popularity = database.details(chain[0][0]).popularity + database.details(chain[-1][0]).popularity
        for item in range(1, len(chain) - 1):
            if (item % 2 == 0):
                popularity += database.details(chain[item][0]).popularity
            else:
                popularity += person.details(chain[item][0]).popularity
        new_chains.append((chain, popularity))

    # Sort chains by popularity
    new_chains.sort(key = lambda x: x[1])
    new_chains.reverse()

    end_time = datetime.datetime.now()

    # Write sorted popularity to file
    file.write("\nChains sorted by popularity: \n")
    for item in range(len(new_chains)):
        # Print list number
        file.write("%i. " %(item+1))

        # Print each chain
        for step in range(len(new_chains[item][0])-1):
            file.write("%s -> " % new_chains[item][0][step][1])
        file.write(new_chains[item][0][-1][1])

        # Print popularity of each chain
        file.write(" | Popularity: %.2f\n" %new_chains[item][1])
    file.write(f"\nTime Elapsed: {end_time-start_time}\n")

    # Print chains sorted by popularity
    printpop(new_chains)

    # Print elapsed time
    print(f"\nTime Elapsed: {end_time-start_time}")

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
