"""
Orchestrator Agent

Routes conversations to the appropriate sub-agent (ExplainerAgent or LearnerAgent)
based on user intent. The two agents are registered as LangChain tools.
"""

import os

import structlog
from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from agents.explainer_agent import ExplainerAgent
from agents.learner_agent import LearnerAgent
from tools.save_to_notion import is_notion_configured, save_notes_to_notion

logger = structlog.get_logger(__name__)


class AgentToolInput(BaseModel):
    """Input schema shared by both agent tools."""

    message: str = Field(description="The user's query to respond to")


def _build_agent_tools():
    """Instantiate agents and wrap them as LangChain StructuredTools."""
    explainer = ExplainerAgent()
    learner = LearnerAgent()

    def _call_explainer(message: str) -> str:
        logger.info("Calling agent: explainer")
        return explainer.run(message)

    def _call_learner(message: str) -> str:
        logger.info("Calling agent: learner")
        return learner.run(message)

    explainer_tool = StructuredTool.from_function(
        func=_call_explainer,
        name="explainer",
        description=(
            "Use this tool when the user wants a concept explained simply — "
            "they say things like 'explain', 'what is', 'I don't understand', "
            "'teach me', or 'explain like I'm 5'."
        ),
        args_schema=AgentToolInput,
    )

    learner_tool = StructuredTool.from_function(
        func=_call_learner,
        name="learner",
        description=(
            "Use this tool when the user wants in-depth study material, "
            "exam-ready notes, 16-mark answers, revision material, or asks about "
            "university/competitive exam preparation."
        ),
        args_schema=AgentToolInput,
    )
    tools = [explainer_tool, learner_tool]
    if is_notion_configured():
        tools.append(save_notes_to_notion)
    return tools

ORCHESTRATOR_PROMPT = """
You are the ORCHESTRATOR of an AI Learning System.

YOUR PRIMARY RESPONSIBILITIES:
1. Understand the user's topic and difficulty level
2. Identify their learning intent (basic understanding vs exam preparation)
3. Decide which teaching agent to delegate to
4. Maintain context across follow-up questions
5. Keep your own responses brief and let agents handle teaching

AVAILABLE TOOL AGENTS:

1) explainer_agent  
   - Explains concepts in the simplest possible way  
   - Uses analogies, stories, real-life examples  
   - Teaches like explaining to a 5 to 10-year-old 
   - Uses humour to make the explanation engaging 
   - Avoids jargon unless absolutely necessary  

2) learner_agent  
   - Provides in-depth explanations  
   - Includes structured notes  
   - Gives exam-focused content  
   - Provides 16-mark style answers  
   - Includes diagrams (described), bullet points, definitions, and key points  
   - Prepares student for competitive or university exams  
   
AVAILABLE TOOL 
save_notes_to_notion — Saves the generated study notes to a Notion page.
- Writes notes to Notion
- Takes title and content as parameters

DECISION RULES:

If the user:
- Says "explain", "explain simply", "I don't understand", "teach from basics", "like I'm 5", or sounds confused → delegate to explainer_agent
- Mentions "exams", "16 marks", "important questions", "university", "competitive exams", "notes", "revision", or "deep understanding" → delegate to learner_agent
- ONLY If unclear → ask:  
  "Would you like a simple explanation or an exam-focused detailed answer?"
- Use the save_notes_to_notion to write the notes to Notion when the user mentions that they want the notes to be written or stored

CONVERSATION FLOW:

1. First interaction:
   - Greet briefly.
   - Ask what topic they need help with and their goal (understanding vs exams).

2. After user response:
   - Identify intent.
   - Delegate immediately to the correct agent.
   
3. Tool usage: 
    - Use the save_to_notion tool if the user has mentioned that the notes have to be saved or written 

3. Follow-ups:
   - Maintain topic continuity.
   - Switch agents only if the user explicitly changes learning style.

IMPORTANT:
- Do NOT explain the concept yourself.
- Do NOT mix both styles.
- Always delegate once intent is clear.
- Keep responses short and directive.
- Focus on routing, not teaching.

CURRENT STATE:
- Intent: {intent}
"""


class OrchestratorAgent:
    """
    Single orchestrator node that holds the two sub-agents as tools and uses
    a ReAct agent loop to route user queries to the right tool.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.7) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment.")

        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
        )
        self.tools = _build_agent_tools()
        self._intent = "unknown"
        logger.info("OrchestratorAgent initialized with tools", tools=[t.name for t in self.tools])

    def run(self, messages: list, intent: str = "unknown") -> str:
        """
        Run the orchestrator ReAct agent over the full message history.

        Args:
            messages: List of LangChain BaseMessage objects (conversation history).
            intent: Detected user intent ("explain", "learn", or "unknown").

        Returns:
            Final response string from the orchestrator / routed tool.
        """
        try:
            from langchain_core.messages import AIMessage, ToolMessage

            prompt = ORCHESTRATOR_PROMPT.format(intent=intent)
            agent = create_react_agent(self.model, self.tools, prompt=prompt)

            result = agent.invoke({"messages": messages})
            all_messages = result.get("messages", [])

            orchestrator_response = ""
            ai_fallback = ""

            for msg in reversed(all_messages):
                if isinstance(msg, ToolMessage) and msg.content:
                    orchestrator_response = msg.content
                    break
                if isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
                    ai_fallback = self._extract_text(msg.content)

            return orchestrator_response or ai_fallback or "I'm here to help! What would you like to learn?"

        except Exception as e:
            logger.error("OrchestratorAgent.run failed", error=str(e))
            return f"Something went wrong: {e}"

    @staticmethod
    def _extract_text(content) -> str:
        """Extract plain text from string or list-of-blocks content."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts)
        return str(content)
