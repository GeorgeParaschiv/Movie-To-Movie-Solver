from tmdbv3api import TMDb, Movie, Person
from tmdbv3api.exceptions import TMDbException
import requests
import re
import datetime
import textwrap
import os
import popularity as p

# API Key 
import config

# Global Variables
tmdb = TMDb()
database = Movie()
person = Person()
tmdb.api_key = config.api_key
tmdb.language = 'en'
fail_counter = 0
dne_counter = 0
# -----------------------------------------------------------------------
""" Get The Daily Challenge """
def get_daily_challenge():
    # Grabbing the Daily Challenge from the Website
    url = 'https://movietomovie.com/bundle.js'
    response = requests.get(url)

    # Extract the movie information from the JavaScript code using regular expressions
    regex = r'\[{id:(.*?),title:\"(.*?)\",poster:.*?},{id:(.*?),title:\"(.*?)\",poster:.*?}\]'
    matches = re.findall(regex, response.text)

    # Create a list of dictionaries containing the different daily challenges
    daily_challenges = []

    # Parsing the daily challenges into a list
    for match in matches:
        start = {'id': int(match[0]), 'title': match[1]}
        end = {'id': int(match[2]), 'title': match[3]}
        daily_challenges.append([start, end])

    # Calculating the challenge index based on days since the source date
    time = datetime.datetime.strptime("05 Mar 2022 13:00:00", "%d %b %Y %H:%M:%S")
    days_since = (datetime.datetime.now() - time).days
    time = days_since % len(daily_challenges)

    # Grab the current daily challenge
    return daily_challenges[time]

# -----------------------------------------------------------------------
""" Grab The Cast From A Specific Movie ID """
def get_cast(movie_id):
    # Store cast in list of tuples (actor_id, actor_name, actor_popularity)
    cast = []

    # Handle connection errors or non-existant actors
    while (True):
        try:
            movie = database.details(movie_id)
        except TMDbException:
            dne_counter += 1
            return cast
        except:
            global fail_counter 
            fail_counter += 1
        else:
            break
     
    actors = movie.casts['cast']
    for actor in actors:
        cast.append((actor.id, actor.name, actor.popularity))
    return cast

# -----------------------------------------------------------------------   
""" Grab The Movies From A Specific Actor ID """
def get_movies(actor_id):
    # Store movies in list of tuples (movie_id, movie_name, movie_popularity)
    movies = []

    # Handle connection errors or non-existant actors
    while (True):
        try:
            credits = person.movie_credits(actor_id).cast
        except TMDbException:
            dne_counter += 1
            return movies
        except:
            global fail_counter
            fail_counter += 1       
        else:
            break

    for movie in credits:
        try:
            movies.append((movie.id, movie.original_title, movie.popularity))
        except:
            movies.append((movie.id, movie.original_title, 0))
    return movies

# -----------------------------------------------------------------------   
""" Find All Chains Of A Specified Length (Limit) """
def chainfinder(chain, list, iterations, movie_flag, limit, reverse):
    # If the list is a list of movies:
    if (movie_flag):
        # If we reach the limit and the end movie is in the list of movies, we have discovered a valid chain
        if (iterations == limit):
            if (any(end_movie[0] in movie for movie in list)):
                new_chain = chain.copy()
                new_chain.append(end_movie)

                # Print the chain and add it to the list of chains
                print("%i. " %(len(chains) + 1), end = "")
                printchain(new_chain, reverse)
                chains.append(new_chain)
            return
        # If not at the limit recursively call function for list of cast of each movie
        else:
            for movie in list:
                # Discard the chain if we have come across the movie before, or we have reached the end movie before the limit
                if (movie[0] == start_movie[0]) or (movie[0] == end_movie[0]):
                    continue
                else:
                    new_chain = chain.copy()
                    new_chain.append(movie)
                    cast = get_cast(movie[0])
                    chainfinder(new_chain, cast, iterations, False, limit, reverse)
    # If the list is a list of actors:
    else:
        for actor in list:
            # Discard chain if we have come across the actor before
            if (limit == 2 and iterations == 1):
                if (chain[1][0] == actor[0]):
                    continue
            # Recursively call function for list of movies of each actor
            
            new_chain = chain.copy()
            new_chain.append(actor)
            movies = get_movies(actor[0])
            chainfinder(new_chain, movies, iterations+1, True, limit, reverse)

# -----------------------------------------------------------------------

""" Print Headers And Call Chainfinder Algorithm """
def solutions(start_movie, limit, file, reverse):

    # Clear chains and print header
    chains.clear()
    print("\nChains of length %i: " %limit)

    # Write header to file
    file.write("\nChains of length %i: \n" %limit)
    start_time = datetime.datetime.now()

    # Find and print all possible chains
    chainfinder([start_movie], get_cast(start_movie[0]), 0, False, limit, reverse)

    # If no chains found print error message
    if (not chains):
        print("No chains of length %i connecting the movies was found." %limit)
        file.write("No chains of length %i connecting the movies was found.\n" %limit)
    else:
        # Write each line to the file
        for chain in chains:
            file.write("%i. " %(chains.index(chain) + 1))

            # If reversed write it backwards
            if reverse:
                for step in range(len(chain)-1, 0, -1):
                    file.write("%s -> " %chain[step][1])
                file.write(chain[0][1])
            else:
                for step in range(len(chain)-1):
                    file.write("%s -> " %chain[step][1])
                file.write(chain[-1][1])
            file.write("\n")

        # Reprint chain sorted by populairty    
        p.popularity(chains, file, reverse)
    
    end_time = datetime.datetime.now()

    file.write(f"\nTime Elapsed: {end_time-start_time}\n")
    print(f"\nTime Elapsed: {end_time-start_time}")

