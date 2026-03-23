import logging

class Session:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.authenticated = False
        self.username = None
        self.user_id = None
        logging.info(f"new session created for node {node_id}.")


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, Session] = {}

    def get_or_create(self, node_id: str) -> Session:
        if node_id not in self.sessions:
            self.sessions[node_id] = Session(node_id)
        return self.sessions[node_id]

    def get(self, node_id: str) -> Session | None:
        return self.sessions.get(node_id)

    def remove(self, node_id: str):
        self.sessions.pop(node_id, None)
