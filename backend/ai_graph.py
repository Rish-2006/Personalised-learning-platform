# LangGraph state machine for lesson flow (updated for latest API)
try:
	from langgraph.graph import StateGraph, END
except ImportError:
	StateGraph = None
	END = None

# Define the state as a simple dict for compatibility
class LessonState(dict):
	pass

def user_input_node(state):
	state['user_query'] = "Explain photosynthesis"
	return state

def content_generation_node(state):
	state['lesson_content'] = f"Lesson on: {state.get('user_query', '')}"
	return state

def feedback_analyzer_node(state):
	import random
	state['quiz_score'] = random.uniform(0, 1)
	return state

def quiz_score_condition(state):
	return state.get('quiz_score', 0) < 0.7

if StateGraph:
	# Pass the state schema (LessonState) to StateGraph constructor
	graph = StateGraph(state_schema=LessonState)
	graph.add_node('user_input', user_input_node)
	graph.add_node('content_generation', content_generation_node)
	graph.add_node('feedback_analyzer', feedback_analyzer_node)
	graph.add_edge('user_input', 'content_generation')
	graph.add_edge('content_generation', 'feedback_analyzer')
	# Use add_conditional_edges (plural) as per latest API
	graph.add_conditional_edges('feedback_analyzer', {
		'content_generation': quiz_score_condition,
		END: lambda state: not quiz_score_condition(state)
	})
	graph.set_entry_point('user_input')
else:
	graph = None
