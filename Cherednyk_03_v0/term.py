class Term:
    id_counter = 0

    def __init__(self,posting):
        self.id = Term.id_counter
        Term.id_counter += 1
        self.freq = 0
        self.postings = posting

