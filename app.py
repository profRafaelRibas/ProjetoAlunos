from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "alunos2em"

usuario = "sesisenai"
senha = "2023adm"
login = False

#FUNÇÃO PARA VERIFICAR SESSÃO
def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False

#CONEXÃO COM O BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_alunos.db")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()
    
# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    alunos = conexao.execute('SELECT * FROM alunos ORDER BY id_alun').fetchall()
    conexao.close()
    return render_template("home.html", alunos=alunos)

#ROTA DA PÁGINA LOGIN
@app.route("/login")
def login():
    return render_template("login.html")

#código do LOGOUT
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

# ROTA DA PÁGINA DE CADASTRO
@app.route("/cadalunos")
def cadalunos():
    return render_template("cadalunos.html")

# ROTA DA PÁGINA DE CADASTRO NO BANCO
@app.route("/cadastro",methods=["post"])
def cadastro():
    nome_alun=request.form['nome_alun']
    port_alun=request.form['port_alun']
    imagem=request.files['img_alun']
    id_foto=str(uuid.uuid4().hex)
    filename=id_foto+nome_alun+'.png'
    imagem.save("static/img/alunos/"+filename)
    conexao = conecta_database()
    conexao.execute('INSERT INTO alunos (nome_alun, port_alun, img_alun) VALUES (?, ?, ?)',(nome_alun, port_alun, filename))
    conexao.commit()
    conexao.close()
    return redirect("/adm")

# ROTA DA PÁGINA DE BUSCA
@app.route("/busca",methods=["post"])
def busca():
    busca=request.form['buscar']
    conexao = conecta_database()
    alunos = conexao.execute('SELECT * FROM alunos WHERE nome_alun LIKE  "%" || ? || "%"',(busca,)).fetchall()
    return render_template("home.html", alunos=alunos)

# ROTA DA PÁGINA ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        alunos = conexao.execute('SELECT * FROM alunos ORDER BY id_alun DESC').fetchall()
        conexao.close()
        return render_template("adm.html", alunos=alunos)
    else:
        return render_template("login.html") 

# ROTA DA PÁGINA ACESSO
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm') #homepage
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

#CRIAR A ROTA DO EDITAR
@app.route("/editalunos/<id_alun>")
def editar(id_alun):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        alunos = conexao.execute('SELECT * FROM alunos WHERE id_alun = ?',(id_alun,)).fetchall()
        conexao.close()
        return render_template("editalunos.html",alunos=alunos)

#CRIAR A ROTA PARA TRATAR A EDIÇÃO
@app.route("/editaralunos", methods=['POST'])
def editprod():
    id_alun = request.form['id_alun']
    nome_alun=request.form['nome_alun']
    port_alun=request.form['port_alun']
    imagem=request.files['img_alun']
    nomeantigo = request.form['img_alun2']
    if imagem:
        imagem.save("static/img/alunos/"+nomeantigo)
    conexao = conecta_database()
    conexao.execute('UPDATE alunos SET nome_alun = ?, port_alun = ? WHERE id_alun = ?',(nome_alun,port_alun, id_alun))
    conexao.commit() #Confirma a alteração no BD
    conexao.close()
    return redirect('/adm') # Vai para a ÁREA ADM

#ROTA DE EXCLUSÃO
@app.route("/excluir/<id>")
def excluir(id):
    #id = int(id)
    conexao = conecta_database()
    conexao.execute('DELETE FROM alunos WHERE id_alun = ?',(id,))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

# FINAL DO CODIGO - EXECUTANDO O SERVIDOR
if __name__ == '__main__':
    app.run(debug=True)
