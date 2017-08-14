class ObjectTracker:
    def __init__(self):
        self.data = dict()
        self.accessed_keys = set()

    def get_or_create(self, key, func, *fargs, **fkwds):
        if key in self.data:
            result = self.data[key]
            created = False
        else:
            result = self.data[key] = func(*fargs, **fkwds)
            created = True
        self.accessed_keys.add(key)
        return result, created

    def discard_reset(self):
        unused_keys = set(self.data) - self.accessed_keys
        self.accessed_keys.clear()
        return [(key, self.data.pop(key)) for key in unused_keys]

    def __contains__(self, key):
        return key in self.data
