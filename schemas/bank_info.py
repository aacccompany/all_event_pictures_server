from pydantic import BaseModel

class BankInfoBase(BaseModel):
    bank_name: str | None = None
    bank_branch: str | None = None
    account_name: str | None = None
    account_number: str | None = None
    citizen_id: str | None = None

class BankInfoCreate(BankInfoBase):
    pass

class BankInfoResponse(BankInfoBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class BankInfoUpdate(BankInfoBase):
    pass
