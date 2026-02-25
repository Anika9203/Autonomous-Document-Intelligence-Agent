from fastapi import FastAPI, Depends, HTTPException
from .database import engine, Base, get_db
from . import models, auth, schemas
from sqlalchemy.orm import Session


app = FastAPI()

#create tables
# When server starts → It automatically creates users table inside PostgreSQL
Base.metadata.create_all(bind=engine)

# a door to my backend appln
@app.get("/")
def root():
    # json formatted data
    return {"message": "API is working!"}

@app.post("/register")
def register(user: schemas.UserCreate, db: Session=Depends(get_db)):

    existing_user=db.query(models.User).filter(models.User.email==user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this Email has already been Registered")
    
    hashed_pw= auth.hash_password(user.password)

    new_user= models.User(email=user.email, hashed_password=hashed_pw)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return{"message":"User Created Successfully!"}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session=Depends(get_db)):

    db_user=db.query(models.User).filter(models.User.email==user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    if not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    access_token=auth.create_access_token(
        data={"sub": db_user.email}
    )

    return{
        "access_token": access_token,
        "token_type": "bearer"
    }