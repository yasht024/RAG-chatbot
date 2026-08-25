from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class SchemeModel(Base):
    __tablename__ = "schemes"

    scheme_id = Column(String, primary_key=True)
    canonical_name = Column(String, nullable=False, unique=True)
    amc = Column(String, nullable=False, default="HDFC Mutual Fund")
    category = Column(String, nullable=False)
    default_plan = Column(String, nullable=False, default="Direct")
    default_option = Column(String, nullable=False, default="Growth")
    groww_url = Column(String, nullable=False)
    coverage_status = Column(String, nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    aliases = relationship("AliasModel", back_populates="scheme", cascade="all, delete-orphan")
    facts = relationship("FactModel", back_populates="scheme", cascade="all, delete-orphan")


class AliasModel(Base):
    __tablename__ = "aliases"

    alias_id = Column(String, primary_key=True)
    scheme_id = Column(String, ForeignKey("schemes.scheme_id"), nullable=False)
    alias_name = Column(String, nullable=False, index=True)
    provenance = Column(String, nullable=False, default="CURATED")
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_to = Column(DateTime(timezone=True), nullable=True)

    scheme = relationship("SchemeModel", back_populates="aliases")


class DocumentModel(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True)
    source_domain = Column(String, nullable=False)
    canonical_url = Column(String, nullable=False)
    document_title = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    scope = Column(String, nullable=False, default="SCHEME")
    publication_date = Column(String, nullable=True)
    effective_from = Column(String, nullable=True)
    content_hash = Column(String, nullable=False, unique=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    approval_status = Column(String, nullable=False, default="APPROVED")

    passages = relationship("PassageModel", back_populates="document", cascade="all, delete-orphan")


class PassageModel(Base):
    __tablename__ = "passages"

    passage_id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.document_id"), nullable=False)
    scheme_ids = Column(JSON, nullable=False)
    plan = Column(String, nullable=False, default="Direct")
    option = Column(String, nullable=False, default="Growth")
    heading_path = Column(JSON, nullable=True)
    page_number = Column(Integer, nullable=True)
    normalized_text = Column(Text, nullable=False)
    source_text_hash = Column(String, nullable=False)
    fact_types = Column(JSON, nullable=True)
    extraction_confidence = Column(Float, nullable=False, default=1.0)
    embedding = Column(Vector(1024), nullable=True)  # BGE Large vector dimension
    index_version = Column(String, nullable=False)

    document = relationship("DocumentModel", back_populates="passages")


class FactModel(Base):
    __tablename__ = "facts"

    fact_id = Column(String, primary_key=True)
    scheme_id = Column(String, ForeignKey("schemes.scheme_id"), nullable=False)
    fact_type = Column(String, nullable=False)
    value_display = Column(String, nullable=False)
    value_normalized = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    conditions = Column(Text, nullable=True)
    plan = Column(String, nullable=False, default="Direct")
    option = Column(String, nullable=False, default="Growth")
    effective_from = Column(String, nullable=True)
    passage_id = Column(String, ForeignKey("passages.passage_id"), nullable=False)
    validation_status = Column(String, nullable=False, default="VALID")

    scheme = relationship("SchemeModel", back_populates="facts")


class ConflictModel(Base):
    __tablename__ = "conflicts"

    conflict_id = Column(String, primary_key=True)
    scheme_id = Column(String, nullable=False)
    fact_type = Column(String, nullable=False)
    document_id_1 = Column(String, nullable=False)
    document_id_2 = Column(String, nullable=False)
    status = Column(String, nullable=False, default="OPEN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ManifestModel(Base):
    __tablename__ = "manifests"

    manifest_id = Column(String, primary_key=True)
    index_version = Column(String, nullable=False, unique=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="STAGING")
