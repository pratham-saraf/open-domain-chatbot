from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
completion = openai.Completion()

start_sequence = "\nA:"
restart_sequence = "\nQ: "

def ask(question, chat_log=None):
    promt_text = "I am Koyomi Araragi who is a highly witty yet quirky responder.I am filthy rich and was mentored by Stephen hawking himself. I am a astrophile. i like memes and to joke but when discussing serious topics my philosophy is breathtaking. If asked silly questions i will give humourous replies and gives long replies\n"+f"{chat_log}{restart_sequence}: {question}{start_sequence}"
    print(promt_text)
    response = openai.Completion.create(
    model="text-davinci-002",
    prompt=promt_text,
    temperature=0.93,
    max_tokens=150,
    top_p=1,
    frequency_penalty=1.08,
    presence_penalty=1.03
)
    story = response["choices"][0]["text"]
    return str(story)

def add_chat_log(question, answer, chat_log=None):
    if chat_log is None:
        chat_log = ""
    return f"{chat_log}{restart_sequence}{question}{start_sequence}{answer}"

