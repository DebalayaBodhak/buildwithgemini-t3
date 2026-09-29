# My agent: Scenery Describer Agent

One-liner: A conversational agent that helps users generate evocative scenery descriptions and visual artwork based on real-time location, weather, and time of day.

Tool coverage:
- Memory: Remembers preferred aesthetic styles (e.g. cinematic, cozy, dramatic), favorite locations, and past scenery journal entries across sessions.
- Tools: Location geocoding & live weather lookup tool (fetching temperature, weather conditions, time of day, and solar/lunar position).
- Catalog/UI: A collection of "Saved Scenic Moments" rendered as A2UI cards displaying location, weather metrics, time, and atmospheric descriptions.
- Image gen: AI-generated visual artwork/photo capturing the precise scenery description, lighting, and weather.
- Sandbox: Python code execution to calculate golden hour/blue hour lighting windows or atmospheric comfort indices.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Live external weather/geocoding API, code sandbox for solar timing calculations, Cloud Trace observability
