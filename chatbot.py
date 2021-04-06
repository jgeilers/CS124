#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import numpy as np
import string
import re
import Queue as q
import random
import difflib
import collections

from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'Figaro'
      self.movieList = []
      self.is_turbo = is_turbo
      self.genre_dict = {}
      self.title_to_year = {}
      self.multiyear_titles = set()
      self.franchises = set()
      self.franchise_to_titles = collections.defaultdict(list)
      self.read_data()
      self.p = PorterStemmer()
      self.another_recommendation = False
      self.stack = []
      self.prev_movie = ''
      self.remember_conversation = False
      self.movie_sentiment = []
      self.asking_for_year = False
      self.asking_for_franchise = False

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = """Hey! My name is {}! Tell me what you think about some movies 
        and I'll give you some recommendations!""".format(self.name)

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = """Thanks for chatting with me! I hope you liked my recommendations. 
          Have a nice day!"""

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def similar(self, word1, word2):
      toReturn = difflib.SequenceMatcher(None, word1, word2)
      toReturn = toReturn.ratio()
      return toReturn

    def calcMinDistance(self, title):
      pq = []
      for line in self.titles:
        movie, year = ' '.join(line[0].split()[:-1]), line[0].split()[-1]
        pq.append((self.similar(title, movie), movie + ' ' + year))
      pq = sorted(pq, key=lambda x: x[0])
      return pq[-1]

    def calcMinDistanceNoQuotes(self, title):
      pq = []
      for line in self.titles:
        movie = line[0]
        pq.append((self.similar(title, movie), movie))
      pq = sorted(pq, key=lambda x: x[0])
      return pq[-1]

    def getMovieName(self, movies, input):

      if len(movies) > 0 and movies[0] not in self.genre_dict.keys():
        # disambiguation
        if movies[0] in self.multiyear_titles:
            yr_list = self.title_to_year[movies[0]]
            if len(yr_list) == 2:
                years = yr_list[0] + ' or ' + yr_list[1]
            else:
                years = ''
                for i in range(len(yr_list) - 1):
                    years += (yr_list[i] + ', ')
                years += ('or ' + yr_list[-1])
 
            response = (
                'Which "{}" did you mean? The one made in '.format(movies[0])
                + years + '?'
            )
            self.asking_for_year = True
            self.prev_movie = movies[0]
            self.prev_input = input
            return True, response
 
        if movies[0] in self.franchises:
            response = 'Which "{}" are you talking about?'.format(movies[0])
            response += '\nPlease respond with the letter for the one you mean!'
            for idx, title in enumerate(self.franchise_to_titles[movies[0]]):
                response += '\n' + '(' + chr(idx + ord('A')) + ') ' + title
 
            self.asking_for_franchise = True
            self.prev_movie = movies[0]
            self.prev_input = input
            return True, response

        if len(movies[0].strip()) > 0:
          result = self.calcMinDistance(movies[0])
          mostSimilar = result[0]
          newTitle = result[1]
          if mostSimilar > .75:
            movies[0] = newTitle
          else:
            for x in self.genre_dict.keys():
              if x.find(movies[0]) != -1:
                movies[0] = x


      if len(movies) == 0 and self.is_turbo == True:
        capitalIndex = [i for i, c in enumerate(input) if c.isupper()]
        regex = re.findall('(\(\\d\\d\\d\\d\))', input)
        spaces = [i for i, ltr in enumerate(input) if ltr == ' ']
        spaces.append(len(input))
 
        if len(capitalIndex) > 0:
          pairList = []
          for val in capitalIndex:
            for space in spaces:
              pairList.append(self.calcMinDistance(input[val:space]))
          pairList = sorted(pairList, key = lambda x: len(x[1]), reverse =False)
          pairList = sorted(pairList, key = lambda x:x[0])
          if pairList[len(pairList) - 1][0] > .87:
            movies.append(pairList[len(pairList) - 1][1])



      error = False
      sentence = ""
      if len(movies) == 0 or movies[0].strip() == "":
        noMovieResponse = [
          "Sorry, I don't understand. Tell me about a movie that you have seen.", 
          "Oops! You forgot to give me a movie title. Tell me about any flicks you've seen recently.",
          "I don't know what you mean. Tell me about your favorite movie ever!",
          "I didn't catch that. What is the worst movie in existence?",
          "I didn't catch a movie title in there. Could you rephrase that?",
          "I don't know what you mean. If you don't tell me about movies you like I can't do my job right.",
          "Don't forget, we're talking about movies. Give me a review of a movie.",
          "Can you try again? I didn't recognize any movie titles in your statement."
        ]
        sentence = random.choice(noMovieResponse)
        error = True
        
      elif len(movies) > 1:
        multipleMovieResponse = [
          "Please tell me about one movie at a time. Go ahead.",
          "Whoa! Slow down there, cowboy. Give me one movie at a time.",
          "Whoa, whoa, whoa. Slow down. I can only think about one movie at a time.",
          "Sorry, I see that you put more than one movie. Try again!",
          "You mentioned too many movies! Can you tell me one at a time?",
          "One movie at a time please! Let's hear what you got to say!",
          "Sorry I'm a bit overwhelmed. Can you tell me one movie at a time?",
          "One movie at a time please! I'm not quite smart enough to process two movies at once yet."
        ]
        sentence = random.choice(multipleMovieResponse)
        error = True

      elif movies[0] in self.movieList:
        sameMovieResponse = [
          "You already told me about that movie! What other movies have you seen?",
          "Oh, yeah! You told me about that movie earlier. What other movies have you seen?",
          "Mhm. We already talked about that movie. What other movies have you watched.",
          "Tell me how you really feel! We already talked about that. Any others you've seen?",
          "Yeah, yeah. I've seen that a few more time than I'd like to admit. Let's talk about another movie.",
          "Someone doesn't know about the multi-armed bandit problem! Life's too short to talk about the same movie all day. Any other movies?",
          "My favourite record is a broken one, but I don't like to hear about movies twice! What else have you seen?",
          "We already talked about that movie. Try again!"
        ]
        sentence = random.choice(sameMovieResponse)
        error = True

      elif movies[0] not in self.genre_dict.keys():
        unknownMovieResponse = [
          "Oh no! I don't have any information about \"{}\"! I've never seen that movie, hope to see it soon, though. Can you tell me about another movie?",
          "I've never heard of \"{}\"! I'll make sure to see it. But for now could you tell me about another movie, hopefully one I've heard of?",
          "Sorry I don't know anything about \"{}\", so I can't recommend another movie properly based off of that. Do you mind telling me about a different one?",
          "Is \"{}\" a movie? Never heard of it. Could you try again?",
          "I know I seem like I know everything about movies, but I haven't heard of \"{}\". Can you tell me about another movie?",
          "Hm, never heard of \"{}\". I appreciate you telling me about it, but I can't use that to recommend other movies. Do you mind telling me about another one?",
          "\"{}\" is not a title a recognize. Tell me about another movie!",
        ]
        sentence = random.choice(unknownMovieResponse).format(movies[0])
        error = True

      return error, sentence

    
    def ask_for_year(self, input):
      self.asking_for_year = False
      year = re.findall('\d\d\d\d', input)
      if len(year) != 1:
          self.asking_for_year = True
          yr_list = self.title_to_year[self.prev_movie]
          if len(yr_list) == 2:
              years = yr_list[0] + ' or ' + yr_list[1]
          else:
              years = ''
              for i in range(len(yr_list) - 1):
                  years += (yr_list[i] + ', ')
              years += ('or ' + yr_list[-1])
          response = 'Sorry! I can only understand if you tell me exactly one year! '
          response += (
              'Which "{}" did you mean? The one made in '.format(self.prev_movie)
              + years + '?'
          )
          return response
      year = '(' + year[0] + ')'
      new_title = self.prev_movie + ' ' + year
      new_input = self.prev_input.replace(self.prev_movie, new_title)
      return self.process(new_input)
 
    def ask_for_franchise(self, input):
        self.asking_for_franchise = False
        choices = re.findall('[A-Za-z]', input)
 
        if len(choices) > 1:
            self.asking_for_franchise = True
            return "Hey man you're throwing a lot at me here and it's kinda tough to get it all. Can you please specify only one title?"
        if len(choices) < 1:
            self.asking_for_franchise = True
            return "C'mon friend throw me a bone! Which movie are you talking about?"
 
        choice = choices[0].upper()
        idx = ord(choice) - ord('A')

        if idx > len(self.franchise_to_titles[self.prev_movie]):
          self.asking_for_franchise = True
          return "Hey there bud. You're kinda making it hard for me to do my job here! Just give me one of the letters!"

        new_title = self.franchise_to_titles[self.prev_movie][idx]
        new_input = self.prev_input.replace(self.prev_movie, new_title)
        return self.process(new_input)


    def read_genres(self):
      movies = open('data/movies.txt', 'r')
      for line in movies:
        split_line = line.split('%')
        title = split_line[1]
        regex = re.findall('(\(\\d\\d\\d\\d\))', title)
        if len(regex) == 1:
          stopIndex = title.find('(')
          yearIndex = title.find(regex[0])
          tempTitle = title[:stopIndex]
          year = title[yearIndex:]
        titleArray = tempTitle.split()
        if len(titleArray) > 0 and ('The' == titleArray[-1] or "A" == titleArray[-1] or "An" == titleArray[-1]  or "Le" == titleArray[-1]):
          article = titleArray[-1]
          title = article + ' ' + title
          toFind = ', ' + article
          removeIndex = title.find(toFind)
          endOfTitle = title[removeIndex + 2 + len(article):]
          title = title[:removeIndex]
          title += endOfTitle
        
        genres = split_line[2].replace('\n', '')
        self.genre_dict[title] = genres.split('|')
 
        # multiyear titles
        title_minus_year, year = ' '.join(title.split()[:-1]), title.split()[-1]
        if title_minus_year in self.title_to_year:
          self.multiyear_titles.add(title_minus_year)
          self.title_to_year[title_minus_year].append(year)
        else:
          self.title_to_year[title_minus_year] = [year]
 
        # franchises
        franchise_breaks = [':', ' and the ']
        for fb in franchise_breaks:
            if fb in title_minus_year:
                franchise = title_minus_year.split(fb)[0]
                self.franchises.add(franchise)
                self.franchise_to_titles[franchise].append(title)
            else:
                self.franchise_to_titles[title_minus_year].append(title)


    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
        
      if self.another_recommendation:
        recommendation = self.recommend_movie()
        return "I suggest you watch " + recommendation + "." + " Would you like to hear another recommendation? (Or enter :quit if you're done.)"

      movies = re.findall('\"(.+?)\"', input)

      if self.asking_for_year:
        return self.ask_for_year(input)

      if self.asking_for_franchise:
        return self.ask_for_franchise(input)

      if self.remember_conversation:
        if len(movies) == 0:
          movies.append(self.prev_movie)
        self.remember_conversation = False
      
      error, sentence = self.getMovieName(movies, input)
      if error:
        return sentence

      sentiment_words = input.replace(movies[0], ' MOVIETITLE ')

      sentiment_words = sentiment_words.replace('.', ' PERIODSTOP ')
      sentiment_words = sentiment_words.replace('!', ' EXCLAMATIONPOINT ')
      sentiment_words = sentiment_words.replace('?', ' QUESTIONMARK ')
      break_words = ['PERIODSTOP', 'EXCLAMATIONPOINT', 'QUESTIONMARK']

      words = re.findall('[\w\']+', sentiment_words)

      others = []
      for word in words:
        if word not in break_words and word != 'MOVIETITLE':
          word = self.p.stem(word).lower()
          others.append(word)
        else:
          others.append(word)
      
      pos_neg = 0
      multiplier = 1

      negation_words = [
        'not', 'never', 'don\'t', 'didn\'t', 'can\'t', 'won\'t',
        'aren\'t', 'ain\'t', 'isn\'t', 'haven\'t', 'hasn\'t',
        'hadn\'t', 'wouldn\'t', 'doesn\'t', 'wasn\'t', 'couldn\'t'
      ]

      strong_sentiment_words = [
        'hate', 'love', 'favorite', 'perfect', 'best', 'worst'
      ]

      amplifier_words = [
        self.p.stem('really'), self.p.stem('very')
      ]

      for idx, word in enumerate(strong_sentiment_words):
          stem = self.p.stem(word)
          strong_sentiment_words[idx] = stem

      strong_sentiment = False
      amplifying = False
      exclamation_count = 0
      for word in others:
        if word in strong_sentiment_words and multiplier != -1:
          strong_sentiment = True
        if word in amplifier_words:
          amplifying = True
          continue
        if word == 'EXCLAMATIONPOINT':
          exclamation_count += 1

        if word in negation_words:
          multiplier *= -1

        if word in break_words:
          multiplier = 1

        if word in self.sentiment:
          if self.sentiment[word] == 'pos':
            pos_neg += multiplier
          else:
            pos_neg -= multiplier
          if amplifying:
            strong_sentiment = True

        if word not in negation_words and word not in self.sentiment:
          amplifying = False

      if exclamation_count >= 2:
          strong_sentiment = True

      positive_responses = [
        'Woah, you liked "{}"? Me too man. Gnarly!',
        'You thought "{}" was a dope movie? That\'s sick!',
        'You think "{}" is as tubular a movie as I do? You\'re a real broski.',
        'Glad to hear you liked "{}"! It\'s one of my faves.',
        'I\'d give you a high five for liking "{}", but unfortunately I don\'t have hands.',
        'I can respect your taste, but I just didn\'t like "{}" as much as you I guess.',
      ]
    
      negative_responses = [
        'Not a big fan of "{}" I see? No worries, they can\'t all be winners.',
        'You didn\'t like "{}"? Yea, I wasn\'t feeling it either.',
        'I can\'t believe you don\'t like "{}", but to each their own.',
        'A great thinker once said, \'I don\'t like "{}."\' That thinker is you.',
        'Movies are meant to entertain, but it looks like "{}" didn\'t do it for ya.',
        'I wish you thought "{}" was as good as some other people tell me it is.'
      ]
    
      unsure_responses = [
        'I\'m not sure that I\'m picking up what you\'re putting down on "{}". You mind telling me a little more?',
        'I can\'t really tell how you feel about "{}". Can you give me some more deets?',
        'I don\'t know whether "{}" tickled your fancy or not. Want to give me a hint?',
        "Hm. I couldn't get a read on how you felt about \"{}\". Would you mind telling me a little more?",
        "Sorry, I didn't catch how you felt about \"{}\". Please tell me a little more.",
        "I missed that, sorry. Can you give me a little more information regarding how you felt about \"{}\"?"
      ]

      movie_title = movies[0]
      response = ''

      if pos_neg > 0:
        response += random.choice(positive_responses).format(movie_title)
        if strong_sentiment:
          strongPosResponseArray = [
            ' I can tell you THOROUGHLY enjoyed this movie.',
            ' You seem to think this was a HIGH quality movie. Makes sense that you like it so much.',
            ' I ran the numbers and here are the results: you REALLY like this one.',
            ' You must have had a GOOD date to this movie. Otherwise, I\'m not sure why you like it so much!'
          ]
          response += random.choice(strongPosResponseArray)
        self.movieList.append(movie_title)
        self.movie_sentiment.append(1)
      elif pos_neg < 0:
        response += random.choice(negative_responses).format(movie_title)
        if strong_sentiment:
          strongNegResponseArray = [
            ' Pretty obvious this one would NOT be an Oscar winner in your book.',
            ' I bet you wanted to BURN the studios down after this one.',
            ' It WAS pretty terrible, now that I think about it.',
            ' Some movies just AREN\'T worth seeing.',
            ' It just DIDN\'T live up to expectations.' 
          ]
          response += random.choice(strongNegResponseArray)
        self.movieList.append(movie_title)
        self.movie_sentiment.append(-1)
      else:
        response = random.choice(unsure_responses).format(movie_title)
        self.prev_movie = movies[0]
        self.remember_conversation = True

      if len(self.movieList) >= 5:
        indexArray = []
        uList = []
        for movie in self.movieList:
          for i in xrange(len(self.titles)):
            if self.titles[i][0] == movie:
              indexArray.append(i)
              uList.append(self.ratings[i])
              continue

        
        self.recommend(uList, indexArray)
        recommendation = self.recommend_movie()
        return response + '\n' + "That's enough for me to make a recommendation." + '\n' + "I suggest you watch " + recommendation + "." + " Would you like to hear another recommendation? If so, enter anything. Otherwise, enter :quit if you're done."

      else:
        if pos_neg != 0:
          responseArray = [
            " Let’s keep talking, tell me about another movie!",
            " Tell me about more movies!",
            " Tell me about another movie you've seen!",
            " What other movies have you seen?",
            " I love talking to you about movies. Tell me some more!",
            " This is so fun. What else have you seen?",
            " I love movies! Tell me about some more."
          ]
          response += random.choice(responseArray)
        else:
          response += " Or, tell me about a different movie you've seen!"
        
        return response


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j

      self.titles, self.ratings = ratings()

      for i in xrange(len(self.titles)):
        title = self.titles[i][0]
        regex = re.findall('(\(\\d\\d\\d\\d\))', title)
        if len(regex) == 1:
          genre = self.titles[i][1]
          stopIndex = title.find('(')
          yearIndex = title.find(regex[0])
          tempTitle = title[:stopIndex]
          year = title[yearIndex:]
        titleArray = tempTitle.split()
        if len(titleArray) > 0 and ('The' == titleArray[-1] or "A" == titleArray[-1] or "An" == titleArray[-1]  or "Le" == titleArray[-1]):
          article = titleArray[-1]
          title = article + ' ' + title
          toFind = ', ' + article
          removeIndex = title.find(toFind)
          endOfTitle = title[removeIndex + 2 + len(article):]
          title = title[:removeIndex]
          title += ' ' + endOfTitle
          self.titles[i] = (title, genre)

      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)
      if self.is_turbo == False:
        self.binarize()
      self.read_genres()


    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      
      self.ratings = np.where(self.ratings == 2.5, -1, self.ratings)
      self.ratings = np.where(self.ratings == 2.0, -1, self.ratings)
      self.ratings = np.where(self.ratings == 1.5, -1, self.ratings)
      self.ratings = np.where(self.ratings == 1.0, -1, self.ratings)
      self.ratings = np.where(self.ratings == 0.5, -1, self.ratings)
      self.ratings = np.where(self.ratings >= 3.0, 1, self.ratings)


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure
      
      dotProduct = np.dot(u, v)
      denom1 = np.linalg.norm(u)
      denom2 = np.linalg.norm(v)
      if denom1 == 0 or denom2 == 0:
        return 0
      return float(dotProduct) / (denom1 * denom2)


    def recommend(self, u, indexArray):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot

      sum = 0
      pq = []
      for i in xrange(len(self.ratings)):
        if i not in indexArray:
          for k in xrange(len(u)):
            sum += self.distance(self.ratings[i], u[k]) * self.movie_sentiment[k]
          pq.append((sum, self.titles[i][0]))
          sum = 0
      pq = sorted(pq, key=lambda x:x[0])

      for i in xrange(len(pq)):
        self.stack.append(pq[i][1])


    def recommend_movie(self):
      recommendation = self.stack.pop()
      self.another_recommendation = True
      return recommendation


    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Hello! Welcome to my humble abode. I was implemented according to the details 
      in the PA6 instructions that some creators' instructor gave to them. If you use 
      my simple mode, please be kind to me and only tell me about movies in the 
      correct format. If you want to check out my ~turbo~ mode, give me all you got,
      I can handle it, and still give you the best movie according to your preferences.

      Enjoy!

      Creative Features include:
       - Fine-grained sentiment extraction
         - Identifies amplifiers: "very, really"
         - Identifies strong words: "hate, love, favorite, perfect, best, worst"
            (Bot responds with one word in all caps)
       - Spell-checking movie titles
       - Disambiguating movie titles for series and year ambiguities
         - Doesn't need year
         - Asks user which movie from the franchise/series they liked best
            (Test this without turbo)
       - Recognizes movie without year
       - Understanding references to things said previously
       - Keeps track of which movies have already been mentioned
       - Speaking very fluently
       - Alternate/foreign titles
       
      Turbo Mode ONLY:
       - Identifying movies without quotation marks or perfect capitalization
       - Using non-binarized dataset
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
