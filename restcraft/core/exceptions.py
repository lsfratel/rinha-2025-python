class RestCraft(Exception):
    def __init__(self, details, status=500):
        super().__init__(details, status)
        self.details = details
        self.status = status


class NotFound(RestCraft):
    def __init__(self, details, status=404):
        super().__init__(details, status)


class ValidationError(RestCraft):
    def __init__(self, details, status=400):
        super().__init__(details, status)
