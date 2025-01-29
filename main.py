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
from fastapi.encoders import jsonable_encoder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/users/")
def getUsers(email: str, db: Session = Depends(get_db)):
    user = db.query(Utilizadores.email, Utilizadores.nome, Utilizadores.apelido).filter(Utilizadores.email == email).first()
    if user is None:
        return "Não foram encontrados utilizadores"
    else:
        return   {
            "nome": user.nome,
            "apelido": user.apelido,
            "email": user.email
        }
    


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


@app.delete('/users/delete')
def deleteUser(userid: int, db: Session = Depends(get_db)):
    db.execute(text('DELETE FROM Utilizadores_Colecoes WHERE userid = :userid'), {"userid":userid})
    db.execute(text('DELETE FROM Utilizadores WHERE userid = :userid'),{"userid":userid})
    db.commit()

@app.put('/users/update')
def updateUser( userid: int = Body(...) ,nome: str = Body(...), apelido: str = Body(...), email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
   
    md5 = hashlib.md5()
    md5.update(password.encode())
    if (nome!= Utilizadores.nome or apelido!= Utilizadores.apelido or email!= Utilizadores.email or md5.hexdigest() != Utilizadores.password):
        db.execute(text('UPDATE Utilizadores SET nome = :nome , apelido = :apelido ,  email = :email WHERE userid = :userid'), {"nome":nome, "apelido": apelido, "email": email, "userid":userid})
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
    
    nomeQuery = db.query(Utilizadores.nome).filter(Utilizadores.email == email).first()
    idQuery = db.query(Utilizadores.userid).filter(Utilizadores.email == email).first()
    emailQuery = db.query(Utilizadores).filter(Utilizadores.email == email).first()
    passwordQuery = db.query(Utilizadores).filter(Utilizadores.password == md5.hexdigest()).first() # o first vai buscar a primeira row que corresponder ao que é pedido no WHERE ou Noke se não houver nenhuma row
    
    if emailQuery != None and passwordQuery != None:
        return {"userid": idQuery[0], "nome":nomeQuery[0]}
    else:
        return "Error"


@app.post('/users/{userid}/livros')
def addBook(userid: int , nome: str = Body(...), dataemissao: str = Body(...), editora: int = Body(...), descricao: str = Body(...), rating: float = Body(...),ISBN: str = Body(...), paginas: int = Body(...), db: Session = Depends(get_db)):
    #isto vai buscar o id da colecao associado ao userid
    result = db.execute(text('SELECT colecoesid FROM Utilizadores_Colecoes WHERE userid = :userid'), {"userid": userid}).first()
    db.execute(text('INSERT INTO Livros ( titulo, dataemissao, editora, descricao, rating, ISBN, paginas) VALUES (:nome, :dataemissao, :editora, :descricao, :rating, :ISBN, :paginas)'), { "nome": nome,"dataemissao": dataemissao,"editora": editora, "descricao": descricao, "rating": rating, "ISBN": ISBN, "paginas": paginas})
    
    idlivros = db.execute(text('SELECT idlivros FROM Livros WHERE ISBN = :ISBN'), {"ISBN": ISBN}).first()
    db.execute(text('INSERT INTO Colecoes_Livros (colecoesid, idlivros) VALUES (:idcolecoes, :idlivros)'), {"idcolecoes": result[0], "idlivros": idlivros[0]})
    db.commit()


@app.post('/users/{user_id}/livros')
def add_book(
    user_id: int,
    nome: str = Body(...), dataemissao: str = Body(...), editora: int = Body(...), descricao: str = Body(...), rating: float = Body(...),ISBN: str = Body(...), paginas: int = Body(...), db: Session = Depends(get_db)
):

    result = db.execute(text('SELECT colecoesid FROM Utilizadores_Colecoes WHERE userid = :user_id'),{"user_id": user_id})
    collection_id = result.scalar()
    
    
    result = db.execute(
        text('INSERT INTO Livros (titulo, dataemissao, editora, descricao, rating, ISBN, paginas) VALUES (:nome, :dataemissao, :editora, :descricao, :rating, :ISBN, :paginas)'),
        {
            "nome": nome,
            "dataemissao": dataemissao,
            "editora": editora,
            "descricao": descricao,
            "rating": rating,
            "ISBN": ISBN,
            "paginas": paginas
        }
    )
    
    book_id = result.scalar()
    
    # Insert the relationship into Colecoes_Livros
    db.execute(
        text('INSERT INTO Colecoes_Livros (idlivros, idcolecoes) VALUES (:book_id, :collection_id)'),
        {
            "book_id": book_id,
            "collection_id": collection_id
        }
    )
    
    db.commit()
    
    return JSONResponse(status_code=200)



@app.get("/colecoes/")
def get_colecoes(userid: int, db: Session = Depends(get_db)):
    query = text('''
        SELECT c.*
        FROM Colecoes c
        JOIN Utilizadores_Colecoes uc ON uc.colecoesid = c.idcolecoes
        WHERE uc.userid = :userid
    ''')
    

    result = db.execute(query, {"userid": userid}).fetchall()

    colecoes = [{"idcolecoes": r[0], "nome": r[1], "isPublic": r[2]} for r in result]

    return {"colecoes": colecoes}



@app.get("/users/{user_id}/collections/{collection_id}/books")
def get_books_for_collection(user_id: int, collection_id: int, db: Session = Depends(get_db)):
    # Check if the collection belongs to the user
    user_collection = db.query(Utilizadores_Colecoes).filter(
        Utilizadores_Colecoes.userid == user_id,
        Utilizadores_Colecoes.colecoesid == collection_id
    ).first()

    if not user_collection:
        raise HTTPException(status_code=404, detail="Collection not found for user")

    # Raw SQL query to fetch books from a collection
    query = text('''
        SELECT l.idlivros, l.titulo, l.ISBN, l.dataemissao, l.descricao, l.rating, l.paginas
        FROM Livros l
        JOIN Colecoes c ON c.idcolecoes = l.idcolecao
        WHERE c.idcolecoes = :collection_id
    ''')

    result = db.execute(query, {"collection_id": collection_id}).fetchall()

    # Map the result to a list of dictionaries
    books = [{"idlivros": r[0], "titulo": r[1], "ISBN": r[2], "dataemissao": r[3],
              "descricao": r[4], "rating": r[5], "paginas": r[6]} for r in result]

    return {"books": books}

