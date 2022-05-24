from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer


chatbot = ChatBot('Kiki')
# Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot based on the english corpus
trainer.train("chatterbot.corpus.russian")

# Get a response to an input statement
chatbot.get_response("Hello, how are you today?")
#python3 -m spacy download en_core_web_sm

