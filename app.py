import os
import streamlit as st
import config
import rag

st.set_page_config(
    page_title="Fiscal do UNO 🟥🟨🟩🟦",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');
    
    /* Esconder o menu de deploy e os três pontinhos do Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Esconder completamente a barra lateral e os controles de colapso */
    [data-testid="stSidebar"], .css-1d391kg, [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    
    /* Cores e Fundo principal (Cinza Escuro / Quase Preto do Layout) */
    .stApp {
        background-color: #0d0f14 !important;
        background-image: none !important;
        color: #f1f2f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Centralizar o bloco principal para ficar com visual profissional e limpo */
    div[data-testid="stAppViewBlockContainer"] {
        max-width: 720px;
        padding-top: 2rem;
        padding-bottom: 5rem;
        margin: auto;
    }
    
    /* Logo customizado do UNO feito em CSS */
    .uno-logo-card {
        width: 48px;
        height: 48px;
        background: #000000;
        border: 2px solid #ffffff;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        transform: rotate(-10deg);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
        flex-shrink: 0;
    }
    .uno-logo-card::before {
        content: "";
        position: absolute;
        width: 40px;
        height: 24px;
        background: #fdf000; /* Yellow oval */
        border-radius: 50%;
        transform: rotate(35deg);
    }
    .uno-logo-text {
        position: relative;
        font-family: 'Outfit', sans-serif;
        color: #ec1c24; /* Red */
        font-weight: 900;
        font-size: 1.1rem;
        text-shadow: -1.5px -1.5px 0 #fff, 1.5px -1.5px 0 #fff, -1.5px 1.5px 0 #fff, 1.5px 1.5px 0 #fff;
        transform: rotate(15deg);
        font-style: italic;
    }
    
    /* Divisor vertical de 4 cores */
    .uno-vertical-divider {
        width: 5px;
        height: 42px;
        background: linear-gradient(180deg, #ec1c24 0%, #ec1c24 25%, #fdf000 25%, #fdf000 50%, #00a651 50%, #00a651 75%, #0054a6 75%, #0054a6 100%);
        border-radius: 3px;
        margin: 0 10px;
        flex-shrink: 0;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #a4a9c2;
        font-size: 1.05rem;
        line-height: 1.5;
        margin-bottom: 2rem;
    }
    
    /* Cartão de Boas-Vindas com borda dividida em 4 cores (conic-gradient) */
    .uno-card {
        background-color: #151821 !important;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 2px solid transparent !important;
        background-image: linear-gradient(#151821, #151821), conic-gradient(from 180deg, #0054a6, #ec1c24, #fdf000, #00a651, #0054a6) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .uno-card-title {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Fontes consultadas */
    .source-box {
        background: rgba(14, 15, 23, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-left: 4px solid #00a651; /* Green border left */
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 1rem;
        font-size: 0.95rem;
        color: #e1e3ed;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .source-badge {
        background-color: #0054a6; /* Blue badge */
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.8rem;
        margin-bottom: 0.8rem;
        display: inline-block;
    }
    
    /* Botões Rápidos de Perguntas Frequentes (Grid do layout) */
    div[data-testid="column"] .stButton>button {
        background-color: #151821 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 400 !important;
        font-size: 0.95rem !important;
        padding: 0.7rem 1rem !important;
        transition: all 0.2s ease !important;
        width: 100%;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        text-align: left !important;
    }
    div[data-testid="column"] .stButton>button div[data-testid="stMarkdownContainer"] p {
        text-align: left !important;
        margin: 0 !important;
        color: #ffffff !important;
    }
    div[data-testid="column"] .stButton>button:hover {
        background-color: #1c1f2b !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-1px) !important;
        box-shadow: none !important;
    }
    
    /* Estilizar o chat input para ter a borda colorida do UNO */
    div[data-testid="stChatInput"] {
        border: 2px solid transparent !important;
        background-image: linear-gradient(#151821, #151821), conic-gradient(from 180deg, #0054a6, #ec1c24, #fdf000, #00a651, #0054a6) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        border-radius: 16px !important;
        background-color: transparent !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Input interno */
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 14px !important;
        font-family: 'Inter', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem; margin-top: 1rem;">
    <div class="uno-logo-card">
        <span class="uno-logo-text">UNO</span>
    </div>
    <div class="uno-vertical-divider"></div>
    <h1 style="margin: 0; color: white; font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 900; line-height: 1;">Fiscal do UNO</h1>
</div>
""", unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="margin-top: 0.2rem; margin-bottom: 1.5rem;">O assistente inteligente para tirar dúvidas rápidas e acabar de vez com as brigas em família!</p>', unsafe_allow_html=True)

st.markdown("""
<div class="uno-card">
    <div class="uno-card-title">🚨 Chega de discussões na mesa de jogo!</div>
    <p style="margin: 0; color: #a4a9c2; font-family: 'Inter', sans-serif; font-size: 0.95rem;">Bem-vindo ao Fiscal do UNO! Tire suas dúvidas sobre as regras...</p>
</div>
""", unsafe_allow_html=True)

api_key = config.get_google_api_key()


indexed = rag.is_indexed()

if not os.path.exists(config.PDF_PATH):
    st.error(f"Erro: O arquivo de regras oficial '{config.PDF_PATH}' não foi encontrado. Por favor, coloque-o na pasta correta.")


if not api_key:
    st.info("💡 Por favor, forneça sua **GOOGLE_API_KEY** na barra lateral para começar a consultar o assistente.")
else:
    
    if not indexed:
        if os.path.exists(config.PDF_PATH):
            st.warning("O índice de regras ainda não foi construído. Construindo índice automaticamente...")
            with st.spinner("Construindo índice local de regras (aguarde)..."):
                try:
                    rag.build_index()
                    st.success("Índice construído com sucesso! Recarregando...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar o índice FAISS: {e}")
                    st.stop()
        else:
            st.stop()

    
    try:
        vectorstore = rag.get_vectorstore()
    except Exception as e:
        st.error(f"Erro ao carregar o banco de vetores FAISS: {e}")
        st.stop()

    
    if 'user_query' not in st.session_state:
        st.session_state['user_query'] = ""
    if 'should_submit' not in st.session_state:
        st.session_state['should_submit'] = False

    
    st.markdown('<h3 style="font-family: \'Outfit\', sans-serif; font-weight: 700; color: white; display: flex; align-items: center; gap: 8px; margin-top: 1.5rem;"><span style="color: #ffaa00;">⚡</span> Perguntas Frequentes</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    if col1.button("Quantas cartas cada jogador recebe?"):
        st.session_state['user_query'] = "Quantas cartas cada jogador recebe no início do jogo?"
        st.session_state['should_submit'] = True
        st.rerun()
    if col2.button("Esqueci de gritar UNO, e agora?"):
        st.session_state['user_query'] = "O que acontece quando o jogador esquece de falar UNO?"
        st.session_state['should_submit'] = True
        st.rerun()
    if col3.button("Como funciona o +4?"):
        st.session_state['user_query'] = "Como funciona a carta especial Coringa Comprar Quatro (+4)?"
        st.session_state['should_submit'] = True
        st.rerun()
    if col4.button("Posso jogar +2 em cima de +2?"):
        st.session_state['user_query'] = "Pode jogar a carta +2 em cima de outra carta +2?"
        st.session_state['should_submit'] = True
        st.rerun()

    
    chat_query = st.chat_input("Digite sua dúvida aqui...")
    
    
    user_query = ""
    if chat_query:
        user_query = chat_query
    elif st.session_state['should_submit']:
        user_query = st.session_state['user_query']
        st.session_state['should_submit'] = False

    
    if user_query:
        with st.spinner("Consultando o manual do UNO (RAG)..."):
            try:
                answer, sources = rag.answer_question(user_query, vectorstore, api_key)
                
                
                st.markdown('<div class="uno-card">', unsafe_allow_html=True)
                st.markdown('<div class="uno-card-title">🔮 Decisão do Fiscal do UNO</div>', unsafe_allow_html=True)
                st.markdown(f"**{answer}**")
                st.markdown('</div>', unsafe_allow_html=True)
                
                
                with st.expander("📖 Trechos consultados (Fontes RAG)"):
                    for i, doc in enumerate(sources):
                        page = doc.metadata.get("page", 0) + 1
                        st.markdown(f"""
                        <div class="source-box">
                            <span class="source-badge">Chunk #{i+1} - Página {page}</span>
                            <p>{doc.page_content}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"Erro ao processar sua pergunta: {e}")
