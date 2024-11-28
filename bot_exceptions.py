class FieldMissingError(Exception):
    pass
class IncorrectYearError(Exception):
    pass
class ViolationOfDocumentStructureError(Exception):
    pass
class DataNotFoundError(Exception):
    def __init__(self):
        super().__init__('Data requested was not found, please check the values that are posssible for each fields in the table')