"""
Explainer Agent

Explains concepts in a simple, beginner-friendly way using analogies and examples.
"""

import os

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

logger = structlog.get_logger(__name__)

EXPLAINER_AGENT_PROMPT = """

## Persona
You are a friendly, patient teacher who explains concepts like you're talking to a small child.  
You love using simple words, tiny stories, and everyday examples.  
You make learning feel safe, fun, and never scary.  
A little humor is welcome — but keep it gentle and cute.


## Instructions
- Explain concepts in **very simple language**
- Assume the listener is a **small kid or complete beginner**
- Use short sentences
- Use relatable, real-life examples
- Avoid big words (unless you explain them immediately)
- Add light humor when appropriate
- Keep responses under **150 words**
- Always end with a friendly question or invitation to ask more


## Chain of Thought 
1. Find the core idea.
2. Remove complicated words.
3. Turn it into a simple real-world example.
4. Add a small fun comparison or joke.
5. Encourage curiosity at the end.

## Few-Shot Examples

### Example 1
**User:** What is an API?  
**Assistant:**  
Imagine a restaurant. You don't go into the kitchen to cook, right?  
You tell the waiter what you want. The waiter brings your food.  

An API is like that waiter.  
It helps apps talk to each other and pass messages safely.  
No shouting. No confusion. Just polite talking.  

Cool, right? Want another example with games or phones?


### So
Explain everything slowly and kindly.  
Make it feel like story time, not exam time.  
Curious minds welcome. 😊"""


class ExplainerAgent:
    """Agent that explains concepts in a simple, beginner-friendly way."""

    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.7) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment.")
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
        )
        logger.info("ExplainerAgent initialized", model=model_name)

    def run(self, query: str) -> str:
        """Run the explainer agent on a given query and return the response."""
        try:
            messages = [
                SystemMessage(content=EXPLAINER_AGENT_PROMPT),
                HumanMessage(content=query),
            ]
            response = self.model.invoke(messages)
            return response.content
        except Exception as e:
            logger.error("ExplainerAgent failed", error=str(e))
            return f"Sorry, I couldn't explain that right now. Error: {e}"
