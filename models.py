import datetime as dt

from sqlalchemy import Column, String, DateTime, create_engine, Integer,Boolean
from sqlalchemy.orm import declarative_base, sessionmaker,Session


DATABASE_URI = "sqlite:///./appointment.db"

engine = create_engine(
    DATABASE_URI,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    patient_name = Column(String(100), nullable=False)
    doctor_name = Column(String(100), nullable=False)

    appointment_date = Column(DateTime, nullable=False)

    reason = Column(String, nullable=True)

    canceled = Column(Boolean, default=False)
    

    created_at = Column(
        DateTime,
        default=dt.datetime.utcnow
    )


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db():
    db: Session = SessionLocal()
   
    try:
        yield db
    finally:
        db.close()
