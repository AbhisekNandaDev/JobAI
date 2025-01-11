from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine, text

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    reset_token = Column(String, nullable=True)


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    jobname = Column(String, nullable=True)
    jobdesc = Column(String, nullable=True)
    jobbenifits = Column(String, nullable=True)
    jobqualification = Column(String, nullable=True)
    jobskills = Column(String, nullable=True)
    joblocation = Column(String, nullable=True)
    jobsalary = Column(String, nullable=True)
    jobrequirements = Column(String, nullable=True)
    jobexperience = Column(String, nullable=True)
    companyname = Column(String, nullable=True)
    joblink = Column(String, nullable=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    userjobdesc = Column(String, nullable=True)
    userjobbenifits = Column(String, nullable=True)
    userjobqualification = Column(String, nullable=True)
    userjobskills = Column(String, nullable=True)
    userjoblocation = Column(String, nullable=True)
    userjobsalary = Column(String, nullable=True)
    userjobrequirements = Column(String, nullable=True)
    userjobexperience = Column(String, nullable=True)