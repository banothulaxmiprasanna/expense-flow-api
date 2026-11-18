# ============================================================
# SESSION 3 — FILE 2 OF 4: user.py
# ============================================================
# WHAT THIS FILE IS:
#   Pydantic schemas for the User entity.
#   Covers user registration, login response.
#
# KEY THINGS TO POINT OUT DURING SESSION:
#   - EmailStr: validates email format automatically
#   - pattern=: regex validation for employee_id and role
#   - @field_validator: validates ONE field with custom logic
#     (password strength — needs re module, can't use Field())
#   - TokenResponse: what we return after a successful login
# ============================================================

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ─────────────────────────────────────────────────────────────
# UserBase — shared fields for all user schemas
# ─────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Must be a valid email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Employee's full name")
    employee_id: str = Field(
        ...,
        pattern=r'^EMP-\d{4,6}$',
        description="Must match format EMP-XXXX to EMP-XXXXXX (4-6 digits)"
    )
    # Valid examples:   EMP-1234  EMP-123456
    # Invalid examples: EMP-12   E123   emp-1234


# ─────────────────────────────────────────────────────────────
# UserCreate — used for POST /users (registration)
# Inherits email, full_name, employee_id from UserBase.
# Adds password with a @field_validator for strength rules.
# ─────────────────────────────────────────────────────────────
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Min 8 chars, must have uppercase + number")
    department_id: int = Field(..., ge=1, description="ID of the user's department")
    manager_id: int | None = Field(default=None, description="Optional: ID of direct manager")
    role: str = Field(
        default="employee",
        pattern=r'^(employee|manager|finance|admin)$',
        description="Must be: employee, manager, finance, or admin"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # Rule 1: must contain at least one uppercase letter
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        # Rule 2: must contain at least one number
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        # If both rules pass — return the value (ALWAYS return v!)
        return v


# ─────────────────────────────────────────────────────────────
# UserResponse — what the API returns when you read a user
# Inherits from UserBase — never returns the password.
# model_config from_attributes=True: reads from SQLAlchemy objects.
# ─────────────────────────────────────────────────────────────
class UserResponse(UserBase):
    id: int
    role: str
    department_id: int
    manager_id: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# TokenResponse — returned after successful login (POST /auth/login)
# Contains the JWT access token and the full user object.
# ─────────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token lifetime in seconds")
    user: UserResponse
