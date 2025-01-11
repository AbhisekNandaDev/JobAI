from pydantic import BaseModel, EmailStr

# Pydantic models
class SignupModel(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordModel(BaseModel):
    email: str

class ResetPasswordModel(BaseModel):
    email: EmailStr
    password: str
    new_password: str

    
