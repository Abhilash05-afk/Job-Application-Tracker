from services import JobService
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Base, Job


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Frontend setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class JobStatus(str, Enum):
    APPLIED = "Applied"
    SCREENING = "Screening"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"


class JobApplication(BaseModel):
    company: str
    job_title: str
    application_date: str
    status: JobStatus
    job_url: str
    notes: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FRONTEND
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

# CREATE
@app.post("/jobs")
def create_job(job: JobApplication, db: Session = Depends(get_db)):

    new_job = Job(
        company=job.company,
        job_title=job.job_title,
        application_date=job.application_date,
        status=job.status,
        job_url=job.job_url,
        notes=job.notes
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "message": "Job application added successfully",
        "job": new_job
    }


# READ ALL
@app.get("/jobs")
def get_jobs(
    status: JobStatus | None = None,
    db: Session = Depends(get_db)
):
    return JobService.get_all_jobs(db, status)


# READ ONE
@app.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job application not found"
        )

    return job


# UPDATE
@app.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    updated_job: JobApplication,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job application not found"
        )

    job.company = updated_job.company
    job.job_title = updated_job.job_title
    job.application_date = updated_job.application_date
    job.status = updated_job.status
    job.job_url = updated_job.job_url
    job.notes = updated_job.notes

    db.commit()
    db.refresh(job)

    return {
        "message": "Job application updated successfully",
        "job": job
    }


# DELETE
@app.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job application not found"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job application deleted successfully"
    }