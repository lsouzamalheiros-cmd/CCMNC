import streamlit as st
from pymongo import MongoClient
import hashlib
import urllib.parse

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(page_title="Sistema Escolar", layout="wide")

# ==============================
# CONEXÃO COM MONGODB (CORRIGIDO)
# ==============================
@st.cache_resource
def conectar():
    usuario = "lsouzamalheiros_db_user"
    senha = urllib.parse.quote_plus("HBpASFoJn9kRK2KG")

    uri = f"mongodb+srv://{usuario}:{senha}@cluster0.zogaia0.mongodb.net/escola?retryWrites=true&w=majority"

    try:
        cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
        cliente.server_info()  # força conexão real
        st.success("✅ Conectado ao MongoDB Atlas!")
        return cliente["escola"]

    except Exception as e:
        st.error(f"❌ Erro na conexão MongoDB: {e}")
        st.stop()

db = conectar()

# ==============================
# CRIAR ADMIN AUTOMÁTICO
# ==============================
def criar_admin_padrao():
    try:
        if db.usuarios.count_documents({}) == 0:
            usuario_padrao = "admin"
            senha_padrao = "admin123"

            senha_hash = hashlib.sha256(senha_padrao.encode()).hexdigest()

            db.usuarios.insert_one({
                "usuario": usuario_padrao,
                "senha": senha_hash,
                "nivel": "admin"
            })

            st.warning("⚠️ Usuário padrão criado: admin / admin123")

    except Exception as e:
        st.error(f"Erro ao criar admin: {e}")

# executa apenas se conectou
if db is not None:
    criar_admin_padrao()

# ==============================
# LOGIN
# ==============================
def login(usuario, senha):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    user = db.usuarios.find_one({"usuario": usuario, "senha": senha_hash})
    return user

# ==============================
# CONTROLE DE SESSÃO
# ==============================
if "logado" not in st.session_state:
    st.session_state.logado = False

# ==============================
# TELA DE LOGIN
# ==============================
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = login(usuario, senha)

        if user:
            st.session_state.logado = True
            st.session_state.usuario = user["usuario"]
            st.session_state.nivel = user["nivel"]
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos")

# ==============================
# SISTEMA PRINCIPAL
# ==============================
else:

    st.sidebar.title("📚 Sistema Escolar")
    st.sidebar.write(f"👤 {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("🏫 Painel Principal")

    st.write("Sistema funcionando perfeitamente 🚀")

    # TESTE DO BANCO
    st.subheader("📊 Teste de conexão")
    try:
        colecoes = db.list_collection_names()
        st.write("📁 Coleções no banco:", colecoes)
    except Exception as e:
        st.error(f"Erro ao listar coleções: {e}")
