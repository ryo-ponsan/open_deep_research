#!/usr/bin/env python3
import argparse
import asyncio
import os
import getpass
import uuid
from typing import Dict, Any, Optional

import open_deep_research
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research.graph import builder
from open_deep_research.configuration import Configuration, PlannerProvider, WriterProvider, SearchAPI


def set_env(var: str):
    """Set environment variable if not already set, prompting user for input."""
    if not os.environ.get(var):
        value = getpass.getpass(f"{var}: ")
        os.environ[var] = value
        print(f"Set {var} environment variable")
    else:
        print(f"Using existing {var} environment variable")


def setup_environment(config_name: str):
    """Set up necessary API keys based on the selected configuration."""
    # Always set OpenAI API key as it's used in most configurations
    set_env("OPENAI_API_KEY")
    
    # Set other API keys based on configuration
    if config_name in ["claude", "fast"]:
        set_env("ANTHROPIC_API_KEY")
    
    if config_name in ["deepseek", "fast", "openai-only"]:
        set_env("TAVILY_API_KEY")
    
    if config_name == "deepseek":
        set_env("GROQ_API_KEY")
    
    if config_name == "claude":
        set_env("PERPLEXITY_API_KEY")


def get_config(config_name: str) -> Dict[str, Any]:
    """Get configuration based on name."""
    REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for 1 structural element (either a list of table) that distills the main body sections 
   - Provide a concise summary of the report"""

    configs = {
        "claude": {
            "thread_id": str(uuid.uuid4()),
            "search_api": SearchAPI.PERPLEXITY.value,
            "planner_provider": PlannerProvider.ANTHROPIC.value,
            "planner_model": "claude-3-7-sonnet-latest",
            "writer_provider": WriterProvider.ANTHROPIC.value,
            "writer_model": "claude-3-5-sonnet-latest",
            "max_search_depth": 2,
            "report_structure": REPORT_STRUCTURE,
        },
        "deepseek": {
            "thread_id": str(uuid.uuid4()),
            "search_api": SearchAPI.TAVILY.value,
            "planner_provider": PlannerProvider.GROQ.value,
            "planner_model": "deepseek-r1-distill-llama-70b",
            "writer_provider": WriterProvider.GROQ.value,
            "writer_model": "llama-3.3-70b-versatile",
            "report_structure": REPORT_STRUCTURE,
            "max_search_depth": 1,
        },
        "fast": {
            "thread_id": str(uuid.uuid4()),
            "search_api": SearchAPI.TAVILY.value,
            "planner_provider": PlannerProvider.OPENAI.value,
            "planner_model": "gpt-4o-mini",
            "writer_provider": WriterProvider.ANTHROPIC.value,
            "writer_model": "claude-3-5-sonnet-latest",
            "max_search_depth": 1,
            "report_structure": REPORT_STRUCTURE,
        },
        "openai-only": {
            "thread_id": str(uuid.uuid4()),
            "search_api": SearchAPI.TAVILY.value,
            "planner_provider": PlannerProvider.OPENAI.value,
            "planner_model": "gpt-4o",
            "writer_provider": WriterProvider.OPENAI.value,
            "writer_model": "gpt-4o",
            "max_search_depth": 1,
            "report_structure": REPORT_STRUCTURE,
        }
    }
    
    return {"configurable": configs.get(config_name, configs["openai-only"])}


async def run_graph(topic: str, config: Dict[str, Any], feedback: Optional[str] = None):
    """Run the graph with the given topic and configuration."""
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    
    # Initial run
    print(f"Generating report on: {topic}")
    print("Initial planning phase...")
    async for event in graph.astream({"topic": topic}, config, stream_mode="updates"):
        if '__interrupt__' in event:
            interrupt_value = event['__interrupt__'][0].value
            print("\n" + interrupt_value + "\n")
    
    # Feedback phase if provided
    if feedback:
        print(f"Providing feedback: {feedback}")
        async for event in graph.astream(Command(resume=feedback), config, stream_mode="updates"):
            if '__interrupt__' in event:
                interrupt_value = event['__interrupt__'][0].value
                print("\n" + interrupt_value + "\n")
    
    # Approval phase
    print("Approving plan and generating final report...")
    async for event in graph.astream(Command(resume=True), config, stream_mode="updates"):
        # Just print progress updates
        if 'state' in event:
            print(f"Current state: {event['state']}")
    
    # Get final report
    final_state = graph.get_state(config)
    report = final_state.values.get('final_report')
    
    print("\n\n=== FINAL REPORT ===\n")
    print(report)
    
    return report


def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description="Generate research reports using AI.")
    parser.add_argument("topic", help="The topic to research")
    parser.add_argument("--config", choices=["claude", "deepseek", "fast", "openai-only"], 
                        default="openai-only", help="Configuration preset to use")
    parser.add_argument("--feedback", help="Optional feedback to refine the report plan")
    parser.add_argument("--output", help="Optional file to save the report to")
    
    args = parser.parse_args()
    
    # Setup environment based on selected configuration
    setup_environment(args.config)
    
    # Get configuration
    config = get_config(args.config)
    
    # Run the graph
    report = asyncio.run(run_graph(args.topic, config, args.feedback))
    
    # Save to file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()


