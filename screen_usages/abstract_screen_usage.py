class AbstractScreenUsage(object):

    def get_next_step(self):
        raise NotImplementedError

    def serialize_state(self):
        raise NotImplementedError

    def load_state(self, serialized_state):
        raise NotImplementedError
