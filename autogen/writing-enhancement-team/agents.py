from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
import os

# Text Reviewer Model Client
text_reviewer_model_client = OpenAIChatCompletionClient(
    model=os.getenv("TEXT_REVIEWER_MODEL_NAME"),
    model_info={
        "family": "gpt-4o",
        "function_calling": True,
        "json_output": True,
        "structured_output": True,
        "vision": True,
    },
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Text Rewriter Model Client
text_rewriter_model_client = OpenAIChatCompletionClient(
    model=os.getenv("TEXT_REWRITER_MODEL_NAME"),
    model_info={
        "family": "unknown",
        "function_calling": True,
        "json_output": True,
        "structured_output": True,
        "vision": True,
    },
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Text Reviewer Agent
text_reviewer_agent = AssistantAgent(
    name="text_reviewer",
    model_client=text_reviewer_model_client,
    # system_message="You are a text reviewer. You are given a text and you need to review it and provide feedback on it.",
    system_message="""
    You are a text reviewer agent.
    Your job is to valuates a given text and produces structured improvement suggestions.    
    First, you need to understand the language of the text (French or English).
    
    **Input**: Raw user-provided text  
    
    **Responsibilities**:
        - Assess grammar, clarity, tone, structure, and coherence
        - Identify weak or ambiguous phrasing
        - Suggest enhancements for readability and style
        - Output actionable suggestions in a standardized format or simply "APPROVED" to indicate that you have finished your task and the text is good to go.
    
    **Output**: 
        - A list of structured suggestions and evaluation notes OR simply the word "APPROVED" to indicate that you have finished your task and the provided text is good to go.
    
    Important: 
        - Do not rephrase the text, just provide the suggestions.
        - Answer in the same language as initial text.
        - When you are done, simply output "APPROVED" to indicate that you have finished your task.
        - If you proposed changes do not output the word "APPROVED", only write "APPROVED" if you are done and the text is good to go.
    """,
    model_client_stream=True
)

# Text Rewriter Agent
text_rewriter_agent = AssistantAgent(
    name="text_rewriter",
    model_client=text_rewriter_model_client,
    system_message="""
    You are a text rewriter agent.
    Your job is to apply the suggestions provided by the `text_reviewer` agent to the original text.
    **Responsibilities**:
        - Rewrite or refine sentences based on the review feedback
        - Ensure the meaning and intent are preserved        
    **Input**: Improvement suggestions from `text_reviewer` agent
    **Output**: Enhanced text
    Important:
        - Do not write any other text than the enhanced text. No comment, no explanation, no nothing.
    """,
    model_client_stream=True
)

# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVED")
max_message_termination = MaxMessageTermination(max_messages=10, include_agent_event=False)
team_combined_termination = text_termination | max_message_termination

# Create Agents Team (Round Robin)
writing_enhancement_team = RoundRobinGroupChat(
    [text_reviewer_agent, text_rewriter_agent],
    termination_condition=team_combined_termination,
)
