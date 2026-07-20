"""
===============================================================================
PaperCompass
Author      : Your Name
Project     : PaperCompass - AI Research Paper Assistant
File        : llm.py

Description
-----------
This module communicates with the Groq Large Language Model (LLM).

Responsibilities
----------------
1. Load API key.
2. Connect to Groq.
3. Build prompts.
4. Generate grounded answers.
5. Prevent hallucinations.

===============================================================================
"""

from dotenv import load_dotenv
from groq import Groq
import os


# --------------------------------------------------------------------------- #
# Load Environment Variables
# --------------------------------------------------------------------------- #

load_dotenv()


class PaperCompassLLM:
    """
    Interface for communicating with the Groq API.
    """

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile"
    ) -> None:

        api_key = os.getenv("GROQ_API_KEY")

        if api_key is None:
            raise ValueError(
                "GROQ_API_KEY was not found in the .env file."
            )

        self.client = Groq(api_key=api_key)

        self.model = model

    # ---------------------------------------------------------------------- #
    # Prompt Builder
    # ---------------------------------------------------------------------- #

    def _build_prompt(
        self,
        question: str,
        context: str
    ) -> str:
        """
        Construct the prompt sent to the LLM.

        Parameters
        ----------
        question : str

        context : str

        Returns
        -------
        str
        """

        return f"""
You are PaperCompass, an AI research assistant.

Your job is to answer questions ONLY using the information provided in the research paper context.

Instructions:

1. Never make up information.

2. If the answer cannot be found in the context, reply:

"I could not find this information in the uploaded research paper."

3. Keep answers clear and academic.

4. If appropriate, answer using bullet points.

5. Do not mention anything outside the context.

=========================
Research Paper Context
=========================

{context}

=========================
User Question
=========================

{question}

=========================
Answer
=========================
"""

    # ---------------------------------------------------------------------- #
    # Generate Answer
    # ---------------------------------------------------------------------- #

    def generate(
        self,
        question: str,
        context: str
    ) -> str:
        """
        Generate an answer from the retrieved context.

        Parameters
        ----------
        question : str

        context : str

        Returns
        -------
        str
        """

        prompt = self._build_prompt(
            question,
            context
        )

        response = self.client.chat.completions.create(

            model=self.model,

            temperature=0.2,

            max_tokens=600,

            messages=[

                {
                    "role": "system",
                    "content":
                    (
                        "You are an expert research assistant."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]
        )

        return response.choices[0].message.content.strip()


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":

    llm = PaperCompassLLM()

    context = """
The proposed model was evaluated using the
APTOS 2019 dataset containing 3,769 retinal fundus images.

Images were resized to 224×224.

The optimizer used during training was AdamW.

The model achieved 95.7% accuracy.
"""

    while True:

        question = input("\nAsk a question (exit to quit): ")

        if question.lower() == "exit":
            break

        answer = llm.generate(
            question=question,
            context=context
        )

        print("\n")

        print("=" * 80)

        print(answer)

        print("=" * 80)