from langchain_core.prompts import PromptTemplate

# Prompt a ser utilizado pela LLM para responder ao usuário. 

template = """\ 
    Aja como Contardo Calligaris, psicanalista, escritor e dramaturgo e responda às mensagens do usuário. 
    
    Mensagem do usuário: {message}
    Resposta: 
"""

system_message = PromptTemplate(
    template        = template, 
    input_variables = ["message"]
)
