from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Utilizadores(Base):
    __tablename__ = "Utilizadores"

    userid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    apelido = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)


class Livros(Base):
    __tablename__ = "Livros"

    idlivros = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    ISBN = Column(String(255), nullable=False)
    dataemissao = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=False)
    rating = Column(Float, nullable=False)
    paginas = Column(Integer, nullable=False) 
    url = Column(String(255), nullable=False)

class Colecoes(Base):
    __tablename__= "Colecoes"

    idcolecoes = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    isPublic = Column(Boolean, nullable=False)

class Utilizadores_Colecoes(Base):
    __tablename__ = "Utilizadores_Colecoes"

    colecoesid = Column(Integer, primary_key=True)
    userid = Column(Integer, primary_key=True)

class Colecoes_Livros(Base):
    __tablename__ = "Colecoes_Livros"

    colecoesid = Column(Integer, primary_key=True)
    idlivros = Column(Integer, primary_key=True)