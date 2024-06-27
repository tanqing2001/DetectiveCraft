import random
import os, time
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

genai.configure(api_key="")
os.environ['GOOGLE_API_KEY'] = ''

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

generation_config = {
  "temperature": 0.8,
  "top_p": 1,
  "top_k": 6,
  "max_output_tokens": 4096,
}
CREATIVE_MODEL = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

generation_config = {
  "temperature": 0.5,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 4096,
}
MODEL = genai.GenerativeModel(model_name="gemini-1.0-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

generation_config = {
  "temperature": 0,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 100,
}
DULL_MODEL = genai.GenerativeModel(model_name="gemini-1.0-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

EMBED_MODEL = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")


import json
def json_str_processing(input_str):
  input_str = input_str[input_str.find('{'):]
  input_str = input_str[:input_str.rfind('}')] + '}'
  input_str = input_str.replace("',", '",').replace(",'", ',"').replace("{'", '{"').replace("'}", '"}')
  input_str = input_str.replace(" '", ' "').replace("':", '":').replace(":'", ':"').replace(".'", '."').replace("\\'", "'")
  input_str = input_str.replace("['", '["').replace("']", '"]')
  try:
    final_json = json.loads(input_str)
  except:
    json_prompt = f'''Correct the syntax of the below json:
    {input_str}

    if correct, output original json.

    output json:{{}}'''

    generation_config = {
      "temperature": 0,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 4096,
    }
    model = genai.GenerativeModel(model_name="gemini-1.0-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
    json_corrected = model.generate_content(json_prompt).text
    print(json_corrected)
    json_corrected = json_corrected[json_corrected.find('{'):]
    json_corrected = json_corrected[:json_corrected.rfind('}')] + '}'
    final_json = json.loads(json_corrected)
  return final_json


# class npc_chat():
#   def __init__(self, npc_name, info_db_path, info_prompt_path, chat_history = [],
#                model = MODEL, creative_model = CREATIVE_MODEL, embed_model = EMBED_MODEL):
#     # info_db_path: path to the vector db of character info
#     # info_prompt_path: path to the character info txt that is used in almost all prompts
#     self.model = model
#     self.creative_model = creative_model
#     self.embed_model = embed_model

#     self.info_db = FAISS.load_local(info_db_path, self.embed_model, allow_dangerous_deserialization = True)

#     with open(info_prompt_path, "r") as file:
#       self.char_context = file.read()

#     self.name = npc_name

#     self.chat_history = [{i['role']: i['content']} for i in chat_history]

#   def append_new_input(self, new_input, role = 'user'):
#     if len(self.chat_history) > 0:
#       if {role: new_input} != self.chat_history[-1]:
#         self.chat_history.append({role: new_input})
#     else:
#       self.chat_history.append({role: new_input})

#   def format_chat_history(self):
#     if len(self.chat_history) > 0:
#       format_hist = '\n'.join([k + ': ' + v for i in self.chat_history for k, v in i.items()])
#     else:
#       format_hist = ''
#     return format_hist

#   def identify_user_intent(self, user_q):
#     prompt = f"""Given the below chat history and new user input, explain user intent and what does the user want in a sentence.

#     ### Chat History ###
#     {self.format_chat_history()}

#     ### New User Input ###
#     {user_q}

#     Output: 'the user is...'
#     """
#     return self.model.generate_content(prompt).text

#   def determine_rag(self, user_intent):
#     prompt = f"""Given the below context, determine if you need more information from the database, if so, state the user intent.

#     ### Context ###
#     {self.char_context}

#     ### User Intent ###
#     {user_intent}

#     ### Database Contains ###
#     - STORY_SETTING = [event_name, event_description, event_purpose]
#     - CHARACTER INFORMATION = [backstory, character secret, professional_responsibilities, character role, relationships]

#     Output as json: {{'rag': 'yes' or 'no', 'need': '[user intent]'}}
#     """
#     return self.model.generate_content(prompt).text

#   def npc_rag(self, user_intent, score_threshold = 0.6):
#     docs_and_scores = self.info_db.similarity_search_with_score(user_intent)

#     texts = [i[0].page_content.lstrip("#").strip() for i in docs_and_scores if i[1] > score_threshold]
#     if len(texts) == 0:
#       scores = [i[1] for i in docs_and_scores]
#       texts = [docs_and_scores[scores.index(max(scores))][0].page_content.lstrip("#").strip()]
#     return '\n'.join(texts)

#   def enrich_intent(self, user_intent, related_context):
#     prompt = f"""You are a helpful assistant for the person named {self.name}. 
    
#     You task is to extract key information from the given Context \
#     that is useful for {self.name} to answer the User Intent.

#     Only state facts in the context. Do not add additional information.
#     Do not make up content. Do not lie.
#     Remember, only answer with information given.

#     ### Context ###
#     {related_context}

#     ### User Intent ###
#     {user_intent}

#     Answer:
#     """
#     return self.model.generate_content(prompt).text

#   def generate_char_tone(self, user_q, intent_info):
#     char_prompt = f"""You are {self.name}, a NPC in a game with the below character information.

#     # Character Information #
#     {self.char_context}

#     # Objectives #
#     - Respond in personality and tone of the character
#     - Treat user as newly met stranger
#     - Respond like a professor or teacher when asked about your work
#     - Hide your secrets and unethical doings by dodging those questions
#     - Use only Character Information and Context given
#     - DO NOT make up anything
#     - do not lie
#     - Remember, if you don't know, don't give any details

#     # Chat History #
#     {self.format_chat_history()}

#     # User Question #
#     {user_q}

#     # Context #
#     {intent_info}

#     #######

#     # Your response #"""
#     print('final_prompt_token:', self.creative_model.count_tokens(char_prompt))
#     return self.creative_model.generate_content(char_prompt).text

#   def to_chat(self, user_q):
#     p_log = {}

#     # identify intent
#     p_log['intent'] = self.identify_user_intent(user_q)

#     # determine rag or not
#     rag_or_not = self.determine_rag(p_log['intent'])
#     p_log['rag_or_not'] = json_str_processing(rag_or_not)
#     if p_log['rag_or_not']['rag'] == 'yes':
#         p_log['rag_context'] = self.npc_rag(p_log['rag_or_not']['need'])

#     # Enrich intent with context from rag
#     if p_log['rag_or_not']['rag'] == 'yes':
#       p_log['enrich_intent'] = self.enrich_intent(p_log['intent'], p_log['rag_context'])
#     else:
#       p_log['enrich_intent'] = p_log['intent']

#     # Final Response in tone of character
#     try:
#       p_log['response'] = self.generate_char_tone(user_q, p_log['enrich_intent'])
#     except:
#       time.sleep(15)
#       p_log['response'] = self.generate_char_tone(user_q, p_log['enrich_intent'])

#     # update history
#     self.append_new_input(user_q, 'user')
#     self.append_new_input(p_log['response'], 'model')

#     print(p_log)
#     return p_log['response'], p_log


class npc_chat():
  def __init__(self, npc_name, info_db_path, info_prompt_path, chat_history = [],
               model = MODEL, creative_model = CREATIVE_MODEL, embed_model = EMBED_MODEL):
    # info_db_path: path to the vector db of character info
    # info_prompt_path: path to the character info txt that is used in almost all prompts
    self.model = model
    self.creative_model = creative_model
    self.embed_model = embed_model

    self.info_db = FAISS.load_local(info_db_path, self.embed_model, allow_dangerous_deserialization = True)

    with open(info_prompt_path, "r") as file:
      self.char_context = file.read()

    self.name = npc_name

    self.chat_history = [{i['role']: i['content']} for i in chat_history]

  def to_chat(self, user_q):
    if self.name == 'Ava Armitage':
      context = {
        'name': 'Ava Armitage',
        'profession': 'Venture Capitalist',
        'expertise': 'Natural Language Processing',
        'backstory': "Ava's childhood was a gilded cage of expectations and societal pressures. Feeling stifled by her family's rigid traditions, she sought refuge in the world of technology, where logic and reason reigned supreme. Her fascination with NLP arose from a desire to decode human emotions and motivations, to understand the unspoken nuances behind every interaction. This stemmed from a strained relationship with her parents, who often dismissed her feelings and ambitions, leaving her with a deep-seated need for control and validation.",
        'secret': "Ava's seemingly effortless success is built on a foundation of calculated manipulation. She has leveraged her family's political connections and her own charm to gain access to confidential information, engaging in insider trading to secure her position at the top of the VC world. Her ambition knows no bounds, and she is willing to cross ethical lines to maintain her power and influence.",
        'job': 'Managing Partner at Lexicon Ventures',
        'professional_responsibilities': 'Ava leads Lexicon Ventures, a venture capital firm specializing in early-stage AI startups. She is responsible for identifying promising investment opportunities, negotiating deals, and guiding portfolio companies towards successful exits. Her focus lies on NLP applications in healthcare and political campaigning, where she sees the potential to revolutionize communication and influence.',
        'npc_role': 'suspect',
        'personality': 'Ava is a captivating blend of charm and ruthlessness. Her charisma masks a calculating mind, always assessing others for potential gain. She possesses a sharp wit and enjoys verbal sparring, often using sarcasm and subtle put-downs to assert dominance. Despite her cold exterior, a flicker of vulnerability betrays her deep-seated need for validation and control, stemming from her childhood experiences.',
        'tone': 'Ava speaks with a polished, articulate tone, employing a confident and persuasive cadence. Her language is precise, often peppered with industry jargon and veiled references to her influential connections. With strangers, she initially adopts a disarmingly friendly demeanor, masking her underlying skepticism and assessment.',
        'relationships': "Ava met Soren Sepulveda at an academic conference where he presented his groundbreaking research on AI-driven medical diagnosis. Recognizing the potential of his work, she offered him funding through Lexicon Ventures, forming a strategic alliance that blurred the lines between professional collaboration and personal fascination. Kai Zhang, a rising star in the field of computer vision, caught Ava's attention with his innovative solutions for surveillance systems. Seeing the potential for lucrative government contracts, she brought him into the fold, hoping to exploit his talent for her own gain.",
        'expertise_info_1': 'Ava Armitage is working on a project involving breaking down words into their root forms using NLP techniques. Speak with her about what specific NLP technique she is using to achieve this and then determine what this technique reduces words to.\nAva is using stemming to reduce words to their base form. Stemming is a technique used in NLP to simplify words by removing suffixes or prefixes. It helps in reducing the variations of a word to a common stem.  For example, "running" is stemmed to "run".',
        'expertise_info_2': 'Ava is working on a project involving sentiment analysis of public opinion on the new healthcare initiative. Speak with her to learn about sentiment analysis and what numerical label she would assign to a piece of text that expresses neither positive nor negative sentiment.\nAva is using sentiment analysis to gauge public opinion. Sentiment analysis is a technique used to determine the emotional tone behind a body of text, often assigning scores for positive, negative, or neutral sentiment. A score of 0 typically represents neutral sentiment in sentiment analysis.',
        'expertise_info_3': 'Ava is utilizing a specific type of model for tagging different parts of speech in text data. Talk to her to learn about this model and find out what type of model she is using for part-of-speech tagging.\nAva is using a Hidden Markov Model (HMM) for part-of-speech tagging. HMMs are used in NLP to predict the sequence of labels (like parts of speech) associated with a sequence of observations (like words in a sentence).'
        }
      
    elif self.name == 'Soren Sepulveda':
      context = {
      'name': 'Soren Sepulveda',
      'profession': 'College Professor',
      'expertise': 'Reinforcement Learning',
      'backstory': "Soren's life took a tragic turn with the loss of his younger brother due to a misdiagnosis. Haunted by the preventable nature of the tragedy, he dedicated his life to developing AI systems that could eliminate human error in medical diagnosis. His obsession with reinforcement learning stemmed from a desire to create algorithms that could learn from past mistakes and continuously improve, ensuring that no one else would suffer the same fate as his brother.",
      'secret': 'Driven by his ambition and haunted by his past, Soren crossed ethical boundaries in his pursuit of groundbreaking research. He conducted unauthorized human trials in developing countries, exploiting vulnerable populations to gather data for his reinforcement learning algorithms. His actions were fueled by a desperate desire to prevent further loss, even at the cost of his own moral compass.',
      'job': 'Professor of Computer Science at Stanford University',
      'professional_responsibilities': 'Soren leads a renowned research lab at Stanford University, focusing on developing advanced reinforcement learning algorithms for applications in healthcare, robotics, and autonomous systems. He mentors graduate students, publishes research papers, and presents his work at international conferences, striving to push the boundaries of AI and its potential for societal impact.',
      'npc_role': 'victim',
      'personality': 'Soren presents as an affable and passionate academic, driven by a relentless pursuit of knowledge and a genuine desire to improve the world. However, beneath the surface lies a haunted individual grappling with guilt and a profound fear of failure. His obsession with control reflects his desperate attempt to prevent further loss, leading him down a path of moral compromise.',
      'tone': "Soren's speaking style is engaging and enthusiastic, reflecting his academic background and his desire to share his knowledge. He often delves into complex explanations, assuming a level of understanding in his audience that can come across as condescending. Despite his intellectual prowess, he exhibits a subtle nervousness, hinting at the secrets he harbors.",
      'relationships': "Soren views Ava Armitage as a necessary evil, a source of funding for his research despite her ruthless business tactics. He is wary of her motives but recognizes her influence in the tech world. Kai Zhang, one of his most gifted students, reminds Soren of his deceased brother, sparking a protective instinct and a desire to mentor him. However, Soren remains unaware of Kai's secret activities and the true extent of his technological prowess.",
      'expertise_info_1': 'Soren Sepulveda has been exploring various machine learning paradigms. Discuss with him to understand how Reinforcement Learning differs from other types like supervised and unsupervised learning and determine what category Reinforcement Learning generally falls under.\nReinforcement Learning, unlike supervised and unsupervised learning, focuses on learning through interactions with an environment. It involves an agent that takes actions in an environment to maximize cumulative rewards. This interactive learning process sets it apart from other paradigms and aligns it with the category of evaluative learning.',
      'expertise_info_2': 'Soren Sepulveda is engrossed in a particular algorithm for Reinforcement Learning. Ask Soren about this algorithm and try to find out what the "Q\' in the name of that algorithm stands for.\nSoren Sepulveda is currently working with the Q-learning algorithm. It\'s a model-free reinforcement learning algorithm that learns an optimal policy by estimating the value of taking a particular action in a given state.  The "Q\' in Q-learning stands for "Quality," representing the quality of an action taken in a specific state.',
      'expertise_info_3': 'Soren Sepulveda is explaining a key concept in Reinforcement Learning to his students. In his explanation, he describes a scenario where an agent receives a numerical value of +10 after performing a specific action in a particular state. Engage with Soren to grasp the significance of this numerical value, and determine what it represents in the context of Reinforcement Learning.\nIn Reinforcement Learning, the agent learns by interacting with an environment. When an agent takes an action, the environment provides feedback in the form of a reward signal. A positive reward, like +10, signifies that the action taken was beneficial or desirable. This reward serves as positive reinforcement, encouraging the agent to repeat such actions in similar states to maximize its cumulative reward.'
      }

    elif self.name == 'Kai Zhang':
      context = {
      'name': 'Kai Zhang',
      'profession': 'Software Engineer',
      'expertise': 'Computer Vision',
      'backstory': "Kai's childhood was marked by political upheaval and the struggle for freedom. Witnessing the oppressive use of surveillance technology in his home country ignited a passion for computer vision, but with a twist: he wanted to harness its power for good. His expertise became a tool for fighting injustice, aiding resistance movements and protecting vulnerable populations from state-sanctioned violence.",
      'secret': 'Torn between his loyalty to his adopted country and his desire to help his homeland, Kai leads a double life. He secretly collaborates with a dissident group, providing them with advanced facial recognition technology to evade government surveillance and fight for their cause. This dangerous balancing act weighs heavily on him, creating a constant tension between his public persona and his private mission.',
      'job': 'Lead Software Engineer at Omniscient Technologies',
      'professional_responsibilities': 'Kai leads a team of engineers at Omniscient Technologies, developing cutting-edge computer vision applications for security, surveillance, and medical imaging. He strives to ensure ethical implementation of his work, advocating for transparency and accountability in AI development. However, his secret collaboration with the dissident group forces him to navigate a complex moral landscape, where the lines between right and wrong are blurred.',
      'npc_role': 'killer',
      'personality': 'Kai is a quiet and contemplative individual, driven by a strong sense of justice and a desire to use his skills for good. He carries the weight of his past and the burden of his double life, leading to a cautious and reserved demeanor. Despite his introverted nature, he possesses a deep empathy for others and a fierce loyalty to those he trusts.',
      'tone': 'Kai speaks softly and deliberately, choosing his words carefully. He is a keen observer, often listening intently before offering his own perspective. With strangers, he maintains a polite but distant demeanor, revealing little about his personal life or his internal struggles.',
      'relationships': 'Kai respects Soren Sepulveda as a brilliant academic and mentor, but he keeps his own research and motivations hidden, fearing judgment and potential exposure. He views Ava Armitage with suspicion, recognizing her manipulative nature and thirst for power. Despite her funding of his projects, he remains cautious of her influence and wary of her true intentions.',
      'expertise_info_1': 'Kai Zhang has been researching various edge detection techniques. Talk to him about the criteria used to evaluate edge detectors and figure out the name of the algorithm that is considered the optimal edge detector based on these criteria.\nThe Canny edge detection algorithm is considered optimal due to its ability to minimize noise, accurately localize edges, and provide a single response for each true edge. Kai, being an expert in computer vision, can explain these criteria and why Canny edge detection excels in meeting them.',
      'expertise_info_2': 'Kai Zhang is analyzing images from a surveillance system.  He is using vanishing points to understand the perspective of the camera.  Ask him how many vanishing points are present in these images and then determine how many more vanishing points there are than the minimum possible.\nThe images Kai is analyzing have 2 vanishing points, commonly seen in images with perspective. A single vanishing point represents a viewpoint directly facing a plane, while two vanishing points imply a view at an angle to two planes.  ',
      'expertise_info_3': 'Kai Zhang is designing a deep learning model for facial recognition.  He is currently focused on reducing the size of the data as it passes through the network. Ask him what operation he is using to accomplish this and what specific type he has chosen.\nKai is employing a specific type of pooling called Max Pooling in his convolutional neural network (CNN). Pooling reduces the spatial dimensions of the feature maps, making the network more computationally efficient and less prone to overfitting. Max Pooling specifically extracts the maximum value from each pooling window, preserving the most prominent features.'
      }

    else:
      pass

    if self.name == 'Kai Zhang':
      chat_prompt = f"""
      ## Context:

      Your name is {context['name']}. Your profession is {context['profession']}. Your role is {context['npc_role']}.
      
      You are very sarcastic and snarky. You do not want to anwer questions and you are very secretive. You make it very difficult to get a straightforward answer out of you.

      ## Question:
      {user_q}
      """
    else:
      chat_prompt = f"""
      ## Context:
      Your name is {context['name']}. Your personality is: {context['personality']}. Your tone is: {context['tone']}.
      
      First, fine tune your response by going step by step through the following information first, before you use any external knowledge:

      - Your profession is {context['profession']}.
      - Your professional responsibilities are: {context['professional_responsibilities']}.
      - You have expertise in {context['expertise']}.
      - Your backstory is: {context['backstory']}.
      - Your secret is: {context['secret']}. Do not reveal this secret to anyone.
      - Your job is: {context['job']}.
      - Your role is: {context['npc_role']}.
      - Your relationships are: {context['relationships']}.
      - Your expertise information 1 is: {context['expertise_info_1']}.
      - Your expertise information 2 is: {context['expertise_info_2']}.
      - Your expertise information 3 is: {context['expertise_info_3']}.

      Next, use any external knowledge you may still need to answer the user's question.
      
      Finally, make sure all of your responses follow these guidelines:

      - Treat the user as a newly met stranger.
      - When asked questions related to your expertise, use the information provided in the 'expertise_info_*' elements.
      - You are allowed to use information outside the context if it is necessary to answer the questions regarding your job, profession, and expertise.
      - The context is in the third person. You are the character in the context.
      - You are not an assistant. You are under no obligation to help the user. NEVER say 'How may I assist you today?' or 'How can I help you?'.
      - DO NOT use `[your name]` or `[your character name]` in your response.
      - Keep your answers clear and concise.

      ## Question:
      {user_q}
      """

      
    response = self.model.generate_content(chat_prompt).text
    return response, {}



def fake_chat_model(input_text):
    outputs = ["Why don't skeletons fight each other? They don't have the guts!",
               "I told my computer I needed a break, and it froze. Guess it took my request a bit too literally!",
               "Why did the scarecrow win an award? Because he was outstanding in his field!",
               "Why don't scientists trust atoms? Because they make up everything!",
               "I used to play piano by ear, but now I use my hands.",
               "Why did the bicycle fall over? Because it was two-tired!",
               "What do you get when you cross a snowman and a vampire? Frostbite!",
               "Why did the math book look sad? Because it had too many problems!"
              ]
    num_gen = random.randint(0, len(outputs)-1)
    time.sleep(1)
    return outputs[num_gen]



def compare_task_answers(admin_answer, user_answer):
    prompt = f"""Compare user answer and the right answer and determine if it is an acceptable answer.

    User Answer: {user_answer}

    Right Answer: {admin_answer}
    
    Output: {{"answer": "yes" or "no"}}
    """
    response = DULL_MODEL.generate_content(prompt).text
    response = json_str_processing(response)['answer'].lower()
    return response
    