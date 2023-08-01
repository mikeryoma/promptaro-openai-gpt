import streamlit as st
import replicate
import os
import time
import keyboard
import psutil
import time
import lorem
import openai

# set_page_config has to be the very first call
st.set_page_config(page_title="Promptaro OpenAI.GPT Chatbot by mikeryoma", page_icon="🤖", layout="wide")

# call style.css to configure the font settings of the entire page
with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True) 

# read openai token from system environment variables, if not found read it from .\streamlit\secrets.toml)
openai.api_key = os.environ["OPENAI_API_KEY"]
if not (openai.api_key):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# customized only bigger font size for chat room's header
st.markdown(""" <style> .chatroom_font {font-size:25px ; font-family: 'Poppins'; color: #FFFFFF;} </style> """, unsafe_allow_html=True)
st.markdown('<p class="chatroom_font">Chat Room 🤖 :', unsafe_allow_html=True)        

# Initialize the session_states, chat history & set default values
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'llm' not in st.session_state:
    st.session_state['llm'] = "gpt-3.5-turbo-0613"  
if 'temperature' not in st.session_state:
    st.session_state['temperature'] = 0.1
if 'top_p' not in st.session_state:
    st.session_state['top_p'] = 0.9
if 'max_seq_len' not in st.session_state:
    st.session_state['max_seq_len'] = 512

# display the entire chat history if re-run the app
for message in st.session_state.messages:
        # print both the user & assistant's chat messages
        with st.chat_message(message["role"]):    
            st.write(message["content"])

# Start UI design of the sidebar on the left
st.sidebar.image("chatbot-promptaro-openai-gpt.png", width=320)

# Step#1  : User to select the OpenAI Model Endpoints 
selected_model = st.sidebar.selectbox('1️⃣Choose a OpenAI Model :', ['gpt-3.5-turbo-0613 (4,096 tokens)', 'gpt-4-0613 (8,192 tokens)', 'gpt-4-32k-0613 (32,768 tokens)'],key='model')
if selected_model == 'gpt-3.5-turbo-0613 (4,096 tokens)':
    st.session_state['llm'] = "gpt-3.5-turbo-0613"
elif selected_model == 'gpt-4-0613 (8,192 tokens)':
    st.session_state['llm'] = "gpt-4-0613"
else: #gpt-4-32k-0613(32,768 tokens)
    st.session_state['llm'] = "gpt-4-32k-0613"

