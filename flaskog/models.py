from flaskog import db
from sqlalchemy import Column, BigInteger, Text, ForeignKey


class Canonical(db.Model):
    id = Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    canonical_url = Column(Text, unique=True, nullable=False)


class URL(db.Model):
    url = Column(Text, primary_key=True)
    canonical_url = Column(Text, ForeignKey("canonical.canonical_url"), nullable=False)


class OGP(db.Model):
    url_id = Column(BigInteger, ForeignKey("canonical.id"), primary_key=True)
    json = Column(Text, nullable=False)
