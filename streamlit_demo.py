# Jeeves is back, and this time he's playing for keeps
import streamlit as st
from streamlit_chat import message as st_message
import streamlit.components.v1 as components
import random
import string

from qa.bot import GroundedQaBot

source_url = ''
iframe = None
source_display = None


### CHAT UPDATED HERE
def getReply():
    user_message = st.session_state.input_text
    history = []
    for chat in st.session_state['history']:
        name = "user" if chat['is_user'] else "bot"
        history.append(f"{name}: {chat['message']}")
    bot.set_chat_history(history)
    reply = bot.answer(user_message,
                       verbosity=2,
                       n_paragraphs=2,
                       model=st.session_state.model,
                       url=st.session_state.url)
    print(reply)
    reply, sources = reply.split("Source:")
    with col2:
        st.subheader("sources")
        st.markdown(sources)

    st.session_state.input_text = ''
    st.session_state.history.append({"message": user_message, "is_user": True, "avatar_style": "gridy"})
    st.session_state.history.append({"message": reply, "is_user": False})


if __name__ == "__main__":
    print("new bot")
    bot = GroundedQaBot(st.secrets["cohere_api_token"], st.secrets["serp_api_token"])

    st.set_page_config(layout="wide")

    ### CHAT HISTORY SETUP
    if "history" not in st.session_state:
        st.session_state.history = []

    ### MAIN PAGE LAYOUT
    col1, col2 = st.columns(2)
    with st.sidebar:
        st.title("Grounded Question Answering")
        st.markdown('This is a Cohere API / Serp API powered contextualized factual question answering bot!')
        #used for any extra settings
        with st.expander("Advanced Settings"):
            st.text_input("Restrict replies to domain:", key="url", placeholder="Ex: shopify.com")
            st.selectbox('Model:', ('xlarge', 'command-xlarge-20221108'), key="model")

    #chat
    with col1:
        for chat in st.session_state['history']:
            # call random.choices() string module to find the string in Uppercase + numeric data.
            ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            st_message(**chat, key=ran)  # laying out messages
        st.text_input("",
                      key="input_text",
                      on_change=getReply,
                      placeholder="Ask me a question...like 'how far away is the moon'")
