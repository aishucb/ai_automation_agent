from phi.workspace import Workspace
from phi.agent import Agent
from phi.tools import Tool
from phi.llm import LLMChat
from phi.assistant import Assistant

# Define the workspace
workspace = Workspace(
    name="ai-email-marketing-agent",
    description="AI Email Marketing Agent with Audience Segmentation",
    llm=LLMChat(model="gpt-4"),
)

# Create the audience segmentation agent
audience_agent = Agent(
    name="audience_segmentation",
    description="Manages contact ingestion and audience segmentation",
    instructions=[
        "You are an AI agent responsible for managing audience segmentation for email marketing campaigns.",
        "You can ingest CSV files containing school/principal contacts, update engagement metrics, and segment audiences based on behavior.",
        "Always validate email addresses and handle duplicates appropriately.",
        "Provide clear summaries of ingestion results and segmentation statistics."
    ],
    tools=[
        Tool(
            name="ingest_csv",
            description="Ingest contacts from a CSV file into the database",
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "Path to the CSV file containing contact data"
                }
            }
        ),
        Tool(
            name="update_contact_engagement",
            description="Update contact engagement metrics and add appropriate tags",
            parameters={
                "email": {
                    "type": "string",
                    "description": "Contact's email address"
                },
                "event_type": {
                    "type": "string",
                    "enum": ["opened", "clicked", "replied"],
                    "description": "Type of engagement event"
                }
            }
        ),
        Tool(
            name="get_contacts_by_tag",
            description="Get all contacts with a specific tag",
            parameters={
                "tag": {
                    "type": "string",
                    "description": "Tag to filter contacts by"
                }
            }
        ),
        Tool(
            name="get_tag_counts",
            description="Get counts of contacts for each tag",
            parameters={}
        )
    ]
)

# Add the agent to the workspace
workspace.add_agent(audience_agent)
