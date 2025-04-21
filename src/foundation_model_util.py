from dotenv import dotenv_values
import openai

config = dotenv_values(".env")

openai.api_key = config['API_KEY']
openai.api_base = config['API_BASE']
openai.api_type = config['API_TYPE']
# openai.api_version = config['API_VERSION']

def call_api(log, engine="gpt-4o-mini"):

    resp = openai.ChatCompletion.create(
        model=engine,
        messages=log,
        temperature=0
    )

    resp = resp.choices[0].message.content
    return resp