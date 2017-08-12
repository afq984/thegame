class ObjectGroup(dict):
    def __init__(self, func):
        self.func = func
        self.pending_removal = []
        self.accessed_keys = set()

    def step(self):
        unused_keys = self.objects.keys() - self.accessed_keys
        for key in unused_keys:
            self.pending_removal.append(self.objects.pop(key))
        self.accessed_keys = set()

    def __getitem__(self, key):
        result = super().__getitem__(key)
        self.accessed_keys.add(key)
        return result

    def __missing__(self, key):
        value = self[key] = self.func()
        return value
