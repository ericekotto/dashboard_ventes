import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processing import *
import os

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Ventes - Électronique & Plus",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un style attractif
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    h1 {
        color: #FF4B4B;
        text-align: center;
        font-size: 3em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2 {
        color: #FAFAFA;
        border-bottom: 3px solid #FF4B4B;
        padding-bottom: 10px;
    }
    h3 {
        color: #A0A0A0;
    }
    .dataframe {
        font-size: 14px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# Chargement des données avec cache
@st.cache_data
def load_data():
    file_path = 'data/data_dashboard_large.xlsx'
    if os.path.exists(file_path):
        return load_and_clean_data(file_path)
    else:
        st.error(f"❌ Fichier non trouvé : {file_path}")
        return None

# Charger les données
df = load_data()

if df is not None:
    # Titre principal
    st.markdown("<h1>📊 Dashboard Ventes - Électronique & Plus</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ============================
    # SIDEBAR - FILTRES
    # ============================
    st.sidebar.title("🎛️ Filtres Dynamiques")
    st.sidebar.markdown("---")
    
    # Filtre par magasin
    magasins = ['Tous'] + sorted(df['Magasin'].unique().tolist())
    selected_magasin = st.sidebar.selectbox("🏪 Sélectionner un Magasin", magasins)
    
    # Filtre par catégorie
    categories = ['Toutes'] + sorted(df['Categorie_Produit'].unique().tolist())
    selected_categorie = st.sidebar.selectbox("📦 Sélectionner une Catégorie", categories)
    
    # Filtre par mode de paiement
    if 'Mode_Paiement' in df.columns:
        modes_paiement = ['Tous'] + sorted(df['Mode_Paiement'].unique().tolist())
        selected_mode = st.sidebar.selectbox("💳 Mode de Paiement", modes_paiement)
    else:
        selected_mode = 'Tous'
    
    # Filtre par date
    if 'Date_Transaction' in df.columns:
        date_min = df['Date_Transaction'].min().date()
        date_max = df['Date_Transaction'].max().date()
        date_range = st.sidebar.date_input(
            "📅 Période",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max
        )
    
    # Appliquer les filtres
    df_filtered = df.copy()
    
    if selected_magasin != 'Tous':
        df_filtered = df_filtered[df_filtered['Magasin'] == selected_magasin]
    
    if selected_categorie != 'Toutes':
        df_filtered = df_filtered[df_filtered['Categorie_Produit'] == selected_categorie]
    
    if selected_mode != 'Tous' and 'Mode_Paiement' in df.columns:
        df_filtered = df_filtered[df_filtered['Mode_Paiement'] == selected_mode]
    
    if 'Date_Transaction' in df.columns and len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['Date_Transaction'].dt.date >= date_range[0]) &
            (df_filtered['Date_Transaction'].dt.date <= date_range[1])
        ]
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 **{len(df_filtered)}** transactions affichées sur **{len(df)}**")
    
    # ============================
    # ONGLETS PRINCIPAUX
    # ============================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Vue d'Ensemble",
        "🏪 Analyse par Magasin",
        "📦 Catégories de Produits",
        "💳 Modes de Paiement",
        "⭐ Satisfaction Client"
    ])
    
    # ============================
    # ONGLET 1 : VUE D'ENSEMBLE
    # ============================
    with tab1:
        st.header("📊 Vue d'Ensemble - KPIs Globaux")
        
        # KPIs
        kpis = get_kpi_metrics(df_filtered)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total des Ventes",
                value=f"{kpis['total_ventes']:,.0f} €",
                delta=f"{kpis['total_ventes']/len(df_filtered):.2f} €/trans"
            )
        
        with col2:
            st.metric(
                label="🛒 Nombre de Transactions",
                value=f"{kpis['nb_transactions']:,}",
                delta=f"{(kpis['nb_transactions']/len(df)*100):.1f}% du total"
            )
        
        with col3:
            st.metric(
                label="📊 Montant Moyen",
                value=f"{kpis['montant_moyen']:.2f} €"
            )
        
        with col4:
            st.metric(
                label="⭐ Satisfaction Moyenne",
                value=f"{kpis['satisfaction_moyenne']:.2f}/5"
            )
        
        st.markdown("---")
        
        # Graphique des ventes quotidiennes
        st.subheader("📈 Évolution des Ventes Quotidiennes")
        
        daily_sales = get_daily_sales(df_filtered)
        if daily_sales is not None:
            fig = px.line(
                daily_sales,
                x='Date',
                y='Ventes',
                title='Ventes Quotidiennes',
                markers=True
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis_title='Date',
                yaxis_title='Ventes (€)',
                hovermode='x unified'
            )
            fig.update_traces(
                line=dict(color='#FF4B4B', width=3),
                marker=dict(size=8, color='#FF4B4B')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Histogramme des ventes
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribution des Montants")
            fig = px.histogram(
                df_filtered,
                x='Montant',
                nbins=30,
                title='Distribution des Montants de Transaction'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📦 Quantités Vendues")
            fig = px.histogram(
                df_filtered,
                x='Quantite',
                nbins=20,
                title='Distribution des Quantités'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ============================
    # ONGLET 2 : ANALYSE PAR MAGASIN
    # ============================
    with tab2:
        st.header("🏪 Analyse par Magasin")
        
        store_data = get_sales_by_store(df_filtered)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥧 Répartition des Ventes par Magasin")
            fig = px.pie(
                store_data,
                values='Ventes_Totales',
                names='Magasin',
                title='Part de Marché par Magasin',
                hole=0.4
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Montant Moyen par Magasin")
            fig = px.bar(
                store_data,
                x='Magasin',
                y='Montant_Moyen',
                title='Montant Moyen par Transaction',
                color='Montant_Moyen',
                color_continuous_scale='Reds'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Tableau détaillé
        st.subheader("📋 Tableau Récapitulatif par Magasin")
        st.dataframe(
            store_data.style.highlight_max(axis=0, color='#FF4B4B'),
            use_container_width=True,
            height=300
        )
        
        # Graphique barres empilées
        st.subheader("📊 Ventes par Magasin et Catégorie")
        store_category = df_filtered.groupby(['Magasin', 'Categorie_Produit'])['Montant'].sum().reset_index()
        fig = px.bar(
            store_category,
            x='Magasin',
            y='Montant',
            color='Categorie_Produit',
            title='Ventes par Magasin et Catégorie',
            barmode='stack'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============================
    # ONGLET 3 : CATÉGORIES
    # ============================
    with tab3:
        st.header("📦 Analyse des Catégories de Produits")
        
        category_data = get_sales_by_category(df_filtered)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Quantités Vendues par Catégorie")
            fig = px.bar(
                category_data,
                x='Categorie_Produit',
                y='Quantite_Totale',
                title='Quantités Totales par Catégorie',
                color='Quantite_Totale',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💰 Ventes par Catégorie")
            fig = px.pie(
                category_data,
                values='Ventes_Totales',
                names='Categorie_Produit',
                title='Répartition du CA par Catégorie'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Graphique empilé par magasin et catégorie
        st.subheader("📊 Montants des Ventes par Catégorie et Magasin")
        store_category = df_filtered.groupby(['Categorie_Produit', 'Magasin'])['Montant'].sum().reset_index()
        fig = px.bar(
            store_category,
            x='Categorie_Produit',
            y='Montant',
            color='Magasin',
            title='Ventes par Catégorie et Magasin (Empilé)',
            barmode='stack'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des catégories
        st.subheader("📋 Tableau Récapitulatif des Catégories")
        st.dataframe(
            category_data.style.highlight_max(axis=0, color='#FF4B4B'),
            use_container_width=True
        )
    
    # ============================
    # ONGLET 4 : MODES DE PAIEMENT
    # ============================
    with tab4:
        st.header("💳 Analyse des Modes de Paiement")
        
        if 'Mode_Paiement' in df_filtered.columns:
            payment_dist = get_payment_distribution(df_filtered)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🥧 Répartition des Modes de Paiement")
                fig = px.pie(
                    values=payment_dist.values,
                    names=payment_dist.index,
                    title='Répartition des Transactions par Mode de Paiement',
                    hole=0.3
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Nombre de Transactions")
                fig = px.bar(
                    x=payment_dist.index,
                    y=payment_dist.values,
                    title='Nombre de Transactions par Mode',
                    labels={'x': 'Mode de Paiement', 'y': 'Nombre'},
                    color=payment_dist.values,
                    color_continuous_scale='Greens'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # KPI Mode le plus utilisé
            mode_plus_utilise = payment_dist.idxmax()
            pct_mode = (payment_dist.max() / payment_dist.sum() * 100)
            
            st.success(f"🏆 **Mode de paiement le plus utilisé** : **{mode_plus_utilise}** ({pct_mode:.1f}%)")
            
            # Montant moyen par mode de paiement
            st.subheader("💰 Montant Moyen par Mode de Paiement")
            avg_by_payment = df_filtered.groupby('Mode_Paiement')['Montant'].mean().reset_index()
            fig = px.bar(
                avg_by_payment,
                x='Mode_Paiement',
                y='Montant',
                title='Montant Moyen par Mode de Paiement',
                color='Montant',
                color_continuous_scale='Purples'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Colonne 'Mode_Paiement' non disponible")
    
    # ============================
    # ONGLET 5 : SATISFACTION CLIENT
    # ============================
    with tab5:
        st.header("⭐ Analyse de la Satisfaction Client")
        
        if 'Satisfaction_Client' in df_filtered.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Satisfaction par Magasin")
                satisfaction_store = get_satisfaction_by_store(df_filtered)
                if satisfaction_store is not None:
                    fig = px.bar(
                        x=satisfaction_store.index,
                        y=satisfaction_store.values,
                        title='Score Moyen de Satisfaction par Magasin',
                        labels={'x': 'Magasin', 'y': 'Score (1-5)'},
                        color=satisfaction_store.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        yaxis_range=[0, 5]
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📦 Satisfaction par Catégorie")
                satisfaction_category = get_satisfaction_by_category(df_filtered)
                if satisfaction_category is not None:
                    fig = px.bar(
                        x=satisfaction_category.index,
                        y=satisfaction_category.values,
                        title='Score Moyen de Satisfaction par Catégorie',
                        labels={'x': 'Catégorie', 'y': 'Score (1-5)'},
                        color=satisfaction_category.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        yaxis_range=[0, 5]
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Distribution des scores
            st.subheader("📊 Distribution des Scores de Satisfaction")
            score_dist = df_filtered['Satisfaction_Client'].value_counts().sort_index()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(
                    x=score_dist.index,
                    y=score_dist.values,
                    title='Distribution des Scores (1-5)',
                    labels={'x': 'Score', 'y': 'Nombre de clients'},
                    color=score_dist.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📋 Tableau des Scores")
                score_table = pd.DataFrame({
                    'Score': score_dist.index,
                    'Nombre': score_dist.values,
                    'Pourcentage': (score_dist.values / score_dist.sum() * 100).round(2)
                })
                st.dataframe(score_table, use_container_width=True)
        else:
            st.warning("⚠️ Colonne 'Satisfaction_Client' non disponible")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #A0A0A0;'>Dashboard créé avec Streamlit & Plotly  de python et réalisé par l'élève professeur EKOTTO ERIC| © 2025</p>",
        unsafe_allow_html=True
    )

else:
    st.error("❌ Impossible de charger les données. Vérifiez que le fichier 'data/data_dashboard_large.xlsx' existe.")
    st.info("💡 Placez votre fichier Excel dans le dossier 'data/' et renommez-le 'data_dashboard_large.xlsx'")