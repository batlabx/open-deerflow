"""Agent nodes.

Each function here is a LangGraph node. Nodes read the shared ``DeerState`` and
return a ``Command`` that carries (a) a state update and (b) ``goto`` — the next
node. Routing lives *inside* the nodes rather than in static edges, which is how
the real DeerFlow expresses its dynamic, supervisor-driven control flow.
"""
