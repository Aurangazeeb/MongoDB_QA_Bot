from src.bot_exceptions import FieldMissingError, IncorrectYearError, ViolationOfDocumentStructureError, DataNotFoundError


class BotResponseExceptionHandler:
    """
    A class dedicated to handle all known exception raised by this bot
    """
    @staticmethod
    def handle_exception(exception_title=None, exception_message= None):
        if exception_title:
            if any([title_str for title_str in ['missing', 'found', 'no data', 'not contain a field', 'does not have a field'] if title_str in exception_title.lower()+ ' ' + exception_message.lower()]):
                raise FieldMissingError(exception_message)
            elif 'year' in exception_title.lower():
                raise IncorrectYearError(exception_message)
            elif any([title_str for title_str in ['range', 'specific'] if title_str in exception_title.lower()]):
                raise ViolationOfDocumentStructureError(exception_message)
            else:
                raise Exception(f"Unknown error : {exception_message}")
        else:
            raise DataNotFoundError