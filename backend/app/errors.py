from fastapi import HTTPException


class InvalidCredentialsError(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=401, detail=detail)


class InvalidToken(HTTPException):
    def __init__(self, detail: str = "THe Token is Expired Or Invalid"):
        super().__init__(status_code=401, detail=detail)


class InvalidTokenType(HTTPException):
    def __init__(self, detail: str = "Invalid Token Type"):
        super().__init__(status_code=401, detail=detail)


class EmailAlreadyExistsError(HTTPException):
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(status_code=409, detail=detail)


class UserNotFoundOrUnauthorised(HTTPException):
    def __init__(self, detail: str = "User not found or Unauthorised"):
        super().__init__(status_code=404, detail=detail)


class ProjectNotFound(HTTPException):
    def __init__(self, detail: str = "Project not found"):
        super().__init__(status_code=404, detail=detail)


class ProjectUnauthorised(HTTPException):
    def __init__(self, detail: str = "Unauthorised to perform this action on project"):
        super().__init__(status_code=403, detail=detail)


class TaskNotFound(HTTPException):
    def __init__(self, detail: str = "Task not found"):
        super().__init__(status_code=404, detail=detail)


class InputValidationError(HTTPException):
    def __init__(self, detail: str = "Invalid Input"):
        super().__init__(status_code=400, detail=detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "You are not allowed to perform this action"):
        super().__init__(status_code=403, detail=detail)


class AccountNotVerified(HTTPException):
    def __init__(self, detail: str = "Account Not Verified"):
        super().__init__(status_code=403, detail=detail)


class PasswordResetNotMatching(HTTPException):
    def __init__(self, detail: str = "Passwords are not same"):
        super().__init__(status_code=403, detail=detail)
