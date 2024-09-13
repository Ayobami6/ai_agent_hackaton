class ServiceException(Exception):

    def __init__(self, *args: object, status_code: int) -> None:
        super().__init__(*args)