# -----------------------------------------------------------------------
""" Print Each Chain """
def printchain(chain, reverse):
    if reverse:
        for step in range(len(chain)-1, 0, -1):
            print("%s -> " %chain[step][1], end = "")
        print(chain[0][1])
    else:
        for step in range(len(chain)-1):
            print("%s -> " % chain[step][1], end = "")
        print(chain[-1][1])

# -----------------------------------------------------------------------
""" Search for Custom Challenge Movies """
def search(start):
     # Loop until user picks a movie
    initial = 0
    cycle = []
    space = False
    while (True):
    
        # Search for the movie
        if (not cycle):
            print("Search for the %s movie: " %("start" if start else "end"))
            string = input()
            search  = database.search(string)
        else:
            search = cycle

        # Print up to 10 options and prompt user to choose
        if (initial >= len(search)):
            initial = 0
        for index in range(initial, initial + 5):
            if (index >= len(search)):
                break
            
            print("%s%i. Name: %s (%s)" %("" if space else "\n", index + 1, search[index].title, search[index].release_date[0:4]))
            wrapper=textwrap.TextWrapper(initial_indent = ('   ' if index < 9 else '    '), 
                                         subsequent_indent = (('\t' + '     ') if index < 9 else ('\t' + '      ')), 
                                         width = 120)
            print(wrapper.fill("Overview: " + ("None" if search[index].overview == "" else search[index].overview)))
            space = False

        # Search yielded no results
        if (len(search) == 0):
            if (string != ""):
                print()
            print("The search yielded no options. Press enter to search again.")
            if (input() != ""):
                print()
            continue
        # Only one movie option
        if (len(search) == 1):
            print("\nThere is only one option. Press enter to select it or 0 to search again:")
            string = input()
            if (string != "0"):
                if (string != ""):
                    print()
                return (search[0].id, search[0].original_title, search[0].popularity)
            print()
        # Multiple options
        else:
            upper_limit = initial + 5 if initial + 5 <= len(search) else len(search)
            print("\nPick a movie (%i-%i), press enter to see more results, or 0 to search again:" %(initial+1, upper_limit))
            selection = input()
            if (selection == ""):
                initial += 5
                cycle = search
                space = True
            elif (not selection.isnumeric()):
                initial+=5
                cycle = search
            else:
                print()
                selection = int(selection) - 1
                if (selection != -1 and selection < upper_limit and selection >= initial): 
                    return (search[selection].id, search[selection].original_title, search[selection].popularity)
                elif (selection == -1):
                    cycle = []
                elif (selection >= upper_limit or selection <= initial):
                    initial += 5
                    cycle = search

# -----------------------------------------------------------------------
""" Main """

# Initializing chains
chains = [] 

print("\nDo you want to solve the daily challenge, or make your own custom challenge to solve? (D/C)")
daily = input()

# Daily Challenge
if (daily == 'D'):
    challenge = get_daily_challenge()

    # Start and End Movies
    start_movie = (challenge[0]['id'], challenge[0]['title'], database.details(challenge[0]['id']).popularity)
    end_movie = (challenge[1]['id'], challenge[1]['title'], database.details(challenge[1]['id']).popularity)   
    
    # Open the text file
    file = open((os.getcwd() + "\\Logs\\Daily Challenges\\" + start_movie[1].replace(":", "") + " - " + end_movie[1].replace(":", "") + ".txt"), 'w', encoding='utf-8')
    file.write("Daily Challenge: %s -> %s\n" %(start_movie[1], end_movie[1]))

    print("\nDaily Challenge: %s -> %s" %(start_movie[1], end_movie[1]))

# Custom Challenge
elif (daily == 'C'):
    
    print()
    
    # Search for the start and end movies
    start_movie = search(True)
    end_movie = search(False)

    # Open the text file
    file = open((os.getcwd() + "\\Logs\\Custom Challenges\\" + start_movie[1].replace(":", "") + " - " + end_movie[1].replace(":", "") + ".txt"), 'w', encoding = 'utf-8')
    file.write("Custom Challenge: %s -> %s\n" %(start_movie[1], end_movie[1]))
    
    print("Custom Challenge: %s -> %s" %(start_movie[1], end_movie[1]))

# Reverse the finder in end_movie_size < start_movie_size
start_movie_size = len(database.details(start_movie[0]).casts['cast'])
end_movie_size = len(database.details(end_movie[0]).casts['cast'])

if (end_movie_size < start_movie_size):
    start_movie, end_movie = end_movie, start_movie
    reverse = True
else:
    reverse = False

# Finding all chains of length 1
solutions(start_movie, 1, file, reverse) 

# Finding all chains of length 2
solutions(start_movie, 2, file, reverse)

# Close the file
file.close() 

print("\nThere were %i actors or movies that did not exist." %dne_counter)
print("There %s %i connection failures." %("was" if fail_counter == 1 else "were", fail_counter))
