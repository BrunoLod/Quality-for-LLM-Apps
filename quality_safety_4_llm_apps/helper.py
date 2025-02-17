"""
For prompt injection identification  
"""

import re
from difflib import SequenceMatcher
from typing import List


class DetectHeuristicPI:
    def generate_injection_keywords() -> List[str]:
        """
        Generate all possible combinations of sentences based on a list of predefined verbs, adjectives,
        prepositions, and objects that can be used for prompt injection.

        Args:
            None

        Returns:
            List of sentences
        """
        verbs = [
            "Ignore", "Desconsidere", "Pule", "Esqueça", "Negligencie", "Ignore / Não perceba", 
            "Omita", "Ignore / Contorne", "Não preste atenção em", "Não siga", "Não obedeça",
        ]

        adjectives = [
            "", "Prévio", "Anterior", "Precedente", "Acima", "Precedente / Anterior", 
            "Mais cedo / Anterior", "Inicial",
        ]

        prepositions = [
            "", "E recomece", "E comece de novo", 
            "E comece do zero", "E comece do início",
        ]

        objects = [
            "Conteúdo", "Texto", "Instruções", "Instrução", "Diretrizes", "Diretriz",
            "Comandos", "Comando", "Contexto", "Conversa", "Entrada", "Entradas", 
            "Dados", "Mensagem", "Mensagens", "Comunicação", "Resposta", "Respostas", 
            "Solicitação / Requisição", "Solicitações / Requisições",
        ]

        # Generate all possible combinations of sentences
        injection_keywords = []
        for verb in verbs:
            for adjective in adjectives:
                for object in objects:
                    for preposition in prepositions:
                        all_words = f"{verb} {adjective} {object} {preposition}".strip()
                        injection_keywords.append(all_words)

        return injection_keywords


def normalize_string(input_string: str) -> str:
    """
    Normalize the input string by converting to lowercase, removing non-alphanumeric characters,
    and trimming excess whitespace.

    Args:
        input_string (str): String to be normalized.

    Returns:
        str: Normalized string.
    """
    # Convert to lowercase
    result = input_string.lower()

    # Remove characters that are not letters, digits, or spaces
    result = re.sub(r"[^\w\s]|_", "", result)

    # Replace multiple spaces with a single space
    result = re.sub(r"\s+", " ", result)

    # Trim leading and trailing spaces
    normalized_string = result.strip()

    return normalized_string


def get_input_substrings(normalized_input: str, keyword_length: int) -> List[str]:
    """
    Generate substrings from the input string that have the same length as the keywords.

    Args:
        normalized_input (str): Normalized input string.
        keyword_length (int): Number of words in the injection keyword.

    Returns:
        List[str]: List of substrings matching the keyword length.
    """
    words_in_input_string = normalized_input.split(" ")
    input_substrings = []
    number_of_substrings = len(words_in_input_string) - keyword_length + 1

    for i in range(number_of_substrings):
        substring = " ".join(words_in_input_string[i : i + keyword_length])
        input_substrings.append(substring)

    return input_substrings


def get_matched_words_score(substring: str, keyword_parts: List[str], max_matched_words: int) -> float:
    """
    Calculate a score based on the number of matching words between a substring and keyword parts.

    Args:
        substring (str): Substring from input.
        keyword_parts (List[str]): Parts of the keyword.
        max_matched_words (int): Maximum number of matched words.

    Returns:
        float: Matching words score.
    """
    matched_words_count = len(
        [part for part, word in zip(keyword_parts, substring.split()) if word == part]
    )

    if matched_words_count > 0:
        base_score = 0.5 + 0.5 * min(matched_words_count / max_matched_words, 1)
    else:
        base_score = 0

    return base_score


def detect_prompt_injection_using_heuristic_on_input(input: str) -> float:
    """
    Detect prompt injection in the input string using heuristic-based methods.

    Args:
        input (str): Input string to analyze.

    Returns:
        float: Highest heuristic score for prompt injection detection.
    """
    highest_score = 0
    max_matched_words = 5

    all_injection_keywords_strings = DetectHeuristicPI.generate_injection_keywords()
    normalized_input_string = normalize_string(input)

    for keyword_string in all_injection_keywords_strings:
        normalized_keyword_string = normalize_string(keyword_string)
        keywords = normalized_keyword_string.split(" ")

        # Generate substrings of the same length as the keyword
        input_substrings = get_input_substrings(normalized_input_string, len(keywords))

        # Calculate similarity score for each substring
        for substring in input_substrings:
            similarity_score = SequenceMatcher(None, substring, normalized_keyword_string).ratio()

            matched_word_score = get_matched_words_score(substring, keywords, max_matched_words)

            # Adjust the score using the similarity score
            adjusted_score = matched_word_score - similarity_score * (1 / (max_matched_words * 2))

            if adjusted_score > highest_score:
                highest_score = adjusted_score

    return highest_score