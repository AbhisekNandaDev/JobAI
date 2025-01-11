from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from model_schema import SignupModel, LoginModel, ResetPasswordModel
from models import User,Job
from jwt_auth import create_jwt_token
from dotenv import load_dotenv
import os
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib


app = FastAPI(docs_url='/docs')


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_db():
    async with async_session() as session:
        yield session

# Routes
@app.post("/signup")
async def signup(user: SignupModel, db: AsyncSession = Depends(get_db)):

    existing_user = await db.execute(
        select(User).filter(User.email == user.email)
    )
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = bcrypt.hash(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    await db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(data: LoginModel, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).filter(User.email == data.email))
    user = user.scalar()
    if not user or not bcrypt.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_jwt_token(data={"sub": user.email,"user_id":user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/reset-password")
async def reset_password(request: ResetPasswordModel, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).filter(User.email == request.email))
    user = user.scalar()
    if not user:
        raise HTTPException(status_code=400, detail="User doesn't exist")
    
    if bcrypt.verify(request.password, user.password):
        if request.new_password == request.password :
            raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
    
        hashed_password = bcrypt.hash(request.new_password)
        user.password = hashed_password
        await db.commit()
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid User or Password")
    

@app.get("/jobs")
async def get_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    return jobs
    
@app.post("/userProfile")
async def create_job(job: Job, user_id: int, db: AsyncSession = Depends(get_db)):
    new_job = Job(
        user_id=user_id,
        userjobdesc=job.jobdesc,
        userjobbenifits=job.jobbenifits,
        userjobqualification=job.jobqualification,
        userjobskills=job.jobskills,
        userjoblocation=job.joblocation,
        userjobsalary=job.jobsalary,
        userjobrequirements=job.jobrequirements,
        userjobexperience=job.jobexperience
    )
    db.add(new_job)
    await db.commit()
    return {"message": "Job created successfully"}

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int, db: AsyncSession = Depends(get_db)):
    model_path = os.path.join("models", "job_recommendation_model.pkl")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('scaler', StandardScaler(with_mean=False)),
        ('kmeans', KMeans(n_clusters=3, random_state=42))
    ])
    model = joblib.load(model_path)
    user = await db.execute(select(User).filter(User.id == user_id))
    user = user.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    result = await db.execute(select(Job))
    jobs = result.scalars().all()
    job_descriptions = [job.jobdesc for job in jobs]
    pipeline.fit(job_descriptions)
    job_clusters = pipeline.predict(job_descriptions)
    user_cluster = pipeline.predict([user.jobdesc])[0]

    recommended_jobs = [jobs[i] for i in range(len(jobs)) if job_clusters[i] == user_cluster]
    return recommended_jobs[:10]