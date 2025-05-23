import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Reader(Base):
    __tablename__ = "reader"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(30), nullable=False)
    borrows: Mapped[List["Borrow"]] = relationship(back_populates="reader")

class Book(Base):
    __tablename__ = "book"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(30), nullable=False)
    year: Mapped[Optional[int]]
    isbn: Mapped[Optional[str]] = mapped_column(String(20))
    quantity: Mapped[int]
    borrows: Mapped[List["Borrow"]] = relationship(back_populates="book")

class Borrow(Base):
    __tablename__ = "borrow"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"))
    reader_id: Mapped[int] = mapped_column(ForeignKey("reader.id"))
    borrow_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Optional[datetime.date]]
    reader: Mapped["Reader"] = relationship(back_populates="borrows")
    book: Mapped["Book"] = relationship(back_populates="borrows")
    
class User(Base):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    is_admin: Mapped[bool]
    
