import os
from google.adk.agents import LlmAgent
from . import prompt
from .maps_tools import maps_compute_route, maps_search_places

root_agent = LlmAgent(
    model=os.environ.get('GOOGLE_ADK_MODEL', 'gemini-3.5-flash-lite'),
    name='google_map_adk',
    instruction=prompt.instruction,
    tools=[maps_search_places, maps_compute_route],
)
