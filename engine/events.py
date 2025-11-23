class EventBus:
    def __init__(self):
        self._subs = {}

    def on(self, event_name: str, handler):
        self._subs.setdefault(event_name, []).append(handler)

    def emit(self, event_name: str, **kwargs):
        for h in self._subs.get(event_name, []):
            h(**kwargs)
