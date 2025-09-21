# Crew.ai setup with OpenAI model
from crewai import Crew, Agent
from openai import OpenAI

# Initialize OpenAI model (ensure your API key is set in environment or config)
openai_model = OpenAI(model="gpt-3.5-turbo")

# Define the Researcher agent
researcher = Agent(
	name="Researcher",
	goal="Gather information on a given topic.",
	model=openai_model
)

# Define the Curriculum Designer agent
curriculum_designer = Agent(
	name="Curriculum Designer",
	goal="Turn gathered information into a structured lesson plan for students.",
	model=openai_model
)

# Create the crew
learning_crew = Crew(agents=[researcher, curriculum_designer])
