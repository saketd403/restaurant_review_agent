import os
import json
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

def get_access_token(var):

    access_token=None

    try:

        with open("token.json", "r") as token_file:
            config = json.load(token_file)
            access_token = config[var]

    except Exception as e:

        print(f"Unable to obtain access token")
        raise

    return access_token

def set_env(var):

    access_token = get_access_token(var)
    if access_token:
        os.environ[var] = access_token

def get_restaurant_info():

    menu_file = "menu.json"
    restaurant_file = "restaurant_details.json"

    restaurant_info = ""

    