from sqlmodel import SQLModel, create_engine
from models import User, Product, License, CompanyProduct

engine = create_engine("sqlite:///test.db", echo=True)
SQLModel.metadata.create_all(engine)

print("Model loaded and tables created successfully")