'''
pip install fastapi uvicorn
para correr -> univorn main:app
'''
from fastapi import FastAPI, Depends 
from fastapi import Body
from models import Utilizadores, Livros, Colecoes, Utilizadores_Colecoes
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import hashlib
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/users/')
def getUsers(email: str, db: Session = Depends(get_db)):
    user = db.query(Utilizadores.email).filter(Utilizadores.email == email).first()
    
    if user is None:
        return "Não foram encontrados utilizadores"
    else:
        return user[0]


@app.post('/users/') #AKA REGISTO
def addUser( nome: str = Body(...), apelido: str = Body(...), email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    md5 = hashlib.md5()
    md5.update(password.encode())
    verificar_email = db.query(Utilizadores.email).filter(Utilizadores.email == email).first()
    if verificar_email:
        return "Email já está a ser utilizado"
    else:
        #inserir valores na tabela colecoes
        db.execute(text('INSERT INTO Colecoes (nome, isPublic) VALUES (:nome, :isPublic)'), {"nome": email, "isPublic": 1})
        id_colecoes = db.query(Colecoes.idcolecoes).filter(Colecoes.nome == email).first()[0]
        
        #inserir valores na tabela utilizadores
        db.execute(text('INSERT INTO Utilizadores (nome, apelido, email, password) VALUES (:nome, :apelido, :email, :password)'), {"nome": nome, "apelido": apelido, "email": email, "password": md5.hexdigest()})
        id_utilizadores = db.query(Utilizadores.userid).filter(Utilizadores.email == email).first()[0]

        #tive de fazer esta parte com ORM
        values = Utilizadores_Colecoes(userid=id_utilizadores, colecoesid=id_colecoes)
        db.add(values)
        #db.execute(text('INSERT INTO Utilizadores_Colecoes (userid, colecoesid) VALUES (:id_utilizadores, :id_colecoes)'), {"id_utilizadores": id_utilizadores, "id_colecoes": id_colecoes})
        db.commit()


@app.delete('/users/')
def deleteUser(userid: int, db: Session = Depends(get_db)):
    db.execute(text('DELETE FROM Utilizadores WHERE userid = :userid'),{"userid":userid})
    db.commit()

@app.put('/users/')
def updateUser(userid: int = Body(...), nome: str = Body(...), apelido: str = Body(...), email: str = Body(...), db: Session = Depends(get_db)):
   
    if (nome!= Utilizadores.nome or apelido!= Utilizadores.apelido or email!= Utilizadores.email):
        db.execute(text('UPDATE Utilizadores SET nome = :nome , apelido = :apelido ,  email = :email WHERE userid = :userid'), {"nome":nome, "apelido": apelido, "email": email, "userid": userid})
        db.commit()

@app.put('/password')
def updatePassword(password: str = Body(...), userid: int = Body(...) , db: Session = Depends(get_db)):
    md5 = hashlib.md5()
    md5.update(password.encode())
    db.execute(text('UPDATE Utilizadores SET password = :password WHERE userid = :userid'), {"password":md5.hexdigest(), "userid":userid})
    db.commit()



@app.post('/login')
def login(password: str = Body(...), email: str  = Body(...), db: Session = Depends(get_db)):
    md5 = hashlib.md5()
    md5.update(password.encode())
    
    emailQuery = db.query(Utilizadores).filter(Utilizadores.email == email).first()
    passwordQuery = db.query(Utilizadores).filter(Utilizadores.password == md5.hexdigest()).first() # o first vai buscar a primeira row que corresponder ao que é pedido no WHERE ou Noke se não houver nenhuma row
    
    if emailQuery != None and passwordQuery != None:
        return "Success"
    else:
        return "Error"


@app.post('/livros/')
def addBook(idlivros: int = Body(...), nome: str = Body(...), dataemissao: str = Body(...), editora: int = Body(...), descricao: str = Body(...), rating: float = Body(...),ISBN: str = Body(...), paginas: int = Body(...), db: Session = Depends(get_db)):
    db.execute(text('INSERT INTO Livros (idlivros, nome, dataemissao, editora, descricao, rating, ISBNM, paginas) VALUES (:idlivros, :nome, :dataemissao, :editora, :descricao, :rating, :ISBN, :paginas)'), {"idlivros": idlivros, "nome": nome,"dataemissao": dataemissao,"editora": editora, "descricao": descricao, "rating": rating, "ISBN": ISBN, "paginas": paginas})
    db.commit()
    


