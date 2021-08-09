from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer

app = FastAPI()

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A SQLAlchemny ORM Place
class DBPlace(Base):
    __tablename__ = 'places'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String, nullable=True)
    coffee = Column(Boolean)
    wifi = Column(Boolean)
    food = Column(Boolean)


Base.metadata.create_all(bind=engine)

# A Pydantic Place
class Place(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    coffee: bool
    wifi: bool
    food: bool

    class Config:
        orm_mode = True

class PlaceUpdate(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    coffee: Optional[bool]
    wifi: Optional[bool]
    food: Optional[bool]

    class Config:
        orm_mode = True

# Methods for interacting with the database
def get_place(db: Session, place_id: int):
    return db.query(DBPlace).where(DBPlace.id == place_id).first()

def get_places(db: Session):
    return db.query(DBPlace).all()

def create_place(db: Session, place: Place):
    place = DBPlace(**place.dict())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


def delete_place(db:Session, place_id:int):
    place = db.query(DBPlace).where(DBPlace.id == place_id).first()
    db.delete(place)
    db.commit()

    return place

def update_place(db: Session, place: PlaceUpdate):
    # get the existing data
    db_place = db.query(DBPlace).filter(DBPlace.id == place.id).one_or_none()

    for var, value in vars(place).items():
        setattr(db_place, var, value) if value else None
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

# Routes for interacting with the API
@app.post('/places/', response_model=Place)
def create_places_view(place: Place, db: Session = Depends(get_db)):
    place = create_place(db, place)
    return place

@app.get('/places/', response_model=List[Place])
def get_places_view(db: Session = Depends(get_db)):
    return get_places(db)

@app.get('/place/{place_id}')
def get_place_view(place_id: int, db: Session = Depends(get_db)):
    return get_place(db, place_id)

@app.put('/place/update', response_description="Updated Successfully")
def update_place_view(place:PlaceUpdate, db: Session = Depends(get_db)):
    return update_place(db, place)

@app.delete('/place/{place_id}/delete', response_description="Deleted Successfully!")
def delete_place_view(place_id: int, db: Session = Depends(get_db)):
    return delete_place(db, place_id)

@app.get('/')
def root():
    return {'GO TO /docs!'}