from flaskog import db
from sqlalchemy import Column, BigInteger, Text


class URL(db.Model):
    url = Column(Text, primary_key=True)
    canonical_url = Column(Text, nullable=False)


class Canonical(db.Model):
    id = Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    canonical_url = Column(Text, unique=True, nullable=False)


class OGP(db.Model):
    url_id = Column(BigInteger, primary_key=True)
    json = Column(Text, nullable=False)
