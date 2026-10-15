from sqlalchemy.orm import Session
from models import Job


class JobService:

    @staticmethod
    def get_all_jobs(db: Session, status=None):
        query = db.query(Job)

        if status:
            query = query.filter(Job.status == status.value)

        return query.all()