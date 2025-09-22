# Crew.ai setup with OpenAI model

import os
from crewai import Crew, Agent
from openai import OpenAI

# Load OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
	raise RuntimeError("OPENAI_API_KEY environment variable not set.")

# Initialize OpenAI client with API key (specify model when making requests)
openai_model = OpenAI(api_key=openai_api_key)


# Define the Researcher agent
researcher = Agent(
	name="Researcher",
	role="AI Research Specialist",
	goal="Gather information on a given topic.",
	backstory="An expert in online research and information synthesis.",
	model=openai_model
)

# Define the Curriculum Designer agent
curriculum_designer = Agent(
	name="Curriculum Designer",
	role="Curriculum Architect",
	goal="Turn gathered information into a structured lesson plan for students.",
	backstory="A creative educator skilled at designing engaging lesson plans.",
	model=openai_model
)

# Create the crew
learning_crew = Crew(agents=[researcher, curriculum_designer])
