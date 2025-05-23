import jwt
from datetime import datetime as dt
from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from database import Reader, Book, Borrow, User
from models import ReaderModel, BookModel, BorrowModel, UserModel
from passlib.hash import bcrypt
from secret import db_url, secret_key

app = FastAPI()
engine = create_engine(db_url, echo=True)
security = True

def verify(token):
    if security:
        try:
            if token == None or jwt.decode(token.replace("Bearer ", ""),
                                           secret_key,
                                           algorithms=["HS256"]).get("sub") == None:
                raise HTTPException(status_code=401, detail="Unauthorized")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
async def root():
    return {"message": "FastAPI application for library"}

@app.post("/register")
def create_user(user: UserModel):
    with Session(engine) as session:
        stmt = select(User).where(User.email == user.email)
        if session.scalars(stmt).one_or_none():
            raise HTTPException(status_code=400, detail="Email already exist")
        session.add(User(email=user.email,
                         password=bcrypt.hash(user.password),
                         is_admin=False))
        session.commit()
    return {"message": "OK"}

@app.post("/login")
def authenticate(user: UserModel):
    with Session(engine) as session:
        stmt = select(User).where(User.email == user.email)
        result = session.scalars(stmt).one_or_none()
        if result:
            if bcrypt.verify(user.password, result.password):
                if result.is_admin:
                    token = jwt.encode({"sub": user.email}, secret_key, algorithm="HS256")
                    return {"access token": token}
                else:
                   raise HTTPException(status_code=403, detail="User isn't admin") 
            else:
                raise HTTPException(status_code=401, detail="Incorrect pasword")
        else:
            raise HTTPException(status_code=404, detail="User is not found") 

@app.post("/create_reader")
def create_reader(reader: ReaderModel):
    with Session(engine) as session:
        stmt = select(Reader).where(Reader.email == reader.email)
        if session.scalars(stmt).one_or_none():
            raise HTTPException(status_code=400, detail="Email already exist")
        session.add(Reader(**dict(reader)))
        session.commit()
    return {"message": "OK"}

@app.get("/read_reader")
def read_reader(reader_id: int, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Reader).where(Reader.id == reader_id)
        reader = session.scalars(stmt).one_or_none()
        if reader == None:
            raise HTTPException(status_code=404, detail="Reader is not found")
    return {"name": reader.name, "email": reader.email}

@app.get("/readers")
def readers(request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Reader).order_by(Reader.name)
        readers = session.scalars(stmt).all()
    return [{"id": x.id, "name": x.name, "email": x.email} for x in readers]

@app.put("/update_reader")
def update_reader(reader_id: int, new_data: ReaderModel, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Reader).where(Reader.id == reader_id)
        reader = session.scalars(stmt).one_or_none()
        if reader == None:
            raise HTTPException(status_code=404, detail="Reader is not found")
        reader.name = new_data.name
        reader.email = new_data.email
        session.commit()
    return {"message": "OK"}

@app.delete("/delete_reader")
def delete_reader(reader_id: int, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Reader).where(Reader.id == reader_id)
        reader = session.scalars(stmt).one_or_none()
        if reader == None:
            raise HTTPException(status_code=404, detail="Reader is not found")
        session.delete(reader)
        session.commit()
    return {"message": "OK"}

