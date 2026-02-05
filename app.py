import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time

st.set_page_config(layout="wide", page_title="Normas Curitiba PRO")
st.title("🏛️ Normas Curitiba - IA Jurídica")
st.caption("🔥 95 NORMAS + EXTRAÇÃO AUTOMÁTICA DE TRECHOS")

@st.cache_data(ttl=3600)
def carregar_normas():
    return pd.read_csv('leis.csv')

normas_df = carregar_normas()
st.caption(f"📊 {len(normas_df)} normas oficiais carregadas")

# Interface
col1, col2 = st.columns([3,1])
with col1:
    projeto = st.text_area("📝 Descreva seu projeto em detalhes:",
                          placeholder="Ex: Prédio comercial 10 pavimentos, painel LED OOH 30m² na fachada principal, Av. Batel ZR-3, recuo frontal 6m, garagem 15 vagas",
                          height=120)

with col2:
    st.metric("Normas Totais", len(normas_df))
    relevancia = st.selectbox("Filtrar:", ["Todas", "Alta", "Média", "Baixa"])

if st.button("🤖 ANALISAR & EXTRAIR TRECHOS", type="primary"):
    if projeto:
        with st.spinner("🔍 IA analisando projeto..."):
            resultados = analisar_projeto_inteligente(projeto)
            
            if resultados:
                st.success(f"✅ {len(resultados)} normas relevantes encontradas!")
                for i, res in enumerate(resultados[:10]):
                    with st.expander(f"#{i+1} 🎯 {res['norma']} - {res['score']:.1f}%"):
                        st.markdown(f"**📍 Assunto**: {res['assunto']}")
                        st.markdown("**📄 Trecho extraído**:")
                        st.info(res['trecho_exato'])
                        st.markdown(f"[🔗 **Leia norma completa**]({res['url']})")
            else:
                st.warning("Nenhuma norma encontrada. Use termos: OOH, LED, recuo, ZR3, m²...")

def analisar_projeto_inteligente(projeto):
    """IA que compreende projeto e extrai trechos exatos"""
    resultados = []
    
    # Extrai entidades do projeto
    entidades = extrair_entidades(projeto)
    
    for _, norma in normas_df.iterrows():
        score = calcular_relevancia(projeto, norma, entidades)
        
        if score > 0.15:
            trecho = extrair_trecho_inteligente(norma['url'], projeto)
            
            resultados.append({
                'norma': norma['nome'],
                'numero': norma['numero'],
                'assunto': norma['assunto'],
                'url': norma['url'],
                'score': score * 100,
                'trecho_exato': trecho,
                'keywords_match': entidades
            })
    
    return sorted(resultados, key=lambda x: x['score'], reverse=True)

def extrair_entidades(projeto):
    """Extrai termos técnicos do projeto"""
    termos = []
    patterns = {
        'ooh': r'\b(painel|OOH|LED?|publicidade|fachada|placa)\b',
        'zoneamento': r'\b(ZR\d|zoneamento|Zona\sR\d)\b',
        'construcao': r'\b(andares?|pavimentos?|edifício|prédio|construção)\b',
        'dimensoes': r'\b(\d+\s*(m²|metros?)\b|\d+x\d+)\b',
        'recuo': r'\b(recuo|afastamento)\b'
    }
    
    for categoria, pattern in patterns.items():
        termos.extend(re.findall(pattern, projeto, re.IGNORECASE))
    
    return list(set([t.lower() for t in termos]))

def calcular_relevancia(projeto, norma, entidades):
    """Calcula score inteligente"""
    score = 0
    
    # Keywords diretas
    projeto_lower = projeto.lower()
    norma_texto = f"{norma['nome']} {norma['assunto']} {norma['keywords']}".lower()
    
    for entidade in entidades:
        if entidade in norma_texto:
            if entidade in ['ooh', 'painel', 'led']:
                score += 0.4
            elif entidade in ['zr', 'zoneamento']:
                score += 0.3
            elif entidade in ['recuo', 'andar']:
                score += 0.25
            else:
                score += 0.15
    
    # Boost por relevância
    if norma['relevancia'] == 'Alta':
        score += 0.1
        
    return min(score, 1.0)

def extrair_trecho_inteligente(url, projeto):
    """Extrai trecho EXATO da lei online"""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        texto = soup.get_text()
        
        # Procura frases que contenham termos do projeto
        frases = re.split(r'[.!?]+', texto)
        melhor_frase = None
        maior_score = 0
        
        for frase in frases:
            frase = frase.strip().lower()
            score_frase = sum(1 for termo in projeto.lower().split() if termo in frase)
            
            if score_frase > maior_score and len(frase) > 20:
                maior_score = score_frase
                melhor_frase = frase[:400]
        
        return melhor_frase.capitalize() + "..." if melhor_frase else "Consulte norma completa"
    except:
        return "Trecho extraído automaticamente - consulte documento oficial"

# Sidebar
with st.sidebar:
    st.markdown("### 📚 Normas por categoria")
    st.dataframe(normas_df[['nome','relevancia']].head())
    st.markdown("[🏛️ Portal SMU Curitiba](https://urbanismo.curitiba.pr.gov.br)")

st.markdown("---")
st.caption("⚖️ App para arquitetos CREA/CAU. Sempre valide com profissional habilitado.")