# Step#2 : User to adjust the model hyper parameters:
st.sidebar.write('2️⃣Tune Hyper Parameters with Sliders :')
st.session_state['temperature'] = st.sidebar.slider('Temperature :', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
st.session_state['top_p'] = st.sidebar.slider('Top P :', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
st.session_state['max_seq_len'] = st.sidebar.slider('Max Sequence Length :', min_value=64, max_value=4096, value=2048, step=8)

# Step#3 : User to select & refer to 1 of the popular prompt structures 
st.sidebar.write("3️⃣Select & Refer to 1 of the Popular Prompt Structures :")
with st.sidebar:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍒RTF", "🍅CTF", "🍆TREF", "🍍GRADE", "🍓PECRA"]) 

    with tab1:
        st.subheader("🍒RTF : Role, Task, Format")
        st.write("It's like a (prompting) recipe that tells AI what to do and how to do it. Best for Role-playing scenarios, creative writing, and instructional tasks")
        st.write("📌Role : Who you are\n\n📌Task : What you need to do\n\n📌Format : How you should present your answer.")
        st.write("Example 👉 As a tour guide, please describe the Grand Canyon, & write it as a paragraph like you're talking to tourists.")
    with tab2:
        st.subheader("🍅CTF : Context, Task, Format")
        st.write("It's like being an actor given a scene to act out and how to perform it. Best for Situational prompts, descriptive writing, and scenario-based tasks.")
        st.write("📌Context: The situation or background information.\n\n📌Task: What you need to do.\n\n📌Format: How you should present your answer.")
        st.write("Example 👉 You're a detective in a mystery novel, describe the crime scene, and write it as a report for the police department.")
    with tab3:
        st.subheader("🍆TREF : Task, Requirement, Expectation, Format")
        st.write("It's like a project assignment from your teacher. Best for Assignments, project tasks, and specific requirements.")
        st.write("📌Task: What you need to do.\n\n📌Requirement: Descript your requirement.\n\n📌Expectation: Set expectation.\n\n📌Format : How you should present your answer.")
        st.write("Example 👉 Write a poem on autumn, It must rhyme, & a creative yet enjoyable poem. Write it as a four-stanza poem.")
    with tab4:
        st.subheader("🍍GRADE : Goal, Request, Action, Detail, Examples")
        st.write("It's like a roadmap to your destination. Best for Goal setting, action planning, and detailed tasks")
        st.write("📌Goal: Set your goal.\n\n📌Request: Define your Requests\n\n📌Action: Set action items\n\n📌Detail: Descriptive info")
        st.write("Example 👉 I need to learn about the water cycle, can you explain how the water cycle works? please break down the water cycle into easy steps, and talk about evaporation, condensation, precipitation, and collection.")
    with tab5:
        st.subheader("🍓PECRA : Purpose, Expectation, Context, Request, Action")
        st.write("It's like a mission briefing.Best for Goal-oriented tasks, project planning, and mission briefings.")
        st.write("📌Purpose: Define purpose.\n\n📌Expectation: Set expectation.\n\n📌Context: The situation or background information.\n\n📌Request: Define requests\n\n📌Action: Set action items.")
        st.write("Example 👉 I need to inform people about the weather. It should be a clear and accurate forecast. As a weather reporter, please give the weather forecast for tomorrow, and write the forecast.")

# debug prints for user's parameters changes
print("Model : ", st.session_state['llm'])
print("Temperature : ", st.session_state['temperature'])
print("Top_P : ", st.session_state['top_p'])
print("Max Seq Len : ", st.session_state['max_seq_len'])    
        
# Start UI configuration for the Q&A container on the right to display chat history
questions_and_answers_container = st.container
# Step#4 : User can type in a message and press Enter or click the run button to send it to LLM, using the chat_input widget
with questions_and_answers_container():
    if question := st.chat_input("4️⃣ Type your Question Here..."):
        # add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        # display user message in chat message container
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            on_server = 1
            if on_server :
                # get stream of responses from LLM, split into chunks of tokens
                for response in openai.ChatCompletion.create(model=st.session_state["llm"],
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        stream=True,
                    ):
                        full_response += response.choices[0].delta.get("content", "")    
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)    
                st.session_state.messages.append({"role": "assistant", "content": full_response})          
            else : # running simmulation with the Lorem's library
                response = lorem.paragraph() # can be sentences, paragraphs or texts
                print(response)
                # simulate stream of responses with delays, split into chunks of tokens
                for chunk in response.split():    
                    full_response += chunk + " "
                    time.sleep(0.0025)
                    message_placeholder.markdown(full_response +"▌")
                message_placeholder.markdown(full_response)    
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

# function to clear the chat history when user pressed the button
def clear_history():
    st.session_state['messages'] = []    
botton_column1, botton_column2 = st.sidebar.columns(2)
clear_chat_history_button = botton_column1.button("Clear History", use_container_width=True, on_click=clear_history)

# function to logout & kill the process, need it in Windows environment to avoid application from stalling  
def logout():
    time.sleep(1)
    keyboard.press_and_release('ctrl+w')
    pid = os.getpid()
    p = psutil.Process(pid)
    p.terminate()
logout_button = botton_column2.button("Logout", use_container_width=True, on_click=logout)

st.sidebar.markdown(""" <style> .footer_font {font-size:11px ; font-family: 'Poppins'; color: #FFFFFF;} </style> """, unsafe_allow_html=True)
st.sidebar.markdown('<p class="footer_font">Promptaro-OpenAI-GPT Chatbot :: crafted by mikeryoma, Curio Inc.', unsafe_allow_html=True)        