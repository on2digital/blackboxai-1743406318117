from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles = relationship('UserRole', back_populates='user')

class Role(Base):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship('UserRole', back_populates='role')

class UserRole(Base):
    """Join table for user-role many-to-many relationship"""
    __tablename__ = 'user_roles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='roles')
    role = relationship('Role', back_populates='users')

class Document(Base):
    """Document model for storing uploaded files"""
    __tablename__ = 'documents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(50), nullable=False)
    status = Column(String(20), default='uploaded')  # uploaded, processing, completed, failed
    metadata = Column(JSON)  # Original document metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    content = relationship('DocumentContent', uselist=False, back_populates='document')

class DocumentContent(Base):
    """Structured content extracted from documents"""
    __tablename__ = 'document_contents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), unique=True)
    text_content = Column(Text)
    structured_data = Column(JSON)  # Tables, lists, etc.
    embeddings = Column(JSON)  # Vector embeddings of the content
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    document = relationship('Document', back_populates='content')

class LLMProviderConfig(Base):
    """Configuration for LLM providers"""
    __tablename__ = 'llm_provider_configs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_name = Column(String(50), nullable=False)  # google-ai, ollama, etc.
    config_data = Column(JSON, nullable=False)  # API keys, model names, etc.
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProcessingJob(Base):
    """Track document processing jobs"""
    __tablename__ = 'processing_jobs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'))
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    logs = Column(Text)

def init_db(connection_string: str):
    """Initialize database connection and create tables"""
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

# Example usage
if __name__ == '__main__':
    # Initialize with PostgreSQL connection string
    db_session = init_db('postgresql://user:password@localhost/document_parser')
    
    # Example: Create a new document record
    from uuid import uuid4
    new_doc = Document(
        id=uuid4(),
        user_id=uuid4(),
        original_filename='sample.pdf',
        storage_path='uploads/sample.pdf',
        file_size=1024,
        file_type='application/pdf',
        status='uploaded'
    )
    
    session = db_session()
    session.add(new_doc)
    session.commit()
    session.close()