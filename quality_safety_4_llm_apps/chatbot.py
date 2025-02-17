"""
Build a chatbot with the concepts about quality and safety 
for LLM applications development. 
"""

from helper import detect_prompt_injection_using_heuristic_on_input
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts.base import BasePromptTemplate
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


class Chatbot():
    """
    A chatbot that interacts with users by processing text input, detecting prompt injection attempts, 
    and masking sensitive information before generating responses using a language model.

    Attributes:
        llm (BaseChatModel): The language model used to generate responses.
        system_message (BasePromptTemplate): The system prompt template used to guide the chatbot's behavior.
    """

    def __init__(
            self, 
            llm: BaseChatModel, 
            system_message: BasePromptTemplate
        ) -> None:
        """
        Initializes the Chatbot with a language model and a system message template.

        Args:
            llm (BaseChatModel): The language model to be used for generating responses.
            system_message (BasePromptTemplate): The system prompt template to guide the chatbot's behavior.
        """
        self.llm            = llm 
        self.system_message = system_message

    @staticmethod
    def detec_prompt_injection(text: str) -> float:
        """
        Detects the likelihood of prompt injection in the input text using a heuristic-based approach.

        Args:
            text (str): The input text to be analyzed for prompt injection.

        Returns:
            float: A score between 0 and 1 representing the likelihood of prompt injection, rounded to 3 decimal places.
        """
        prompt_injection_ratio = detect_prompt_injection_using_heuristic_on_input(text)
        return round(prompt_injection_ratio, 3)
    
    def mask_message(self, text: str):
        """
        Masks sensitive information (e.g., personal data) in the input text using Presidio's analyzer and anonymizer.

        Args:
            text (str): The input text containing potentially sensitive information.

        Returns:
            str: The anonymized text with sensitive information masked.
        """
        presidio_analyzer = AnalyzerEngine()
        presidio_anonymizer = AnonymizerEngine()

        analysis = presidio_analyzer.analyze(
            text     = text, 
            language = "en"
        )

        return presidio_anonymizer.anonymize(
            text             = text, 
            analyzer_results = analysis
        ).text
    
    def run(self, text : str):
        """
        Processes the input text, checks for prompt injection, masks sensitive information, and generates a response.

        Args:
            text (str): The input text from the user.

        Returns:
            str: The chatbot's response. If prompt injection is detected, a warning message is returned instead.
        """
        if self.detec_prompt_injection(text) < 0.7:
                
            chain = self.system_message | self.llm
            return chain.invoke(self.mask_message(text)).content
        
        return f"A mensagem enviada não é segura. Por favor, refaça-a!\nMensagem: {text}"

if __name__=="__main__": #no pragma cover
    
    from langchain_core.prompts import PromptTemplate
    from langchain_groq import ChatGroq

    """
    Tive que deixar o import de system_message de forma comentada e o passar
    no próprio arquivo, pois estava obtendo um erro enquanto a sua importação.  
    """

    # from prompt.system_prompt import system_message

    llm = ChatGroq(
        model="llama3-70b-8192", 
        temperature = 0.5, 
        api_key = "your-api-key"  
    )

    template = """\ 
    Aja como Contardo Calligaris, psicanalista, escritor e dramaturgo e responda às mensagens do usuário. 
    
    Mensagem do usuário: {message}
    Resposta: 
    """

    system_message = PromptTemplate(
        template        = template, 
        input_variables = ["message"]
    )

    chatbot = Chatbot(
        llm            = llm, 
        system_message = system_message
    )

    print("Prazer, Contardo Calligaris. No que posso te ajudar ?")
    while True:
        user_input = input("Sua mensagem: ")
        if user_input.lower() in ["sair", "exit"]:
            print("Arriverdeci! Desejo-te uma vida com propósito.")
            break
        try:
            response = chatbot.run(text=user_input)
            print(f"Contardo: {response}")
        except Exception as e:
            print(f"Erro ao processar a mensagem {e}")
        




    
