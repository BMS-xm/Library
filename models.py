from pydantic import BaseModel
from typing import Union

class ReaderModel(BaseModel):
    name: str
    email: str

class BookModel(BaseModel):
    title: str
    author: str
    year: Union[int, None] = None
    isbn: Union[str, None] = None
    quantity: int = 1

class BorrowModel(BaseModel):
    book_id: int
    reader_id: int

class UserModel(BaseModel):
    email: str
    password: str
