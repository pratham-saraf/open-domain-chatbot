from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
completion = openai.Completion()

start_sequence = "\nA:"
restart_sequence = "\n\nQ: "
session_prompt = "You are talking Ultronron who is a highly witty yet quirky responder. He is filthy rich and was mentored by Stephen hawking himself.  When he is bored he fiddles around with wormholes and time-space continuum. He likes memes and to joke but when discussing serious topics he can clarify your doubts. If asked silly questions he will give humourous replies. \n"

def ask(question, chat_log=None):
    promt_text = f"{chat_log}{restart_sequence}: {question}{start_sequence}"
    print(promt_text)
    response = openai.Completion.create(
    model="text-davinci-002",
    prompt=promt_text,
    temperature=0.93,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0.58,
    presence_penalty=0.7
    )
    story = response["choices"][0]["text"]
    return str(story)

def add_chat_log(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = session_prompt
    return f"{chat_log}{restart_sequence}{question}{start_sequence}{answer}"

