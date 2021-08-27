from threading import Thread


class Bot(Thread):

    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        raise NotImplementedError()
