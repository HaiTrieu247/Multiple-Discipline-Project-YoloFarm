class EventBus:
    listeners = {}

    @classmethod
    def on(cls, event, callback):
        cls.listeners.setdefault(event, []).append(callback)

    @classmethod
    def emit(cls, event, data=None):
        if event in cls.listeners:
            for cb in cls.listeners[event]:
                cb(data)