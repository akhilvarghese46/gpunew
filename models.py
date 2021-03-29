class Gpu():
    def __init__(self, name, doi, manufacturer):
        self.name = name
        self.doi = doi
        self.manufacturer = manufacturer

    def set_properties(self, name, value):
        setattr(self, name, value)
