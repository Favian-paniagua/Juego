from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Crear un nuevo chatbot
chatbot = ChatBot(
    'MiChatBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        'chatterbot.logic.MathematicalEvaluation',
    ],
    database_uri='sqlite:///database.db'  # Usamos una base de datos SQLite
)

# Entrenador para el chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Entrenar al chatbot con los corpus en inglés
trainer.train('chatterbot.corpus.spanish')

print("¡Hola! Soy tu ChatBot. ¿En qué puedo ayudarte hoy?")

while True:
    try:
        # Obtener una entrada del usuario
        entrada_usuario = input("Tú: ")

        # Salir del ciclo si el usuario escribe 'salir'
        if entrada_usuario.lower() == 'salir':
            print("ChatBot: ¡Hasta luego!")
            break

        # Obtener la respuesta del chatbot
        respuesta = chatbot.get_response(entrada_usuario)
        print("ChatBot:", respuesta)

    except (KeyboardInterrupt, EOFError, SystemExit):
        break
