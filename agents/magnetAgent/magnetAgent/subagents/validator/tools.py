"""
Tools for the Validator Agent
"""
from google.adk.tools.tool_context import ToolContext


def exit_loop(tool_context: ToolContext):
    """
    Signal that the design validation loop should exit.
    Call this when the design meets all requirements.
    
    This sets the escalate flag to terminate the LoopAgent iteration.
    """
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    return {}
