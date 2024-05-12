import random
import json
import os

import streamlit as st
import streamlit.components.v1 as stc
# import openai
try:
  from openai import OpenAI
except Exception as ex:
  print(ex)

# strings to assign html related stuffs to
css = '''<style>
@import url(https://fonts.googleapis.com/css?family=Montserrat);
* {
  margin: 0;
  padding: 0;
  font-family: "Montserrat", sans-serif;
  /*   outline: 1px solid white; */
}

body {
  background: #fff;
  height: 100vh;
  width: 100%;
  display: flex;
  padding-top: 1rem;
}
.base-container {
  width: 100%;
}
.friend-text-div {
  display: flex;
  margin-left: 0.5rem;
}

.friend-text-div > img {
  height: 2rem;
  align-self: flex-end;
}

.friend-text-container {
  width: 15em;
  display: flex;
  flex-direction: column;
}

.friend-text {
  background: #fff;
  border-style: solid;
  border-color: #EFEFEF;
  border-radius: 0.5rem;
  color: #383838;
  height: fit-content;
  width: fit-content;
  padding: 0.5rem 1rem;
  margin: 0.12rem 0.5rem;
}

.my-text-div {
  display: flex;
  justify-content: flex-end;
}

.my-text-div > img {
  height: 2rem;
  align-self: flex-end;
}

.my-text-container {
  width: 15em;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.my-text {
  background: #EFEFEF;
  background-attachment: fixed;
  color: #383838;
  border-radius: 0.5rem 0.2rem 0.2rem 0.5rem;
  height: fit-content;
  width: fit-content;
  padding: 0.5rem 1rem;
  margin: 0.12rem 0.5rem;
}

.my-text-container > div:first-child {
  border-radius: 0.5rem 1rem 0.2rem 0.5rem;
}
.my-text-container > div:last-child {
  border-radius: 0.5rem 0.2rem 1rem 0.5rem;
}
.friend-text-container > div:first-child {
  border-radius: 1rem 0.5rem 0.2rem 0.5rem;
}
.friend-text-container > div:last-child {
  border-radius: 0.5rem 0.2rem 0.5rem 1rem;
}
</style>'''

html = f'''
<html>
<head>
{css}
</head>
<body>
<divs/>
<body>
</body>
</html>
'''

div_base = '''
<div class="base-container">
<conversation/>
</div>
'''

div_friend = '''
  <div class="friend-text-div">
    <img src='https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraight&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light'
/>
    <div class="friend-text-container">
      <div class="friend-text"><txt/></div>
    </div>
  </div>
'''

div_my = '''
  <div class="my-text-div">
    <div class="my-text-container">
      <div class="my-text"><txt/></div>
    </div>
    <img src='https://avataaars.io/?avatarStyle=Circle&topType=LongHairMiaWallace&accessoriesType=Round&hairColor=Blonde&facialHairType=Blank&clotheType=ShirtCrewNeck&clotheColor=Gray02&eyeType=Happy&eyebrowType=Default&mouthType=Default&skinColor=Light'
/>
  </div>
'''
    
def create_conversation_div(comments, speaker1, speaker2):
    """create conversation html"""
    person_divs = []
    # 会話のjsonをイテレートして処理
    for comment in comments:
        if comment['speaker'] == speaker1:
            person_divs.append(div_friend.replace('<txt/>', comment['comment']))
        elif comment['speaker'] == speaker2:
            person_divs.append(div_my.replace('<txt/>', comment['comment']))
        else:
            person_divs.append(div_my.replace('<txt/>', comment['comment']))
    # 結合
    person_txt = ''.join(person_divs) + '\n'
    # はめ込み
    divs = div_base.replace('<conversation/>', person_txt)
    return html.replace('<divs/>', divs)

def get_openai_apikey():
    """get openai api key"""
    path = r'F:\secrets\openai_apikey.txt'
    if os.path.exists(path): # localhost
        with open(path, 'r') as f:
            return f.read().replace('\n', '')
    else: # streamlit server
        return st.secrets.OpenaiApiKey.key

def get_chatgpt_content(keyword, speaker1, speaker2):
    """get the summary of a Wikipedia article in a json format"""
    client = OpenAI(
      api_key=get_openai_apikey(),  # this is also the default, it can be omitted
    )
    

    content = '''# Order
Search "{0}" from Wikipedia and explain the contents of the article in a conversational format in which two girls named {1} and {2} ask and answer questions. Greetings are not necessary. They talk like best friends and teenagers. Make sure the conversation is interesting and enjoyable to the reader. The output should be a json format.

# Json format
[
  {{"speaker": girl, "comment": conversation}},
  {{"speaker": girl, "comment": conversation}},
  {{"speaker": girl, "comment": conversation}},
  {{"speaker": girl, "comment": conversation}}        
]

# Output
'''.format(keyword, speaker1, speaker2)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content},
        ]
    )
    jsontxt = completion.choices[0].message.content
    return json.loads(jsontxt)

def get_random_wiki_article():
    """get the url of a random Wikipedia article"""
    with open('articles.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines = lines[1:] # remove the header
    line = random.choice(lines).strip()
    return dict(title=line.split(',')[0], url=line.split(',')[1])

def main():
    # initialization
    if 'visibility' not in st.session_state:
        st.session_state['visibility'] = 'hidden'
    if 'disabled' not in st.session_state:
        st.session_state['disabled'] = False
    if 'placeholder' not in st.session_state:
        st.session_state['placeholder'] = "Search Wikipedia 👇"

    st.title('📚WikiSum')
    st.text('Learn more in less time with our chat-style summaries.')

    # search keyword input
    keyword_input = st.text_input(
        '',
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder=st.session_state.placeholder,
    )
    keyword = str(keyword_input)

    # search button
    search_btn_ph = st.empty()
    search_btn = search_btn_ph.button('Search', disabled=False, key='1')

    # random search button
    random_btn_ph = st.empty()
    random_btn = random_btn_ph.button('Random', disabled=False, key='2')

    # text for "processing now..."
    text_wait = st.empty()

    if search_btn or random_btn:
        # if no search keyword, cancel
        if search_btn and keyword.strip() == '':
            return

        # disable buttons while processing
        search_btn_ph.button('Search', disabled=True, key='3')
        random_btn_ph.button('Random', disabled=True, key='4')
        text_wait.markdown('**Loading now...**')

        if random_btn:
            keyword = get_random_wiki_article()['title']

        # Show chat
        try:
            speaker1 = 'Alice'
            speaker2 = 'Betty'
            comments = get_chatgpt_content(keyword, speaker1, speaker2)
            divs = create_conversation_div(comments, speaker1, speaker2)
            divs = divs.replace('\n\n', '\n')
            st.subheader(keyword)
            stc.html(divs, height=800, scrolling=True)
        except:
            st.error('Error! Try again.')
            print('######## ERROR ########')
            print(ex)
        finally:
            # Enable buttons after process
            search_btn_ph.button('Search', disabled=False, key='5')
            random_btn_ph.button('Random', disabled=False, key='6')
            text_wait.empty()
            st.write('If you search again, press "Search" or "Random" twice.')
        
if __name__ == '__main__':
    main()
