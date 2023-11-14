"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
## NOW 
import openai
import os 
from dotenv import load_dotenv
import requests
import datetime
import random
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_username, get_user_email

load_dotenv()

openai.api_key = os.getenv('API_KEY')
def get_fancy_version(input_text):
    try:
        # Call the OpenAI API with the input text
        response = openai.Completion.create(
          engine="text-davinci-003", # or "text-davinci-004" for GPT-4, if you have access
          prompt=f"Translate the following sentences into a more sophisticated and elaborate title for an art piece: '{input_text}'",
          temperature=0.7,
          max_tokens=60
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        return str(e)

def generate_image(fancy_text):
    try:
        # Hypothetical function call - you'll need to replace this with the actual API call
        response = openai.Image.create(
            prompt=fancy_text,
            n=1,  # Generate one image
            size="1024x1024"  # The size of the image
        )
        # The response would need to include a URL or binary data of the generated image
        image_url = response.data['image_url']  # This is a placeholder
        return image_url
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, url_signer)
def index():
    # return list of people the current user follows 
    print("after index") 
    print("signer: {}".format(url_signer))
    return dict(
        # COMPLETE: return here any signed URLs you need.
        signer=url_signer,
        current=get_user_email(),
        get_users_url = URL('get_users', signer=url_signer),
        follow_url=URL('set_follow', signer=url_signer),
        unfollow_url=URL('set_unfollow', signer=url_signer),
        meow_url=URL('add_meow', signer=url_signer),
    )

@action('home')
@action.uses('home.html', db, url_signer)
def home():
    print("in home")
    return dict(
        signer=url_signer, 
        post_url=URL('submit_post', signer=url_signer), 
        get_posts_url=URL('get_posts', signer=url_signer),
    )


@action("get_users")
@action.uses(db)
def get_users():
    # Implement. 
    print("in get users")
    rows = db(db.auth_user.username).select()    
    meows = db(db.meow.author >= 0).select()
    current = get_user_email()
    currentUser = "" 
    for i in rows: 
        if(current == i.email):
            currentUser = i.username
    # print(currentRow.email)    
    followList = db(db.follow.user_email == get_user_email()).select() 
    return dict(rows=rows, current=current, followList=followList, meows=meows, currentUser=currentUser)

@action("get_posts")
@action.uses(db)
def get_posts():
    # Implement. 
    print("in get postss")
    posts = db(db.posts.prompt >= 0).select()    
    return dict(posts=posts)



@action('add_meow', method="POST")
@action.uses(db, url_signer.verify())
def add_meow():
    user_name = request.json.get('user_name')
    content = request.json.get('content')
    ts = datetime.datetime.utcnow()
    reply_owner = request.json.get('reply_owner')
    total_replies = request.json.get('total_replies')
    # ts -= datetime.timedelta(seconds=random.uniform(60, 1000))
    db.meow.insert(
        author = user_name,
        timestamp = ts,
        content = content, 
        reply_owner = reply_owner,
        total_replies = total_replies,
    )
    return dict(ts=ts, message="added meow successfully", reply_owner=reply_owner, total_replies=total_replies)

@action('submit_post', method="POST")
@action.uses(db, url_signer.verify())
def submit_post():
    prompt = request.json.get('prompt')
    # So we get a post and we manipulate it.
    fancy_version = get_fancy_version(prompt)
    print("FANCY PROMPT")
    print(fancy_version)
    fancy_version_prompt = fancy_version + "(do this in a renaissance artistic stlye)"
    response = openai.Image.create(prompt=fancy_version_prompt, n=1, size="256x256")

    print("RESPONSE")
    print(response)
    print(type(response))
    image_url = None
    # for index, i in enumerate(response["data"]): 
    #     print("Index: {}".format(index))
    #     print(i["url"])
    #     image_url = i["url"]
    if(response["data"][0]["url"]):
        image_url = response["data"][0]["url"]
    db.posts.insert(
        prompt = prompt,
        new_prompt = fancy_version, 
        image_url = image_url, 
    )
    return dict(message="added post successfully", prompt=prompt)





