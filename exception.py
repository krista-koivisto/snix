class Snixception(RuntimeError):
    def __init__(self, offset, msg):
        self.args = (offset, msg)
