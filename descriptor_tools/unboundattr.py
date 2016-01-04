class UnboundAttribute:
    def __init__(self, descriptor, owner):
        self.descriptor = descriptor
        self.owner

    def __call__(self, instance):
        return self.descriptor.__get__(instance, self.owner)

    def __getattr__(self, item):
        return getattr(self.descriptor, item)

    def __str__(self):
        pass  # TODO

    def __repr__(self):
        pass  # TODO
