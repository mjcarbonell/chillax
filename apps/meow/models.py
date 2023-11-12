"""
This file defines the database models
"""
import random
# text generation ^^^^^^ 

import datetime
import random
from py4web.utils.populate import FIRST_NAMES, LAST_NAMES, IUP
from .common import db, Field, auth
from pydal.validators import *

class MarkovChain:
    def __init__(self):
        self.memory = {}

    def _learn_key(self, key, value):
        if key not in self.memory:
            self.memory[key] = []
        self.memory[key].append(value)

    def learn(self, text):
        tokens = text.split(" ") # modern, techhnologies, ... 
        bigrams = [] # (modern technologies), (technologies, are), , 
        for i in range(0, len(tokens) - 1):
            bigram = (tokens[i], tokens[i + 1])
            bigrams.append(bigram)

        for bigram in bigrams:
            self._learn_key(bigram[0], bigram[1])

    def generate(self, max_length=50):
        start_word = random.choice(list(self.memory.keys()))
        sentence = [start_word]
        for _ in range(max_length):
            if sentence[-1] in self.memory:
                next_word = random.choice(self.memory[sentence[-1]])
                sentence.append(next_word)
            else:
                break  # End if we've reached a word we don't know a next step for
        return ' '.join(sentence)

sample_data = """
Artificial Intelligence (AI) is a rapidly evolving field that has the potential to transform various aspects of our lives. This report draws on several sources to provide insights into the economic potential of generative AI, how AI will transform the way science gets done, how humans and AI might evolve together in the next decade, a new era of generative AI for everyone, the current and future state of AI/ML, and the promise and perils of artificial intelligence.
According to a report by McKinsey[1], generative AI's impact on productivity could add trillions of dollars in value to the global economy. The report estimates that generative AI could add $2.6 trillion to $4.4 trillion annually to the global economy by 2040. This highlights the potential of AI to drive economic growth and create new opportunities.
Eric Schmidt, Google's former CEO, argues that AI will transform the way science gets done[2]. He notes that AI is already transforming how some scientists conduct literature reviews. Tools like PaperQA and Elicit harness LLMs to scan databases of articles and produce succinct and accurate summaries of the existing literature. However, there are still challenges to be addressed, such as aggregating data on molecular properties stored across dozens of databases.
A report by Pew Research Center[3] suggests that we will see big improvements in infrastructure, such as traffic, sewage treatment, and supply chain, due to AI. The report also highlights the need for humans and AI to evolve together in the next decade.
Accenture's report[4] discusses the potential of generative AI and large language models to transform work and reinvent business. The report notes that companies will have thousands of ways to apply generative AI and foundation models to maximize efficiency and drive competitive advantage. However, an enterprise-wide strategy needs to account for all the variants of AI and associated technologies they intend to use, not only generative AI and large language models.
A Reddit post[5] discusses the current and future state of AI/ML and highlights the problem with AI-generation. The post notes that without extreme deterrence, we will sacrifice human achievement at the top percentile. The post also highlights the PaLM (Scaling Language Modeling with Pathways) paper from Google Research, which opened up a can of worms of ideas.
Finally, a documentary by FRONTLINE[6] explores the promise and perils of artificial intelligence, from fears about work and privacy to rivalry between the US and China. The documentary features interviews with experts in the field and provides insights into the potential of AI to transform various aspects of our lives.
In conclusion, AI has the potential to transform various aspects of our lives, from driving economic growth to transforming the way science gets done. However, there are still challenges to be addressed, and humans and AI need to evolve together in the next decade. It is important to have an enterprise-wide strategy that accounts for all the variants of AI and associated technologies.
"""
markov_chain = MarkovChain()
markov_chain.learn(sample_data)

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'follow',
    Field('user_name'),
    Field('uid'),
    Field('user_email',  default=get_user_email),
    Field('creation_date', 'datetime', default=get_time),
)

db.define_table(
    'meow',
    Field('author'),
    Field('content'),
    Field('reply_owner'),
    Field('total_replies'), 
    Field('timestamp', 'datetime', default=get_time),
)

db.commit()

def add_users_for_testing(num_users):
    # Test user names begin with "_".
    # Counts how many users we need to add.
    db(db.auth_user.username.startswith("_")).delete()
    num_test_users = db(db.auth_user.username.startswith("_")).count()
    num_new_users = num_users - num_test_users
    print("Adding", num_new_users, "users.")
    for k in range(num_test_users, num_users):
        first_name = random.choice(FIRST_NAMES)
        last_name = first_name = random.choice(LAST_NAMES)
        username = "_%s%.2i" % (first_name.lower(), k)
        user = dict(
            username=username,
            email=username + "@ucsc.edu",
            first_name=first_name,
            last_name=last_name,
            password=username,  # To facilitate testing.
        )
        auth.register(user, send=False)
        ts = datetime.datetime.utcnow()
        ts -= datetime.timedelta(seconds=random.uniform(60, 1000))
        db.meow.insert(
            author = username,
            timestamp = ts,
            content = markov_chain.generate(), 
        )
    db.commit()
    
# Comment out this line if you are not interested. 

add_users_for_testing(5)