@app.post("/create_book")
def create_book(book: BookModel, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        if book.isbn:
            stmt = select(Book).where(Book.isbn == book.isbn)
            if session.scalars(stmt).one_or_none():
                raise HTTPException(status_code=400, detail="Book already exist")
        session.add(Book(**dict(book)))
        session.commit()
    return {"message": "OK"}

@app.get("/read_book")
def read_book(book_id: int, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Book).where(Book.id == book_id)
        book = session.scalars(stmt).one_or_none()
        if book == None:
            return HTTPException(status_code=404, detail="Book is not found")
    return {"title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "quantity": book.quantity}

@app.get("/books")
def books():
    with Session(engine) as session:
        stmt = select(Book).order_by(Book.title)
        books = session.scalars(stmt).all()
    return [{"id": x.id, "title": x.title, "author": x.author, "quantity": x.quantity} for x in books]

@app.put("/update_book")
def update_book(book_id: int, new_data: BookModel, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Book).where(Book.id == book_id)
        book = session.scalars(stmt).one_or_none()
        if book == None:
            return HTTPException(status_code=404, detail="Book is not found")
        book.title = new_data.title
        book.author = new_data.author
        book.year = new_data.year
        book.isbn = new_data.isbn
        book.quantity = new_data.quantity
        session.commit()
    return {"message": "OK"}

@app.delete("/delete_book")
def delete_book(book_id: int, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Book).where(Book.id == book_id)
        book = session.scalars(stmt).one_or_none()
        if book == None:
            return HTTPException(status_code=404, detail="Book is not found")
        session.delete(book)
        session.commit()
    return {"message": "OK"}

@app.post("/give_book")
def give_book(borrow: BorrowModel, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        with session.begin():
            stmt = select(Book).where(Book.id == borrow.book_id)
            book = session.scalars(stmt).one_or_none()
            if book == None:
                raise HTTPException(status_code=404, detail="Book is not found")
            if book.quantity == 0:
                raise HTTPException(status_code=400, detail="Book is not available")
            stmt = select(Reader).where(Reader.id == borrow.reader_id)
            reader = session.scalars(stmt).one_or_none()
            if reader == None:
                raise HTTPException(status_code=404, detail="Reader is not found")
            stmt = select(Borrow).where(Borrow.reader_id == borrow.reader_id).where(Borrow.return_date == None)
            borrows = session.scalars(stmt).all()
            if len(borrows) >= 3:
                raise HTTPException(status_code=400, detail="Too many books borrowed")
            session.add(Borrow(book_id=borrow.book_id,
                               reader_id=borrow.reader_id,
                               borrow_date=dt.today()))
            book.quantity -= 1
            session.commit()
    return {"message": "OK"}

@app.get("/borrows")
def borrows(request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Borrow).order_by(Borrow.id)
        borrows = session.scalars(stmt).all()
    return [{"id": x.id,
             "book_id": x.book_id,
             "reader_id": x.reader_id,
             "borrow_date": x.borrow_date,
             "return_date": x.return_date} for x in borrows]

@app.get("/reader_borrows")
def reader_borrows(reader_id: int, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        stmt = select(Borrow).where(Borrow.reader_id == reader_id).where(Borrow.return_date == None)
        borrows = session.scalars(stmt).all()
    return [{"id": x.id,
             "book_id": x.book_id,
             "reader_id": x.reader_id,
             "borrow_date": x.borrow_date,
             "return_date": x.return_date} for x in borrows]

@app.post("/take_book")
def take_book(borrow: BorrowModel, request: Request):
    verify(request.headers.get("Authorization"))
    with Session(engine) as session:
        with session.begin():
            stmt = select(Book).where(Book.id == borrow.book_id)
            book = session.scalars(stmt).one_or_none()
            if book == None:
                raise HTTPException(status_code=404, detail="Book is not found")
            stmt = select(Reader).where(Reader.id == borrow.reader_id)
            reader = session.scalars(stmt).one_or_none()
            if reader == None:
                raise HTTPException(status_code=404, detail="Reader is not found")
            stmt = select(Borrow).where(Borrow.book_id == borrow.book_id).where(Borrow.reader_id == borrow.reader_id).where(Borrow.return_date == None)
            borrowed = session.scalars(stmt).one_or_none()
            if borrows == None:
                raise HTTPException(status_code=400, detail="Book was not borrowed")
            borrowed.return_date=dt.today()
            book.quantity += 1
            session.commit()
    return {"message": "OK"}
