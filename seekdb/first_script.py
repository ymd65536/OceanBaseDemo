import pyseekdb

client = pyseekdb.Client(path="./agent_state.db")
memory = client.get_or_create_collection(name="episodic")

for step in agent.run():
    # Persist the observation
    memory.upsert(ids=[step.id], documents=[step.observation])

    # Retrieve relevant context — milliseconds after the write,
    # served by the incremental HNSW (no waiting on a background rebuild)
    relevant = memory.query(query_texts=step.next_query, n_results=5)

    agent.act(relevant)
