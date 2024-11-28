from bot_exceptions import FieldMissingError, IncorrectYearError, ViolationOfDocumentStructureError, DataNotFoundError

class BotResponseExceptionHandler:
    @staticmethod
    def handle_exception(exception_title=None, exception_message= None):
        if exception_title:
            if 'missing field' in exception_title.lower():
                raise FieldMissingError(exception_message)
            elif 'incorrect year' in exception_title.lower():
                raise IncorrectYearError(exception_message)
            elif any([title_str for title_str in ['range', 'specific'] if title_str in exception_title.lower()]):
                raise ViolationOfDocumentStructureError(exception_message)
        else:
            raise DataNotFoundError