import pandas as pd
import numpy as np
from datetime import datetime

def load_and_clean_data(file_path):
    """
    Charge et nettoie les données du fichier Excel
    """
    try:
        # Charger le fichier Excel
        df = pd.read_excel(file_path)
        
        # Afficher les colonnes disponibles
        print("Colonnes du dataset:", df.columns.tolist())
        
        # Nettoyer les noms de colonnes (enlever les espaces)
        df.columns = df.columns.str.strip()
        
        # Convertir la colonne Date_Transaction en datetime
        if 'Date_Transaction' in df.columns:
            df['Date_Transaction'] = pd.to_datetime(df['Date_Transaction'], errors='coerce')
        
        # Supprimer les lignes avec des valeurs manquantes critiques
        df = df.dropna(subset=['Montant', 'Magasin', 'Categorie_Produit'])
        
        # Convertir les types de données
        if 'Montant' in df.columns:
            df['Montant'] = pd.to_numeric(df['Montant'], errors='coerce')
        
        if 'Quantite' in df.columns:
            df['Quantite'] = pd.to_numeric(df['Quantite'], errors='coerce')
        
        if 'Satisfaction_Client' in df.columns:
            df['Satisfaction_Client'] = pd.to_numeric(df['Satisfaction_Client'], errors='coerce')
        
        # Supprimer les doublons
        df = df.drop_duplicates()
        
        # Ajouter des colonnes calculées
        if 'Date_Transaction' in df.columns:
            df['Jour'] = df['Date_Transaction'].dt.date
            df['Mois'] = df['Date_Transaction'].dt.month
            df['Jour_Semaine'] = df['Date_Transaction'].dt.day_name()
        
        return df
    
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return None

def get_kpi_metrics(df):
    """
    Calcule les KPIs principaux
    """
    kpis = {
        'total_ventes': df['Montant'].sum(),
        'nb_transactions': len(df),
        'montant_moyen': df['Montant'].mean(),
        'satisfaction_moyenne': df['Satisfaction_Client'].mean() if 'Satisfaction_Client' in df.columns else 0
    }
    return kpis

def get_sales_by_store(df):
    """
    Analyse des ventes par magasin
    """
    store_analysis = df.groupby('Magasin').agg({
        'Montant': ['sum', 'mean', 'count']
    }).round(2)
    store_analysis.columns = ['Ventes_Totales', 'Montant_Moyen', 'Nb_Transactions']
    return store_analysis.reset_index()

def get_sales_by_category(df):
    """
    Analyse des ventes par catégorie
    """
    category_analysis = df.groupby('Categorie_Produit').agg({
        'Quantite': 'sum',
        'Montant': 'sum'
    }).round(2)
    category_analysis.columns = ['Quantite_Totale', 'Ventes_Totales']
    return category_analysis.reset_index()

def get_payment_distribution(df):
    """
    Distribution des modes de paiement
    """
    if 'Mode_Paiement' in df.columns:
        payment_dist = df['Mode_Paiement'].value_counts()
        return payment_dist
    return None

def get_satisfaction_by_store(df):
    """
    Satisfaction client par magasin
    """
    if 'Satisfaction_Client' in df.columns:
        satisfaction = df.groupby('Magasin')['Satisfaction_Client'].mean().round(2)
        return satisfaction
    return None

def get_satisfaction_by_category(df):
    """
    Satisfaction client par catégorie
    """
    if 'Satisfaction_Client' in df.columns:
        satisfaction = df.groupby('Categorie_Produit')['Satisfaction_Client'].mean().round(2)
        return satisfaction
    return None

def get_daily_sales(df):
    """
    Ventes quotidiennes
    """
    if 'Jour' in df.columns:
        daily_sales = df.groupby('Jour')['Montant'].sum().reset_index()
        daily_sales.columns = ['Date', 'Ventes']
        return daily_sales
    return None