import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import base64

# Configuração da página Streamlit
st.set_page_config(
    page_title="IDEB 2023 SP | Diagnóstico Pedagógico, Efeito-Escola & Impacto Social",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Controladores do Tutorial de Boas-Vindas (Onboarding Modal / Carousel)
if 'tutorial_aberto' not in st.session_state:
    st.session_state.tutorial_aberto = True
if 'tutorial_step' not in st.session_state:
    st.session_state.tutorial_step = 1

def proximo_step():
    if st.session_state.tutorial_step < 5:
        st.session_state.tutorial_step += 1

def anterior_step():
    if st.session_state.tutorial_step > 1:
        st.session_state.tutorial_step -= 1

def fechar_tutorial():
    st.session_state.tutorial_aberto = False

def abrir_tutorial():
    st.session_state.tutorial_aberto = True
    st.session_state.tutorial_step = 1

# Estilização CSS Personalizada (Visual Executivo & Moderno)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    :root {
        --primary: #1E3A8A;
        --secondary: #0284C7;
        --accent: #0D9488;
        --bg-card: #F8FAFC;
        --border-card: #E2E8F0;
    }

    /* Card do Tutorial Onboarding */
    .tutorial-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        border: 2px solid #38BDF8;
        border-radius: 16px;
        padding: 24px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
    }
    .tutorial-badge {
        background: #38BDF8;
        color: #0F172A;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .tutorial-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 10px;
        margin-bottom: 8px;
    }
    .tutorial-text {
        font-size: 1rem;
        color: #E2E8F0;
        line-height: 1.6;
    }
    .tutorial-highlight {
        background: rgba(56, 189, 248, 0.15);
        border-left: 4px solid #38BDF8;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
        color: #F0F9FF;
        font-weight: 500;
    }
    .tutorial-step-dots {
        font-size: 1.2rem;
        letter-spacing: 4px;
        color: #38BDF8;
        margin-bottom: 12px;
    }

    /* Cards Executivos */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid var(--border-card);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-subtitle {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 6px;
    }
    .badge-pos {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
    }
    .badge-neg {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
    }

    /* Cards de Recomendação Pedagógica e Comunitária */
    .action-card {
        background: #FFFFFF;
        border-left: 5px solid #0284C7;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .action-card-warning { border-left-color: #F59E0B; }
    .action-card-danger { border-left-color: #EF4444; }
    .action-card-success { border-left-color: #10B981; }

    .action-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 6px;
    }
    .action-tag {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .tag-danger { background-color: #FEE2E2; color: #991B1B; }
    .tag-warning { background-color: #FEF3C7; color: #92400E; }
    .tag-success { background-color: #D1FAE5; color: #065F46; }

    /* Cabeçalho da Aplicação */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%);
        color: white;
        padding: 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 10px 20px -5px rgba(30, 58, 138, 0.3);
    }
    .main-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .main-header p {
        color: #E0F2FE;
        font-size: 1rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dataset consolidado e base de conhecimento de DREs
@st.cache_data
def carregar_dados():
    caminhos = [
        'dados_escolas_dashboard_sp.csv',
        'resultados_efeito_escola_2023.csv',
        os.path.join(os.getcwd(), 'dados_escolas_dashboard_sp.csv')
    ]
    df = None
    for p in caminhos:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, encoding='utf-8-sig')
                break
            except Exception:
                pass
    
    if df is None:
        st.error("Dataset 'dados_escolas_dashboard_sp.csv' não encontrado. Por favor, execute o notebook preditivo primeiro.")
        st.stop()
        
    # Carregar base de conhecimento de DREs se existir
    if os.path.exists('mapeamento_dres_sp.csv'):
        try:
            df_dre_map = pd.read_csv('mapeamento_dres_sp.csv', encoding='utf-8-sig')
            df_dre_map['ID_ESCOLA'] = df_dre_map['ID_ESCOLA'].astype(int)
            df['ID_ESCOLA'] = df['ID_ESCOLA'].astype(int)
            # Atualizar DREs com base no mapa oficial local
            df = df.drop(columns=['DRE'], errors='ignore').merge(df_dre_map[['ID_ESCOLA', 'DRE']], on='ID_ESCOLA', how='left')
        except Exception:
            pass

    return df

df = carregar_dados()

# Garantir colunas essenciais ou valores fallback
colunas_acionaveis = {
    'PC_ROTINA_ESTUDO': 'Rotina de Estudos (>=1h extraclasse)',
    'PC_INCENTIVO_TAREFA': 'Incentivo Familiar para Lição de Casa',
    'PC_INCENTIVO_PRESENCA': 'Cobrança Familiar de Assiduidade',
    'PC_CLAREZA_METAS_DOCENTE': 'Clareza de Metas e Objetivos pelo Docente',
    'PC_SONDAGEM_PREVIA': 'Sondagem Prévia de Conhecimentos',
    'PC_METODOLOGIAS_ATIVAS': 'Uso de Metodologias Ativas / Grupo',
    'PC_INTERESSE_AULAS': 'Interesse dos Alunos pelas Aulas',
    'PC_EXPECTATIVA_DOCENTE': 'Alta Expectativa Docente Percebida',
    'PC_MOTIVACAO_ESTUDOS': 'Motivação Docente para Continuidade',
    'PC_SENTE_SEGURO_ESCOLA': 'Clima de Segurança na Escola'
}

for col in colunas_acionaveis.keys():
    if col not in df.columns:
        df[col] = 0.5

if 'IDEB_PREDITO_SOCIAL' not in df.columns:
    df['IDEB_PREDITO_SOCIAL'] = df['VL_OBSERVADO_2023'] * 0.95
if 'RESIDUO_EFEITO_ESCOLA' not in df.columns:
    df['RESIDUO_EFEITO_ESCOLA'] = df['VL_OBSERVADO_2023'] - df['IDEB_PREDITO_SOCIAL']

# Cabeçalho Principal
st.markdown("""
<div class="main-header">
    <h1>🎓 Diagnóstico Pedagógico, Efeito-Escola & Impacto Social - IDEB SP</h1>
    <p>Rede Municipal de Ensino de São Paulo | Anos Iniciais (5º Ano) | A Escola como Agente de Transformação Social</p>
</div>
""", unsafe_allow_html=True)

# BARRA LATERAL: FILTROS & TUTORIAL
st.sidebar.header("🔍 Navegação & Seleção Escolar")

if st.sidebar.button("💡 Tutorial de Boas-Vindas (Idéia da Ferramenta)", use_container_width=True):
    abrir_tutorial()

st.sidebar.markdown("---")
st.sidebar.subheader("🏫 Seleção da Unidade Escolar")

dres = ['Todas as DREs'] + sorted(list(df['DRE'].dropna().unique()))
dre_selecionada = st.sidebar.selectbox("Filtrar por DRE:", dres)

if dre_selecionada != 'Todas as DREs':
    df_filtrado_dre = df[df['DRE'] == dre_selecionada].copy()
else:
    df_filtrado_dre = df.copy()

opcoes_escolas = df_filtrado_dre.apply(
    lambda r: f"{r['NO_ESCOLA']} (INEP: {int(r['ID_ESCOLA'])})", axis=1
).tolist()

escola_selecionada_str = st.sidebar.selectbox(
    "Selecione ou busque a Escola:",
    opcoes_escolas
)

inep_selecionado = int(re.search(r'INEP:\s*(\d+)', escola_selecionada_str).group(1))
dados_escola = df[df['ID_ESCOLA'] == inep_selecionado].iloc[0]


# ==============================================================================
# TUTORIAL ONBOARDING (MODAL / CAROUSEL DE BOAS-VINDAS)
# ==============================================================================
if st.session_state.tutorial_aberto:
    step = st.session_state.tutorial_step
    dots = " ".join(["●" if i == step else "○" for i in range(1, 6)])
    
    st.markdown(f'<div class="tutorial-step-dots">Etapa {step} de 5 &nbsp;&nbsp;|&nbsp;&nbsp; {dots}</div>', unsafe_allow_html=True)
    
    if step == 1:
        st.markdown("""
        <div class="tutorial-container">
            <span class="tutorial-badge">CARD 1 DE 5: O PROPÓSITO & O DESAFIO SOCIAL</span>
            <div class="tutorial-title">🎯 Por que esta ferramenta existe?</div>
            <div class="tutorial-text">
                Na rede pública, o perfil socioeconômico e territorial das famílias (INSE, DRE, escolaridade materna, recursos em casa) estatisticamente explica cerca de <strong>90% da variação do IDEB</strong>. 
                Se pararmos por aí, parece que a escola está de mãos atadas frente à vulnerabilidade do território.
            </div>
            <div class="tutorial-highlight">
                🚀 <strong>A Visão da Ferramenta:</strong> A escola NÃO é refém do contexto social! Esta ferramenta foi criada para decompor o IDEB e isolar o <strong>Efeito-Escola (Valor Agregado)</strong>, mostrando como a gestão pedagógica e a integração com a comunidade conseguem superar barreiras socioeconômicas.
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif step == 2:
        st.markdown("""
        <div class="tutorial-container">
            <span class="tutorial-badge">CARD 2 DE 5: DECOMPOSIÇÃO ECONOMÉTRICA</span>
            <div class="tutorial-title">📊 Como funciona o IDEB Esperado vs. Real?</div>
            <div class="tutorial-text">
                Nosso modelo de Inteligência Artificial calcula o <strong>IDEB Esperado Social & Territorial</strong> para cada escola, considerando rigorosamente a renda, a DRE, a escolaridade dos pais e a infraestrutura familiar dos alunos.
            </div>
            <div class="tutorial-highlight">
                💡 <strong>O Efeito-Escola (Resíduo):</strong> Se a sua escola atinge um IDEB Real de 6.2, mas a sua expectativa social era 5.8, o seu Efeito-Escola é <strong>+0.40</strong>. Esse saldo positivo é o resultado PURO do trabalho da equipe gestora, dos professores e do engajamento com as famílias!
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif step == 3:
        st.markdown("""
        <div class="tutorial-container">
            <span class="tutorial-badge">CARD 3 DE 5: OS 9 FATORES ACIONÁVEIS</span>
            <div class="tutorial-title">🔎 Diagnóstico nos Fatores sob Controle da Escola</div>
            <div class="tutorial-text">
                Construímos 9 indicadores práticos extraídos das respostas contextuais dos próprios estudantes do 5º ano (SAEB 2023). Eles medem desde o clima escolar e clareza de metas até a rotina de estudos e o incentivo familiar.
            </div>
            <div class="tutorial-highlight">
                🎯 <strong>Gráficos Comparativos:</strong> Através do Gráfico Radar e das Barras de Comparação, você identifica instantaneamente onde a sua escola é referência e quais são os <strong>gargalos prioritários</strong> em relação à sua DRE e à Cidade de São Paulo.
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif step == 4:
        st.markdown("""
        <div class="tutorial-container">
            <span class="tutorial-badge">CARD 4 DE 5: PLANOS DE AÇÃO EM 5 EIXOS</span>
            <div class="tutorial-title">🌱 A Escola como Instrumento de Mudança Social</div>
            <div class="tutorial-text">
                Para evoluir de verdade, a escola precisa atuar dentro da sala de aula E influenciar ativamente o território. Por isso, cada gargalo vem acompanhado de um plano estruturado em <strong>5 Eixos Práticos</strong>:
            </div>
            <div class="tutorial-highlight">
                1. 🚀 <strong>Meta de Curto Prazo</strong> (30 dias)<br>
                2. 🏫 <strong>Formação Coletiva (JEIF/PEA)</strong><br>
                3. 📋 <strong>Instrumentos & Ferramentas Pedagógicas</strong><br>
                4. 👥 <strong>Responsabilidades Internas</strong><br>
                5. 🌐 <strong>Ação de Extensão Comunidade & Família (Impacto Social)</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif step == 5:
        st.markdown("""
        <div class="tutorial-container">
            <span class="tutorial-badge">CARD 5 DE 5: PRONTO PARA COMEÇAR</span>
            <div class="tutorial-title">🚀 Como usar a tela a partir de agora?</div>
            <div class="tutorial-text">
                1. Use o menu lateral esquerdo para selecionar a sua <strong>DRE</strong> e a sua <strong>Escola</strong>.<br>
                2. Explore o <strong>Raio-X da Unidade</strong> com a nota real, a expectativa social e os pontos de atenção.<br>
                3. Abra os cards de recomendação para planejar suas reuniões de JEIF/PEA e Conselho de Escola.<br>
                4. Clique no botão ao final da página para <strong>Baixar o Relatório Executivo Completo</strong> com gráficos visuais em HTML/PDF.
            </div>
            <div class="tutorial-highlight">
                ✨ <em>"A educação não transforma o mundo. A educação muda as pessoas. As pessoas transformam o mundo."</em> (Paulo Freire)
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_t1, col_t2, col_t3 = st.columns([1, 1, 2])
    with col_t1:
        if step > 1:
            st.button("⬅️ Anterior", on_click=anterior_step, use_container_width=True)
    with col_t2:
        if step < 5:
            st.button("Próximo ➡️", on_click=proximo_step, use_container_width=True)
        else:
            st.button("🚀 Iniciar Exploração", on_click=fechar_tutorial, use_container_width=True)
    with col_t3:
        st.button("❌ Fechar Tutorial", on_click=fechar_tutorial, use_container_width=True)

    st.markdown("---")


# ==============================================================================
# TABs PRINCIPAIS DO DASHBOARD
# ==============================================================================
tab_diag, tab_rede = st.tabs([
    "🎯 Diagnóstico Pedagógico, Efeito-Escola & Plano Comunitário",
    "📊 Visão Geral da Rede Municipal & Explicabilidade do Modelo (R²)"
])

# ==============================================================================
# TAB 1: DIAGNÓSTICO PEDAGÓGICO & OPORTUNIDADES DE MELHORIA
# ==============================================================================
with tab_diag:
    st.subheader(f"📌 Raio-X da Unidade: {dados_escola['NO_ESCOLA']}")
    st.caption(f"Código INEP: {int(dados_escola['ID_ESCOLA'])} | DRE: {dados_escola['DRE']}")

    # 1. CARDS EXECUTIVOS
    col1, col2, col3, col4 = st.columns(4)
    
    rank_dre = df_filtrado_dre['VL_OBSERVADO_2023'].rank(ascending=False, method='min')
    pos_dre = int(rank_dre[df_filtrado_dre['ID_ESCOLA'] == inep_selecionado].values[0])
    total_dre = len(df_filtrado_dre)
    
    rank_rede = df['VL_OBSERVADO_2023'].rank(ascending=False, method='min')
    pos_rede = int(rank_rede[df['ID_ESCOLA'] == inep_selecionado].values[0])
    total_rede = len(df)

    res_val = dados_escola['RESIDUO_EFEITO_ESCOLA']
    res_badge = f"<span class='badge-pos'>+{res_val:.2f} (Valor Agregado)</span>" if res_val >= 0 else f"<span class='badge-neg'>{res_val:.2f} (Abaixo do Esperado)</span>"

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">IDEB Real 2023</div>
            <div class="metric-value" style="color:#1E3A8A;">{dados_escola['VL_OBSERVADO_2023']:.2f}</div>
            <div class="metric-subtitle" style="color:#475569;">Nota Observada oficial no INEP</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">IDEB Esperado Social</div>
            <div class="metric-value" style="color:#0284C7;">{dados_escola['IDEB_PREDITO_SOCIAL']:.2f}</div>
            <div class="metric-subtitle" style="color:#475569;">Expectativa pelo Perfil Socio-Territorial</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Efeito-Escola (Resíduo)</div>
            <div class="metric-value">{res_val:+.2f}</div>
            <div class="metric-subtitle">{res_badge}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Classificação DRE</div>
            <div class="metric-value" style="color:#0D9488;">{pos_dre}º <span style="font-size:1.1rem; color:#64748B;">/ {total_dre}</span></div>
            <div class="metric-subtitle" style="color:#475569;">Rede SP: {pos_rede}º lugar de {total_rede}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. PAINEL COMPARATIVO RADAR & BARRA
    col_chart1, col_chart2 = st.columns([1.1, 1])

    eixos = [
        ('PC_ROTINA_ESTUDO', 'Rotina Estudos'),
        ('PC_INCENTIVO_TAREFA', 'Incentivo Tarefa'),
        ('PC_INCENTIVO_PRESENCA', 'Cobrança Presença'),
        ('PC_CLAREZA_METAS_DOCENTE', 'Clareza Metas'),
        ('PC_SONDAGEM_PREVIA', 'Sondagem Prévia'),
        ('PC_METODOLOGIAS_ATIVAS', 'Metodologias Ativas'),
        ('PC_INTERESSE_AULAS', 'Interesse Aulas'),
        ('PC_EXPECTATIVA_DOCENTE', 'Expectativa Docente'),
        ('PC_MOTIVACAO_ESTUDOS', 'Motivação Estudos'),
        ('PC_SENTE_SEGURO_ESCOLA', 'Segurança Escola')
    ]

    categories = [e[1] for e in eixos]
    val_escola = [dados_escola[e[0]] * 100 for e in eixos]
    
    df_dre_curr = df[df['DRE'] == dados_escola['DRE']]
    val_dre = [df_dre_curr[e[0]].mean() * 100 for e in eixos]
    val_rede = [df[e[0]].mean() * 100 for e in eixos]

    with col_chart1:
        st.markdown("### 🕸️ Radar de Desempenho dos Fatores Acionáveis")
        st.caption("Comparação percentual da escola contra a média da DRE e da Rede Municipal")

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=val_escola + [val_escola[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=f"Escola: {dados_escola['NO_ESCOLA'][:25]}...",
            line=dict(color='#1E3A8A', width=3)
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=val_dre + [val_dre[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=f"Média {dados_escola['DRE']}",
            line=dict(color='#0284C7', width=2, dash='dash')
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=val_rede + [val_rede[0]],
            theta=categories + [categories[0]],
            name="Média Rede Municipal SP",
            line=dict(color='#64748B', width=1.5, dash='dot')
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%')
            ),
            showlegend=True,
            height=430,
            margin=dict(l=40, r=40, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_chart2:
        st.markdown("### 📊 Desvio em Relação à Média da Rede (%)")
        st.caption("Indicadores acima de 0% são fortalezas; abaixo de 0% exigem intervenção imediata")

        diffs = [v_e - v_r for v_e, v_r in zip(val_escola, val_rede)]
        df_diff = pd.DataFrame({
            'Indicador': categories,
            'Diferenca': diffs,
            'Cor': ['#10B981' if d >= 0 else '#EF4444' for d in diffs]
        }).sort_values(by='Diferenca', ascending=True)

        fig_bar = px.bar(
            df_diff,
            x='Diferenca',
            y='Indicador',
            orientation='h',
            text=[f"{d:+.1f}%" for d in df_diff['Diferenca']],
            color='Cor',
            color_discrete_map='identity'
        )
        fig_bar.update_layout(
            height=430,
            xaxis_title="Diferença Percentual em relação à Rede SP",
            yaxis_title="",
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=30)
        )
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # 3. PLANO DE AÇÃO ESCOLAR & IMPACTO SOCIAL COMUNITÁRIO (5 EIXOS)
    st.markdown("### 🛠️ Plano de Ação Estruturado: Escola como Agente de Mudança Social")
    st.caption("Recomendações acionáveis divididas em 5 eixos práticos: Pedagogia Interna + Extensão Comunitária & Família")

    gargalos_identificados = []
    pontos_fortes = []

    for var, nome in eixos:
        tx_escola = dados_escola[var]
        tx_rede_avg = df[var].mean()
        diff = tx_escola - tx_rede_avg
        
        if diff < -0.03:
            gargalos_identificados.append((var, nome, tx_escola, tx_rede_avg, diff))
        elif diff > 0.05:
            pontos_fortes.append((var, nome, tx_escola, tx_rede_avg, diff))

    if res_val >= 0.25:
        st.markdown(f"""
        <div class="action-card action-card-success">
            <span class="action-tag tag-success">🏆 Case de Sucesso Pedagógico & Comunitário</span>
            <div class="action-title">Escola de Alto Valor Agregado (Efeito-Escola: +{res_val:.2f})</div>
            <div class="action-desc">
                Esta unidade escolar supera significativamente a expectativa de desempenho calculada pelo seu perfil socioeconômico e territorial. 
                <strong>Recomendação de Gestão:</strong> Mapear e documentar as práticas de gestão pedagógica, clima escolar e acolhimento comunitário como referência e boas práticas para disseminação na DRE <em>{dados_escola['DRE']}</em>.
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not gargalos_identificados:
        st.success("🎉 **Excelente Desempenho Pedagógico e Social!** A escola encontra-se alinhada ou acima da média da rede municipal em todos os eixos pedagógicos e comunitários investigados.")
    else:
        st.markdown(f"Foram identificados **{len(gargalos_identificados)} gargalos prioritários** para intervenção pedagógica e social:")
        
        recomendacoes_map = {
            'PC_ROTINA_ESTUDO': {
                'titulo': 'Ampliação da Autonomia e Rotina de Estudos Extraclasse',
                'tag': 'Acompanhamento de Aprendizagem',
                'classe': 'action-card-warning',
                'tag_cls': 'tag-warning',
                'curto_prazo': 'Implantar o Diário de Estudos Autorregulados no 5º ano e instituir rotina de checagem diária de tarefas.',
                'jeif_pea': 'Oficina em JEIF/PEA sobre orientação de lição de casa como extensão pedagógica e não apenas punição.',
                'ferramentas': 'Guia Semanal de Tarefas, Tabela de Planejamento do Aluno e Cantinho dos Estudos.',
                'responsaveis': 'Coordenação Pedagógica + Professores Regentes + Famílias.',
                'comunidade': 'Oficinas de Cantinho dos Estudos para Pais: Sensibilizar famílias em vulnerabilidade sobre a criação de um espaço e horário fixo sem telas para estudo em casa, articulando parceria com bibliotecas comunitárias e centros de acolhimento do bairro.'
            },
            'PC_CLAREZA_METAS_DOCENTE': {
                'titulo': 'Formação Continuada: Explicitação de Objetivos e Rubricas de Aprendizagem',
                'tag': 'Gestão Pedagógica & JEIF/PEA',
                'classe': 'action-card-danger',
                'tag_cls': 'tag-danger',
                'curto_prazo': 'Afixar na lousa/mural da sala a "Meta da Aula" e o "O que vamos aprender hoje" no início de cada aula.',
                'jeif_pea': 'Pauta formativa em JEIF/PEA focada em Planejamento Reverso e elaboração compartilhada de Rubricas de Avaliação.',
                'ferramentas': 'Mural "O que aprendi hoje?", Ficha de Autoavaliação do Aluno e Matriz de Objetivos por Sequência Didática.',
                'responsaveis': 'Coordenador Pedagógico + Docentes Regentes.',
                'comunidade': 'Mural Comunitário de Aprendizagens: Expor os objetivos didáticos e as produções dos alunos no portão/entrada da escola e em boletins digitais da comunidade (WhatsApp/Redes), valorizando o avanço acadêmico perante as famílias do bairro.'
            },
            'PC_SONDAGEM_PREVIA': {
                'titulo': 'Fortalecimento da Avaliação Diagnóstica e Mapeamento de Conhecimento Prévio',
                'tag': 'Avaliação Diagnóstica',
                'classe': 'action-card-warning',
                'tag_cls': 'tag-warning',
                'curto_prazo': 'Aplicar sondagens curtas de 5 minutos (quiz/perguntas disparadoras) antes de introduzir novos tópicos.',
                'jeif_pea': 'Análise coletiva de dados de sondagens em Língua Portuguesa e Matemática para reagrupamento de estudantes.',
                'ferramentas': 'Mapas de Aprendizagem da Turma, Fichas de Sondagem de Leitura e Escrita e Registros de Erros Construtivos.',
                'responsaveis': 'Docentes + Coordenação Pedagógica.',
                'comunidade': 'Valorização dos Saberes Locais no Currículo: Incluir aspectos da história, cultura e contexto socioeconômico do bairro nas sondagens e sequências didáticas, convidando moradores e lideranças locais para rodas de conversa com os alunos.'
            },
            'PC_INCENTIVO_PRESENCA': {
                'titulo': 'Protocolos Locais de Busca Ativa e Valorização da Assiduidade Escolar',
                'tag': 'Combate ao Absenteísmo & Busca Ativa',
                'classe': 'action-card-danger',
                'tag_cls': 'tag-danger',
                'curto_prazo': 'Acionar contato direto com a família no 2º dia consecutivo de falta e emitir alerta de assiduidade.',
                'jeif_pea': 'Discussão dos fatores territoriais de absenteísmo e elaboração do plano focal de busca ativa escolar.',
                'ferramentas': 'Ficha FICAI/Busca Ativa Local, Mural da Presença Premiada e Painel Mensal de Assiduidade.',
                'responsaveis': 'Direção Escolar + Assistente de Direção + Conselho de Escola + Famílias.',
                'comunidade': 'Rede Territorial de Busca Ativa Escolar: Mapear barreiras de deslocamento e problemas sociais no entorno da escola, articulando parcerias estratégicas com CRAS, Postos de Saúde (UBS), Agentes Comunitários e lideranças comunitárias para acompanhar famílias vulneráveis e zerar o abandono.'
            },
            'PC_INCENTIVO_TAREFA': {
                'titulo': 'Parceria Família-Escola e Corresponsabilidade nas Lições de Casa',
                'tag': 'Engajamento Familiar',
                'classe': 'action-card-warning',
                'tag_cls': 'tag-warning',
                'curto_prazo': 'Realizar reunião temática com responsáveis sobre a importância do incentivo positivo às tarefas escolares.',
                'jeif_pea': 'Elaboração de comunicados pedagógicos acessíveis e informativos aos pais sem jargões acadêmicos.',
                'ferramentas': 'Agenda Escolar Interativa, Diário Família-Escola e Canal direto de dúvidas no contraturno.',
                'responsaveis': 'Equipe Gestora + Professores + Responsáveis.',
                'comunidade': 'Encontros de Parentalidade Positiva: Promover encontros mensais acolhedores com os responsáveis (em horários flexíveis), com apoio de profissionais da saúde/assistência social, orientando os pais sobre como fortalecer os vínculos afetivos e a vida escolar dos filhos.'
            },
            'PC_EXPECTATIVA_DOCENTE': {
                'titulo': 'Cultura de Altas Expectativas Acadêmicas e Mentalidade de Crescimento',
                'tag': 'Clima Escolar & Vínculo',
                'classe': 'action-card-warning',
                'tag_cls': 'tag-warning',
                'curto_prazo': 'Instituir rodadas semanais de devolutivas individuais encorajadoras com elogios focados no esforço.',
                'jeif_pea': 'Formação sobre Efeito Pigmaleão, Estereótipos de Aprendizagem e Mentalidade de Crescimento (Growth Mindset).',
                'ferramentas': 'Fichas de Devolutiva Formativa, Quadro dos Avanços Pessoais e Tutoria Pedagógica entre Pares.',
                'responsaveis': 'Docentes + Coordenação Pedagógica.',
                'comunidade': 'Campanha "Eu Acredito no Seu Futuro": Promover feiras de profissões e palestras inspiradoras com moradores do próprio bairro e ex-alunos da escola municipal que cursaram universidade ou se destacaram no mercado, construindo referências reais de sucesso local.'
            },
            'PC_MOTIVACAO_ESTUDOS': {
                'titulo': 'Incentivo à Continuidade dos Estudos e Projeto de Vida no 5º Ano',
                'tag': 'Motivação Discente',
                'classe': 'action-card-warning',
                'tag_cls': 'tag-warning',
                'curto_prazo': 'Organizar o "Dia das Profissões e dos Sonhos" trazendo trajetórias inspiradoras de ex-alunos da rede.',
                'jeif_pea': 'Planejamento de sequências didáticas interdisciplinares conectando conteúdos escolares com aplicações reais.',
                'ferramentas': 'Árvore dos Sonhos, Portfólio de Conquistas e Visitas Guiadas de transição para o 6º ano.',
                'responsaveis': 'Professores + Coordenação Pedagógica + Convidados da comunidade.',
                'comunidade': 'Projetos de Intervenção Comunitária: Engajar os estudantes em projetos práticos de impacto social no bairro (horta comunitária, revitalização de praças, campanhas ambientais), demonstrando a aplicação real do conhecimento escolar na transformação da comunidade.'
            },
            'PC_SENTE_SEGURO_ESCOLA': {
                'titulo': 'Fortalecimento da Segurança Afetiva, Acolhimento e Convivência Ética',
                'tag': 'Convivência Ética & Clima',
                'classe': 'action-card-danger',
                'tag_cls': 'tag-danger',
                'curto_prazo': 'Realizar Assembleia de Classe para pactuação de combinados de convivência e acolhimento socioemocional.',
                'jeif_pea': 'Formação sobre Justiça Restaurativa, Mediação de Conflitos e Combate ao Bullying no ambiente escolar.',
                'ferramentas': 'Caixa de Sugestões/Desabafos, Comissão de Mediação de Pares e Protocolo Restaurativo.',
                'responsaveis': 'Comissão de Mediação + Direção + Professores Regentes + Estudantes.',
                'comunidade': 'Pacto Territorial por um Entorno Seguro (Escola Aberta & Cultura de Paz): Articular com comerciantes locais, associação de moradores e Conselho Tutelar um corredor de proteção escolar ("Caminho Seguro"), abrindo a escola nos finais de semana para atividades culturais e esportivas comunitárias.'
            },
            'PC_METODOLOGIAS_ATIVAS': {
                'titulo': 'Estímulo a Trabalhos Colaborativos e Aprendizagem entre Pares',
                'tag': 'Práticas Pedagógicas Inovadoras',
                'classe': 'action-card-warning',
                'tag_cls': 'tag-warning',
                'curto_prazo': 'Reorganizar as carteiras em duplas/trios de trabalho produtivo com papéis claros atribuídos aos alunos.',
                'jeif_pea': 'Oficina prática de Metodologias Ativas (Aprendizagem Baseada em Problemas, Rotação por Estações).',
                'ferramentas': 'Guia de Papéis no Grupo (Relator, Cronometrista, Líder), Roteiro de Estações de Aprendizagem.',
                'responsaveis': 'Professores Regentes + Coordenação Pedagógica.',
                'comunidade': 'Feiras de Saberes Compartilhados na Comunidade: Organizar exposições e feiras de ciências em praças públicas ou centros comunitários do bairro, onde os próprios alunos apresentam suas pesquisas em grupo para os moradores, elevando a autoconfiança e o orgulho comunitário.'
            }
        }

        for var, nome, tx_e, tx_r, diff in gargalos_identificados:
            rec = recomendacoes_map.get(var, {
                'titulo': f'Melhoria no indicador {nome}',
                'tag': 'Gargalo Pedagógico',
                'classe': 'action-card-warning',
                'tag_cls': 'tag-warning',
                'curto_prazo': 'Implementar acompanhamento direto com a coordenação pedagógica.',
                'jeif_pea': 'Pauta formativa nos horários coletivos sobre o indicador.',
                'ferramentas': 'Fichas de acompanhamento semanal.',
                'responsaveis': 'Equipe Gestora e Docentes.',
                'comunidade': 'Articular reuniões de sensibilização com os responsáveis e parcerias com lideranças comunitárias do bairro.'
            })
            
            with st.expander(f"🔴 {rec['titulo']} (Escola: {tx_e*100:.1f}% vs. Rede: {tx_r*100:.1f}%)", expanded=True):
                st.markdown(f"""
                <span class="action-tag {rec['tag_cls']}">{rec['tag']}</span>
                <br>
                <table style="width:100%; font-size:0.9rem; border-collapse:collapse; margin-top:8px;">
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="width:28%; font-weight:bold; color:#1E3A8A; padding:8px 0;">🚀 Meta de Curto Prazo (30 dias):</td><td style="padding:8px 0;">{rec['curto_prazo']}</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="font-weight:bold; color:#0284C7; padding:8px 0;">🏫 Formação Coletiva (JEIF/PEA):</td><td style="padding:8px 0;">{rec['jeif_pea']}</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="font-weight:bold; color:#0D9488; padding:8px 0;">📋 Ferramentas & Instrumentos:</td><td style="padding:8px 0;">{rec['ferramentas']}</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="font-weight:bold; color:#475569; padding:8px 0;">👥 Responsabilidades Internas:</td><td style="padding:8px 0;">{rec['responsaveis']}</td></tr>
                    <tr><td style="font-weight:bold; color:#B45309; padding:8px 0;">🌐 Extensão Comunidade & Família (Impacto Social):</td><td style="padding:8px 0; font-weight:500; color:#1E293B;">{rec['comunidade']}</td></tr>
                </table>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # 4. EXPORTAÇÃO DO RELATÓRIO EXECUTIVO PDF/HTML COM GRÁFICOS VISUAIS
    st.markdown("### 📄 Exportação do Sumário Executivo de Diagnóstico & Impacto Social (com Gráficos)")
    
    # Gerar representação HTML dos gráficos Plotly interativos para incluir no arquivo de relatório baixado
    fig_radar_html = fig_radar.to_html(include_plotlyjs='cdn', full_html=False)
    fig_bar_html = fig_bar.to_html(include_plotlyjs='cdn', full_html=False)

    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Relatório de Diagnóstico Pedagógico - {dados_escola['NO_ESCOLA']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; color: #1E293B; line-height: 1.5; }}
            h1 {{ color: #1E3A8A; font-size: 22px; margin-bottom: 4px; }}
            .subtitle {{ color: #64748B; font-size: 13px; margin-bottom: 20px; }}
            .card-grid {{ display: flex; gap: 15px; margin-bottom: 25px; }}
            .card {{ background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 18px; border-radius: 8px; flex: 1; text-align: center; }}
            .card-title {{ font-size: 11px; color: #64748B; text-transform: uppercase; font-weight: bold; }}
            .card-val {{ font-size: 20px; font-weight: bold; color: #0F172A; margin-top: 4px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }}
            th, td {{ border: 1px solid #CBD5E1; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #F1F5F9; color: #1E3A8A; font-weight: bold; }}
            .rec-box {{ background: #EFF6FF; border-left: 4px solid #0284C7; padding: 12px 16px; margin-top: 14px; font-size: 12px; border-radius: 4px; }}
            .comunidade-tag {{ color: #B45309; font-weight: bold; margin-top: 6px; }}
            .chart-section {{ margin: 25px 0; padding: 15px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <h1>🎓 SUMÁRIO EXECUTIVO - DIAGNÓSTICO PEDAGÓGICO & IMPACTO SOCIAL IDEB 2023</h1>
        <div class="subtitle">Unidade Escolar: <strong>{dados_escola['NO_ESCOLA']}</strong> | INEP: {int(dados_escola['ID_ESCOLA'])} | DRE: {dados_escola['DRE']}</div>
        
        <div class="card-grid">
            <div class="card"><div class="card-title">IDEB Real 2023</div><div class="card-val">{dados_escola['VL_OBSERVADO_2023']:.2f}</div></div>
            <div class="card"><div class="card-title">IDEB Esperado Social</div><div class="card-val">{dados_escola['IDEB_PREDITO_SOCIAL']:.2f}</div></div>
            <div class="card"><div class="card-title">Efeito-Escola (Resíduo)</div><div class="card-val">{res_val:+.2f}</div></div>
            <div class="card"><div class="card-title">Posição na DRE</div><div class="card-val">{pos_dre}º / {total_dre}</div></div>
        </div>

        <h3>1. VISUALIZAÇÃO GRÁFICA DOS INDICADORES DA ESCOLA</h3>
        <div class="chart-section">
            <h4>🕸️ Radar de Desempenho dos Fatores Acionáveis</h4>
            {fig_radar_html}
        </div>
        <div class="chart-section">
            <h4>📊 Desvio em Relação à Média da Rede Municipal (%)</h4>
            {fig_bar_html}
        </div>

        <h3>2. BALANÇO DE INDICADORES DO FATOR ESCOLA</h3>
        <table>
            <thead>
                <tr>
                    <th>Indicador Acionável</th>
                    <th>Escola (%)</th>
                    <th>Média DRE (%)</th>
                    <th>Média Rede Municipal (%)</th>
                    <th>Status Comparativo</th>
                </tr>
            </thead>
            <tbody>
    """
    for var, nome in eixos:
        v_e = dados_escola[var] * 100
        v_d = df_dre_curr[var].mean() * 100
        v_r = df[var].mean() * 100
        st_txt = "Abaixo da Média" if v_e < v_r else "Alinhado/Acima"
        html_report += f"<tr><td>{nome}</td><td>{v_e:.1f}%</td><td>{v_d:.1f}%</td><td>{v_r:.1f}%</td><td>{st_txt}</td></tr>"

    html_report += """
            </tbody>
        </table>

        <h3>3. PLANO DE AÇÃO EM 5 EIXOS (PEDAGOGIA + EXTENSÃO COMUNITÁRIA)</h3>
    """
    if gargalos_identificados:
        for var, nome, tx_e, tx_r, diff in gargalos_identificados:
            rec_item = recomendacoes_map.get(var, {})
            comunidade_txt = rec_item.get('comunidade', 'Promover articulação com as famílias e lideranças comunitárias.')
            html_report += f"""
            <div class="rec-box">
                <strong>🔴 Gargalo Identificado: {nome} (Escola: {tx_e*100:.1f}% vs. Rede: {tx_r*100:.1f}%)</strong><br>
                <strong>• Meta Curto Prazo:</strong> {rec_item.get('curto_prazo', 'Pauta pedagógica focal.')}<br>
                <strong>• Formação JEIF/PEA:</strong> {rec_item.get('jeif_pea', 'Reuniões coletivas.')}<br>
                <div class="comunidade-tag">🌐 Ação Comunidade & Família:</div> {comunidade_txt}
            </div>
            """
    else:
        html_report += "<p>Sem gargalos prioritários detectados. Unidade com desempenho exemplar na rede.</p>"

    html_report += """
        <br><br>
        <div style="font-size: 10px; color: #94A3B8; text-align: center;">Relatório gerado automaticamente pelo Sistema de Inteligência Preditiva do IDEB SP - Univesp 2023/2026.</div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_report.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="Relatorio_Diagnostico_{int(dados_escola["ID_ESCOLA"])}.html" class="button" style="background-color:#1E3A8A; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:600;">📥 Baixar Relatório Executivo Completo com Gráficos (HTML/PDF)</a>'
    st.markdown(href, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: VISÃO GERAL DA REDE & MODELO PREDITIVO
# ==============================================================================
with tab_rede:
    st.subheader("🌐 Visão Geral da Rede Municipal de São Paulo & Explicabilidade do Modelo")
    st.caption("Detalhamento dos Fatores Sociais & Territoriais DRE (90,78% de R²) e Análise do Efeito-Escola (Resíduo Preditivo)")

    # CAIXA EXPLICATIVA DOS FATORES SOCIAIS E TERRITORIAIS (DRE)
    st.markdown("""
    <div style="background-color: #EFF6FF; border-left: 5px solid #1E3A8A; padding: 18px; border-radius: 8px; margin-bottom: 20px;">
        <h4 style="color: #1E3A8A; margin-top:0;">📚 Quais são os Fatores Sociais e Territoriais (DRE) que explicam ~90,78% do IDEB?</h4>
        <p style="font-size: 0.95rem; color: #334155; line-height: 1.6;">
            O modelo <strong>Baseline Socio-Territorial</strong> utiliza a base de conhecimento das 13 DREs e 14 variáveis socioeconômicas e familiares do <strong>INSE/INEP</strong> e do questionário contextual do <strong>SAEB 2023</strong>:
        </p>
        <ul style="font-size: 0.9rem; color: #1E293B; line-height: 1.6;">
            <li><strong>Território & DRE (Vulnerabilidade Espacial):</strong> Mapeamento oficial de cada escola entre as 13 DREs da cidade para incorporar o contexto territorial e de vulnerabilidade periférica.</li>
            <li><strong>Indicador Socioeconômico (INSE):</strong> % de estudantes nas faixas de Vulnerabilidade, Médio-Baixo, Médio-Alto e Alta Renda.</li>
            <li><strong>Escolaridade dos Pais:</strong> % de Mães com Baixa Escolaridade (Fundamental Incompleto), % de Pais com Baixa Escolaridade e % de Mães com Ensino Superior Completo.</li>
            <li><strong>Infraestrutura Familiar & Tecnologia:</strong> % de famílias Sem Computador, % com acesso a Wi-Fi em Casa e % com Celular com Internet.</li>
            <li><strong>Estrutura Familiar & Demografia:</strong> % de Famílias Grandes (5+ moradores), Quantidade de Alunos Avaliados no INSE, % de Alunos Pretos/Pardos e % Sexo Feminino.</li>
        </ul>
        <p style="font-size: 0.9rem; color: #0F172A; font-weight: 600; margin-bottom: 0;">
            💡 <em>Por que considerar a DRE como fator socio-territorial?</em> A localização geográfica reflete a infraestrutura do bairro, acesso a transporte, saneamento e equipamentos públicos de cultura. O modelo ajusta a expectativa inicial por DRE para isolar o que é <strong>mérito exclusivo da gestão escolar e pedagógica (+1,29% de ganho líquido)</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_macro1, col_macro2 = st.columns([1.3, 1])

    with col_macro1:
        st.markdown("### IDEB Real vs. IDEB Esperado Social")
        st.caption("Tom Azul: Escolas que superam a expectativa | Tom Vermelho/Laranja: Escolas abaixo da expectativa")

        # Escala de cores invertida conforme pedido: Azul para resíduo positivo (superam) e Vermelho/Laranja para resíduo negativo (abaixo)
        custom_colorscale = [
            [0.0, '#EF4444'],   # Vermelho Intenso (Abaixo)
            [0.4, '#F97316'],   # Laranja (Abaixo Leve)
            [0.5, '#CBD5E1'],   # Cinza Neutro (Na Expectativa)
            [0.6, '#0284C7'],   # Azul Claro (Supera)
            [1.0, '#1E3A8A']    # Azul Escuro Intenso (Supera Muito)
        ]

        fig_scatter = px.scatter(
            df,
            x='IDEB_PREDITO_SOCIAL',
            y='VL_OBSERVADO_2023',
            color='RESIDUO_EFEITO_ESCOLA',
            size='QTD_ALUNOS_INSE',
            hover_name='NO_ESCOLA',
            hover_data=['DRE', 'VL_OBSERVADO_2023', 'IDEB_PREDITO_SOCIAL', 'RESIDUO_EFEITO_ESCOLA'],
            color_continuous_scale=custom_colorscale,
            labels={
                'IDEB_PREDITO_SOCIAL': 'IDEB Esperado pelo Perfil Socio-Territorial',
                'VL_OBSERVADO_2023': 'IDEB Observado Real 2023',
                'RESIDUO_EFEITO_ESCOLA': 'Efeito-Escola (Resíduo)'
            }
        )
        fig_scatter.add_shape(
            type="line", x0=4.0, y0=4.0, x1=7.5, y1=7.5,
            line=dict(color="#475569", width=2, dash="dash")
        )
        fig_scatter.update_layout(height=480)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_macro2:
        st.markdown("### Top 10 Escolas em Valor Agregado")
        st.caption("Unidades com maior Efeito-Escola positivo (Superação do Perfil Social)")
        
        # Colunas organizadas conforme pedido do usuário: Nome da Escola, DRE, Valor Agregado
        top10_df = df.sort_values(by='RESIDUO_EFEITO_ESCOLA', ascending=False).head(10)[
            ['NO_ESCOLA', 'DRE', 'RESIDUO_EFEITO_ESCOLA']
        ].copy()
        
        top10_df.columns = ['Nome da Escola', 'DRE', 'Valor Agregado']
        st.dataframe(
            top10_df.style.format({
                'Valor Agregado': '+{:.2f}'
            }).background_gradient(subset=['Valor Agregado'], cmap='Blues'),
            use_container_width=True,
            height=430
        )

    st.markdown("---")
    
    st.markdown("### 🏬 Comparativo do Efeito-Escola Médio por Diretoria Regional de Educação (DRE)")
    df_dre_summary = df.groupby('DRE').agg({
        'ID_ESCOLA': 'count',
        'VL_OBSERVADO_2023': 'mean',
        'IDEB_PREDITO_SOCIAL': 'mean',
        'RESIDUO_EFEITO_ESCOLA': 'mean'
    }).reset_index()
    
    df_dre_summary.rename(columns={
        'ID_ESCOLA': 'Qtd Escolas',
        'VL_OBSERVADO_2023': 'IDEB Real Médio',
        'IDEB_PREDITO_SOCIAL': 'IDEB Esperado Médio',
        'RESIDUO_EFEITO_ESCOLA': 'Efeito-Escola Médio'
    }, inplace=True)
    
    fig_dre_bar = px.bar(
        df_dre_summary.sort_values(by='Efeito-Escola Médio', ascending=True),
        x='Efeito-Escola Médio',
        y='DRE',
        orientation='h',
        color='Efeito-Escola Médio',
        color_continuous_scale='Tealgrn',
        labels={'Efeito-Escola Médio': 'Saldo do Efeito-Escola Médio'}
    )
    fig_dre_bar.update_layout(height=400)
    st.plotly_chart(fig_dre_bar, use_container_width=True)

st.markdown("---")
st.caption("Projetos Integradores UNIVESP 2023/2026 | Base de Conhecimento DRE & Sistema de Inteligência Preditiva do IDEB SP")
