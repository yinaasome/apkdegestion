import os
os.environ['KIVY_NO_ARGS'] = '1'

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock

# Configuration de la fenêtre pour mobile
Window.size = (360, 640)

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import hashlib
import json
from collections import defaultdict

# Mode démo sans Firebase
DEMO_MODE = True

# Données de démo
class DemoData:
    users = {
        'admin': {'id': 'admin', 'username': 'admin', 'password': hashlib.sha256('admin123'.encode()).hexdigest(), 'role': 'admin', 'nom_complet': 'Administrateur'},
        'gerant1': {'id': 'gerant1', 'username': 'gerant1', 'password': hashlib.sha256('pass123'.encode()).hexdigest(), 'role': 'gerant', 'nom_complet': 'Jean Dupont'}
    }
    
    produits = {
        'prod1': {'id': 'prod1', 'code': 'ORD001', 'nom': 'Ordinateur Portable', 'prix_unitaire': 800.0, 'stock_actuel': 15, 'stock_min': 5, 'date_creation': datetime.now().isoformat()},
        'prod2': {'id': 'prod2', 'code': 'SOU002', 'nom': 'Souris USB', 'prix_unitaire': 25.5, 'stock_actuel': 3, 'stock_min': 10, 'date_creation': datetime.now().isoformat()},
        'prod3': {'id': 'prod3', 'code': 'CLV003', 'nom': 'Clavier Bluetooth', 'prix_unitaire': 45.0, 'stock_actuel': 20, 'stock_min': 5, 'date_creation': datetime.now().isoformat()},
        'prod4': {'id': 'prod4', 'code': 'ECR004', 'nom': 'Écran 24"', 'prix_unitaire': 180.0, 'stock_actuel': 8, 'stock_min': 3, 'date_creation': datetime.now().isoformat()},
        'prod5': {'id': 'prod5', 'code': 'DIS005', 'nom': 'Disque Dur 1To', 'prix_unitaire': 60.0, 'stock_actuel': 25, 'stock_min': 8, 'date_creation': datetime.now().isoformat()}
    }
    
    ventes = []
    entrees = []

if not DEMO_MODE:
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase-config.json")
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print(f"Erreur Firebase: {e}")
        db = None
        DEMO_MODE = True
else:
    db = None

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.create_interface()
    
    def create_interface(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Titre
        title = Label(
            text='LeTousgestions',
            font_size=dp(24),
            size_hint_y=0.3,
            color=(0.2, 0.4, 0.6, 1)
        )
        layout.add_widget(title)
        
        # Formulaire de connexion
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15))
        
        self.username = TextInput(
            hint_text="Nom d'utilisateur",
            size_hint_y=None,
            height=dp(50),
            multiline=False,
            padding=dp(10)
        )
        
        self.password = TextInput(
            hint_text="Mot de passe",
            password=True,
            size_hint_y=None,
            height=dp(50),
            multiline=False,
            padding=dp(10)
        )
        
        login_btn = Button(
            text='Se connecter',
            size_hint_y=None,
            height=dp(60),
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        login_btn.bind(on_release=self.login)
        
        info_label = Label(
            text="Admin: admin / admin123\nGérant: gerant1 / pass123",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(40),
            color=(0.5, 0.5, 0.5, 1)
        )
        
        form_layout.add_widget(self.username)
        form_layout.add_widget(self.password)
        form_layout.add_widget(login_btn)
        form_layout.add_widget(info_label)
        
        layout.add_widget(form_layout)
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username.text.strip()
        password = self.password.text.strip()
        
        if not username or not password:
            self.show_popup("Erreur", "Veuillez remplir tous les champs")
            return
        
        try:
            if self.db and not DEMO_MODE:
                users_ref = self.db.collection('users')
                query = users_ref.where('username', '==', username).limit(1)
                results = query.get()
                
                if len(results) == 0:
                    self.show_popup("Erreur", "Nom d'utilisateur incorrect")
                    return
                
                user_data = results[0].to_dict()
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                if user_data['password'] == password_hash:
                    user_info = {
                        'id': results[0].id,
                        'username': user_data['username'],
                        'role': user_data['role'],
                        'nom_complet': user_data['nom_complet']
                    }
                    self.manager.current = 'main'
                    self.manager.get_screen('main').load_user_data(user_info)
                else:
                    self.show_popup("Erreur", "Mot de passe incorrect")
            else:
                # Mode démo
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                user_data = DemoData.users.get(username)
                
                if user_data and user_data['password'] == password_hash:
                    user_info = {
                        'id': user_data['id'],
                        'username': user_data['username'],
                        'role': user_data['role'],
                        'nom_complet': user_data['nom_complet']
                    }
                    self.manager.current = 'main'
                    self.manager.get_screen('main').load_user_data(user_info)
                else:
                    self.show_popup("Erreur", "Identifiants incorrects")
                    
        except Exception as e:
            self.show_popup("Erreur", f"Erreur de connexion: {str(e)}")
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.user_id = None
        self.user_data = None
        self.create_interface()
    
    def create_interface(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # Header
        self.header = Label(
            text='Tableau de bord',
            size_hint_y=0.1,
            font_size=dp(18),
            color=(0.2, 0.4, 0.6, 1)
        )
        self.layout.add_widget(self.header)
        
        # Contenu scrollable
        scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        
        scroll.add_widget(self.content)
        self.layout.add_widget(scroll)
        
        self.add_widget(self.layout)
    
    def load_user_data(self, user_data):
        self.user_data = user_data
        self.user_id = user_data['id']
        self.header.text = f'Tableau de bord - {user_data["nom_complet"]} ({user_data["role"]})'
        self.load_dashboard()
    
    def load_dashboard(self):
        self.content.clear_widgets()
        
        # Statistiques
        stats_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        
        # Carte Produits
        prod_card = self.create_stat_card('0', 'Produits', (0.2, 0.6, 0.8, 1))
        stats_grid.add_widget(prod_card)
        
        # Carte Alertes
        alert_card = self.create_stat_card('0', 'Alertes', (0.9, 0.3, 0.3, 1))
        stats_grid.add_widget(alert_card)
        
        # Carte CA
        ca_card = self.create_stat_card('0 €', "CA Aujourd'hui", (0.2, 0.8, 0.3, 1))
        stats_grid.add_widget(ca_card)
        
        # Carte Ventes
        ventes_card = self.create_stat_card('0', 'Ventes Jour', (0.8, 0.6, 0.2, 1))
        stats_grid.add_widget(ventes_card)
        
        self.content.add_widget(stats_grid)
        
        # Boutons de navigation
        buttons = [
            ('📦 Gestion des Produits', self.show_produits),
            ('💰 Ventes', self.show_ventes),
            ('📥 Entrées Stock', self.show_entrees),
            ('⚠️ Alertes Stock', self.show_alertes),
            ('📊 Statistiques', self.show_stats),
        ]
        
        if self.user_data and self.user_data['role'] == 'admin':
            buttons.append(('👥 Utilisateurs', self.show_users))
        
        buttons.append(('🚪 Déconnexion', self.logout))
        
        for text, callback in buttons:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(60),
                background_color=(0.3, 0.5, 0.7, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_release=callback)
            self.content.add_widget(btn)
        
        self.load_stats_data()
    
    def create_stat_card(self, value, title, color):
        card = BoxLayout(orientation='vertical')
        with card.canvas.before:
            Color(*color)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=self.update_rect, size=self.update_rect)
        
        value_label = Label(text=value, font_size=dp(20), color=(1,1,1,1))
        title_label = Label(text=title, font_size=dp(12), color=(1,1,1,1))
        
        card.add_widget(value_label)
        card.add_widget(title_label)
        
        # Stocker la référence pour mise à jour
        if title == 'Produits':
            self.nb_produits = value_label
        elif title == 'Alertes':
            self.nb_alertes = value_label
        elif title == "CA Aujourd'hui":
            self.ca_jour = value_label
        elif title == 'Ventes Jour':
            self.nb_ventes_jour = value_label
            
        return card
    
    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def load_stats_data(self):
        try:
            if self.db and not DEMO_MODE:
                # Compter les produits
                produits_ref = self.db.collection('produits')
                nb_produits = len([doc for doc in produits_ref.stream()])
                
                # Produits en alerte
                produits_alerte = produits_ref.where('stock_actuel', '<=', 'stock_min').stream()
                nb_alertes = len(list(produits_alerte))
                
                # CA du jour
                today = datetime.now().strftime('%Y-%m-%d')
                ventes_ref = self.db.collection('ventes')
                ventes_du_jour = ventes_ref.where('date_vente', '>=', today).stream()
                
                ca_jour = 0
                nb_ventes_jour = 0
                for vente in ventes_du_jour:
                    vente_data = vente.to_dict()
                    ca_jour += vente_data.get('quantite', 0) * vente_data.get('prix_unitaire', 0)
                    nb_ventes_jour += 1
                
            else:
                # Données de démo
                nb_produits = len(DemoData.produits)
                nb_alertes = sum(1 for p in DemoData.produits.values() if p['stock_actuel'] <= p['stock_min'])
                
                today = datetime.now().strftime('%Y-%m-%d')
                ca_jour = sum(v['quantite'] * v['prix_unitaire'] for v in DemoData.ventes if v['date_vente'].startswith(today))
                nb_ventes_jour = sum(1 for v in DemoData.ventes if v['date_vente'].startswith(today))
            
            self.nb_produits.text = str(nb_produits)
            self.nb_alertes.text = str(nb_alertes)
            self.ca_jour.text = f"{ca_jour:.2f} €"
            self.nb_ventes_jour.text = str(nb_ventes_jour)
            
        except Exception as e:
            print(f"Erreur dashboard: {e}")
            self.nb_produits.text = "0"
            self.nb_alertes.text = "0"
            self.ca_jour.text = "0 €"
            self.nb_ventes_jour.text = "0"
    
    def show_produits(self, instance=None):
        self.manager.current = 'produits'
        self.manager.get_screen('produits').load_produits()
    
    def show_ventes(self, instance=None):
        self.manager.current = 'ventes'
        self.manager.get_screen('ventes').load_ventes()
    
    def show_entrees(self, instance=None):
        self.manager.current = 'entrees'
        self.manager.get_screen('entrees').load_entrees()
    
    def show_alertes(self, instance=None):
        self.manager.current = 'alertes'
        self.manager.get_screen('alertes').load_alertes()
    
    def show_stats(self, instance=None):
        self.manager.current = 'stats'
        self.manager.get_screen('stats').load_stats()
    
    def show_users(self, instance=None):
        if self.user_data and self.user_data['role'] == 'admin':
            self.manager.current = 'users'
            self.manager.get_screen('users').load_users()
        else:
            self.show_popup("Accès refusé", "Seul l'administrateur peut gérer les utilisateurs")
    
    def logout(self, instance=None):
        self.user_id = None
        self.user_data = None
        self.manager.current = 'login'
        self.username.text = ""
        self.password.text = ""
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class ProduitsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.create_interface()
    
    def create_interface(self):
        layout = BoxLayout(orientation='vertical')
        
        # Header avec bouton retour
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=dp(10))
        
        back_btn = Button(
            text='← Retour',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        
        title = Label(
            text='Produits',
            font_size=dp(20),
            color=(0.2, 0.4, 0.6, 1)
        )
        
        add_btn = Button(
            text='+ Ajouter',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=self.add_produit)
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(add_btn)
        layout.add_widget(header)
        
        # Liste des produits
        scroll = ScrollView()
        self.produits_list = GridLayout(
            cols=1,
            spacing=dp(5),
            padding=dp(10),
            size_hint_y=None
        )
        self.produits_list.bind(minimum_height=self.produits_list.setter('height'))
        scroll.add_widget(self.produits_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def load_produits(self):
        self.produits_list.clear_widgets()
        
        try:
            if self.db and not DEMO_MODE:
                produits_ref = self.db.collection('produits')
                produits = produits_ref.stream()
                
                for produit in produits:
                    data = produit.to_dict()
                    self.add_produit_item(produit.id, data)
            else:
                # Données de démo
                for prod_id, data in DemoData.produits.items():
                    self.add_produit_item(prod_id, data)
                    
        except Exception as e:
            print(f"Erreur chargement produits: {e}")
            self.show_popup("Erreur", f"Impossible de charger les produits: {str(e)}")
    
    def add_produit_item(self, produit_id, data):
        item = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=dp(80),
            padding=dp(5)
        )
        
        with item.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=item.pos, size=item.size)
        
        # Informations produit
        info_layout = BoxLayout(orientation='vertical')
        
        nom_label = Label(
            text=data['nom'],
            size_hint_y=0.5,
            font_size=dp(16),
            color=(0, 0, 0, 1),
            text_size=(dp(200), None),
            halign='left'
        )
        nom_label.bind(size=nom_label.setter('text_size'))
        
        details_label = Label(
            text=f"Code: {data['code']} | Stock: {data['stock_actuel']}",
            size_hint_y=0.25,
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1)
        )
        
        prix_label = Label(
            text=f"Prix: {data['prix_unitaire']}€ | Min: {data['stock_min']}",
            size_hint_y=0.25,
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1)
        )
        
        info_layout.add_widget(nom_label)
        info_layout.add_widget(details_label)
        info_layout.add_widget(prix_label)
        item.add_widget(info_layout)
        
        # Boutons d'action
        btn_layout = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(2))
        
        edit_btn = Button(
            text='Modifier',
            size_hint_y=0.5,
            background_color=(1, 0.6, 0, 1),
            color=(1, 1, 1, 1),
            font_size=dp(10)
        )
        
        delete_btn = Button(
            text='Supprimer',
            size_hint_y=0.5,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=dp(10)
        )
        
        edit_btn.bind(on_release=lambda x: self.edit_produit(produit_id, data))
        delete_btn.bind(on_release=lambda x: self.delete_produit(produit_id, data['nom']))
        
        btn_layout.add_widget(edit_btn)
        btn_layout.add_widget(delete_btn)
        item.add_widget(btn_layout)
        
        self.produits_list.add_widget(item)
    
    def add_produit(self, instance):
        self.show_produit_popup()
    
    def edit_produit(self, produit_id, data):
        self.show_produit_popup(produit_id, data)
    
    def delete_produit(self, produit_id, nom):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=f"Supprimer le produit {nom} ?"))
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        confirm_btn = Button(text='Oui', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Non')
        
        popup = Popup(title='Confirmation', content=content, size_hint=(0.8, 0.4))
        
        def confirm_delete(instance):
            try:
                if self.db and not DEMO_MODE:
                    self.db.collection('produits').document(produit_id).delete()
                else:
                    DemoData.produits.pop(produit_id, None)
                
                self.load_produits()
                popup.dismiss()
                self.show_popup("Succès", "Produit supprimé avec succès")
            except Exception as e:
                self.show_popup("Erreur", f"Erreur suppression: {str(e)}")
        
        confirm_btn.bind(on_release=confirm_delete)
        cancel_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup.open()
    
    def show_produit_popup(self, produit_id=None, data=None):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Champs du formulaire
        code_input = TextInput(
            hint_text='Code produit', 
            text=data['code'] if data else '',
            size_hint_y=None,
            height=dp(50)
        )
        nom_input = TextInput(
            hint_text='Nom du produit', 
            text=data['nom'] if data else '',
            size_hint_y=None,
            height=dp(50)
        )
        prix_input = TextInput(
            hint_text='Prix unitaire', 
            text=str(data['prix_unitaire']) if data else '',
            size_hint_y=None,
            height=dp(50),
            input_filter='float'
        )
        stock_input = TextInput(
            hint_text='Stock actuel', 
            text=str(data['stock_actuel']) if data else '',
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )
        stock_min_input = TextInput(
            hint_text='Stock minimum', 
            text=str(data['stock_min']) if data else '',
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )
        
        content.add_widget(code_input)
        content.add_widget(nom_input)
        content.add_widget(prix_input)
        content.add_widget(stock_input)
        content.add_widget(stock_min_input)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        save_btn = Button(text='Enregistrer', background_color=(0.2, 0.8, 0.2, 1))
        cancel_btn = Button(text='Annuler', background_color=(0.8, 0.8, 0.8, 1))
        
        popup = Popup(
            title='Ajouter produit' if not data else 'Modifier produit', 
            content=content, 
            size_hint=(0.9, 0.8)
        )
        
        def save_produit(instance):
            try:
                if not all([code_input.text, nom_input.text, prix_input.text, stock_input.text, stock_min_input.text]):
                    self.show_popup("Erreur", "Tous les champs sont obligatoires")
                    return
                
                produit_data = {
                    'code': code_input.text,
                    'nom': nom_input.text,
                    'prix_unitaire': float(prix_input.text),
                    'stock_actuel': int(stock_input.text),
                    'stock_min': int(stock_min_input.text),
                    'date_creation': datetime.now().isoformat()
                }
                
                if self.db and not DEMO_MODE:
                    if produit_id:
                        self.db.collection('produits').document(produit_id).update(produit_data)
                    else:
                        self.db.collection('produits').add(produit_data)
                else:
                    if produit_id:
                        DemoData.produits[produit_id].update(produit_data)
                    else:
                        new_id = f"prod_{len(DemoData.produits) + 1}"
                        produit_data['id'] = new_id
                        DemoData.produits[new_id] = produit_data
                
                self.load_produits()
                popup.dismiss()
                self.show_popup("Succès", "Produit enregistré avec succès")
                
            except ValueError:
                self.show_popup("Erreur", "Veuillez vérifier les nombres (prix, stock)")
            except Exception as e:
                self.show_popup("Erreur", f"Erreur: {str(e)}")
        
        save_btn.bind(on_release=save_produit)
        cancel_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class VentesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.create_interface()
    
    def create_interface(self):
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=dp(10))
        
        back_btn = Button(
            text='← Retour',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        
        title = Label(
            text='Ventes',
            font_size=dp(20),
            color=(0.2, 0.4, 0.6, 1)
        )
        
        add_btn = Button(
            text='+ Vente',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=self.add_vente)
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(add_btn)
        layout.add_widget(header)
        
        # Liste des ventes
        scroll = ScrollView()
        self.ventes_list = GridLayout(
            cols=1,
            spacing=dp(5),
            padding=dp(10),
            size_hint_y=None
        )
        self.ventes_list.bind(minimum_height=self.ventes_list.setter('height'))
        scroll.add_widget(self.ventes_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def load_ventes(self):
        self.ventes_list.clear_widgets()
        
        try:
            if self.db and not DEMO_MODE:
                ventes_ref = self.db.collection('ventes')
                ventes = ventes_ref.order_by('date_vente', direction=firestore.Query.DESCENDING).stream()
                
                for vente in ventes:
                    data = vente.to_dict()
                    self.add_vente_item(vente.id, data)
            else:
                # Données de démo
                for i, vente in enumerate(DemoData.ventes):
                    self.add_vente_item(f"vente_{i}", vente)
                    
        except Exception as e:
            print(f"Erreur chargement ventes: {e}")
            self.show_popup("Erreur", f"Impossible de charger les ventes: {str(e)}")
    
    def add_vente_item(self, vente_id, data):
        item = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(100),
            padding=dp(5)
        )
        
        with item.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=item.pos, size=item.size)
        
        total = data['quantite'] * data['prix_unitaire']
        date_str = datetime.fromisoformat(data['date_vente']).strftime('%d/%m/%Y %H:%M')
        
        # Ligne 1: Produit et quantité
        ligne1 = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        ligne1.add_widget(Label(
            text=data['produit_nom'],
            font_size=dp(16),
            color=(0, 0, 0, 1),
            text_size=(dp(200), None),
            halign='left'
        ))
        ligne1.add_widget(Label(
            text=f"x{data['quantite']}",
            font_size=dp(16),
            color=(0.3, 0.3, 0.3, 1)
        ))
        
        # Ligne 2: Client et total
        ligne2 = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        ligne2.add_widget(Label(
            text=f"Client: {data.get('client', 'N/A')}",
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1)
        ))
        ligne2.add_widget(Label(
            text=f"Total: {total:.2f}€",
            font_size=dp(14),
            color=(0.2, 0.6, 0.2, 1)
        ))
        
        # Ligne 3: Date et gérant
        ligne3 = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        ligne3.add_widget(Label(
            text=date_str,
            font_size=dp(11),
            color=(0.5, 0.5, 0.5, 1)
        ))
        ligne3.add_widget(Label(
            text=f"Par: {data.get('gerant_nom', 'N/A')}",
            font_size=dp(11),
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        item.add_widget(ligne1)
        item.add_widget(ligne2)
        item.add_widget(ligne3)
        self.ventes_list.add_widget(item)
    
    def add_vente(self, instance):
        self.show_vente_popup()
    
    def show_vente_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Sélection produit
        produit_spinner = Spinner(
            text='Sélectionner produit',
            size_hint_y=None,
            height=dp(50)
        )
        
        # Charger les produits disponibles
        produits_disponibles = []
        if self.db and not DEMO_MODE:
            produits_ref = self.db.collection('produits')
            produits = produits_ref.where('stock_actuel', '>', 0).stream()
            for produit in produits:
                data = produit.to_dict()
                if data['stock_actuel'] > 0:
                    produits_disponibles.append({
                        'id': produit.id,
                        'nom': data['nom'],
                        'stock': data['stock_actuel'],
                        'prix': data['prix_unitaire']
                    })
        else:
            for prod_id, data in DemoData.produits.items():
                if data['stock_actuel'] > 0:
                    produits_disponibles.append({
                        'id': prod_id,
                        'nom': data['nom'],
                        'stock': data['stock_actuel'],
                        'prix': data['prix_unitaire']
                    })
        
        if not produits_disponibles:
            self.show_popup("Information", "Aucun produit en stock disponible")
            return
        
        produit_spinner.values = [f"{p['nom']} (Stock: {p['stock']})" for p in produits_disponibles]
        produit_spinner.text = produit_spinner.values[0]
        
        quantite_input = TextInput(
            hint_text='Quantité',
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )
        
        prix_input = TextInput(
            hint_text='Prix unitaire',
            size_hint_y=None,
            height=dp(50),
            input_filter='float'
        )
        
        client_input = TextInput(
            hint_text='Client (optionnel)',
            size_hint_y=None,
            height=dp(50)
        )
        
        # Auto-remplir le prix
        def on_produit_select(spinner, text):
            if produits_disponibles and spinner.text != 'Sélectionner produit':
                index = spinner.values.index(text)
                prix_input.text = str(produits_disponibles[index]['prix'])
        
        produit_spinner.bind(text=on_produit_select)
        
        content.add_widget(Label(text='Produit:', size_hint_y=None, height=dp(30)))
        content.add_widget(produit_spinner)
        content.add_widget(Label(text='Quantité:', size_hint_y=None, height=dp(30)))
        content.add_widget(quantite_input)
        content.add_widget(Label(text='Prix unitaire:', size_hint_y=None, height=dp(30)))
        content.add_widget(prix_input)
        content.add_widget(Label(text='Client:', size_hint_y=None, height=dp(30)))
        content.add_widget(client_input)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        save_btn = Button(text='Enregistrer', background_color=(0.2, 0.8, 0.2, 1))
        cancel_btn = Button(text='Annuler', background_color=(0.8, 0.8, 0.8, 1))
        
        popup = Popup(title='Nouvelle vente', content=content, size_hint=(0.9, 0.8))
        
        def save_vente(instance):
            try:
                if produit_spinner.text == 'Sélectionner produit':
                    self.show_popup("Erreur", "Veuillez sélectionner un produit")
                    return
                
                if not quantite_input.text or not prix_input.text:
                    self.show_popup("Erreur", "Quantité et prix sont obligatoires")
                    return
                
                index = produit_spinner.values.index(produit_spinner.text)
                produit_selectionne = produits_disponibles[index]
                quantite = int(quantite_input.text)
                prix = float(prix_input.text)
                client = client_input.text.strip() or None
                
                if quantite <= 0:
                    self.show_popup("Erreur", "La quantité doit être positive")
                    return
                
                if quantite > produit_selectionne['stock']:
                    self.show_popup("Erreur", f"Stock insuffisant. Disponible: {produit_selectionne['stock']}")
                    return
                
                vente_data = {
                    'produit_id': produit_selectionne['id'],
                    'produit_nom': produit_selectionne['nom'],
                    'quantite': quantite,
                    'prix_unitaire': prix,
                    'client': client,
                    'gerant_id': App.get_running_app().root.get_screen('main').user_id,
                    'gerant_nom': App.get_running_app().root.get_screen('main').user_data['nom_complet'],
                    'date_vente': datetime.now().isoformat()
                }
                
                if self.db and not DEMO_MODE:
                    # Enregistrer la vente
                    self.db.collection('ventes').add(vente_data)
                    
                    # Mettre à jour le stock
                    produit_ref = self.db.collection('produits').document(produit_selectionne['id'])
                    produit_ref.update({'stock_actuel': firestore.Increment(-quantite)})
                else:
                    # Mode démo
                    DemoData.ventes.append(vente_data)
                    # Mettre à jour le stock
                    DemoData.produits[produit_selectionne['id']]['stock_actuel'] -= quantite
                
                self.load_ventes()
                popup.dismiss()
                self.show_popup("Succès", "Vente enregistrée avec succès")
                
            except ValueError:
                self.show_popup("Erreur", "Veuillez vérifier les nombres (quantité, prix)")
            except Exception as e:
                self.show_popup("Erreur", f"Erreur: {str(e)}")
        
        save_btn.bind(on_release=save_vente)
        cancel_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class EntreesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.create_interface()
    
    def create_interface(self):
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=dp(10))
        
        back_btn = Button(
            text='← Retour',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        
        title = Label(
            text='Entrées Stock',
            font_size=dp(20),
            color=(0.2, 0.4, 0.6, 1)
        )
        
        add_btn = Button(
            text='+ Entrée',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=self.add_entree)
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(add_btn)
        layout.add_widget(header)
        
        # Liste des entrées
        scroll = ScrollView()
        self.entrees_list = GridLayout(
            cols=1,
            spacing=dp(5),
            padding=dp(10),
            size_hint_y=None
        )
        self.entrees_list.bind(minimum_height=self.entrees_list.setter('height'))
        scroll.add_widget(self.entrees_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def load_entrees(self):
        self.entrees_list.clear_widgets()
        
        try:
            if self.db and not DEMO_MODE:
                entrees_ref = self.db.collection('entrees_stock')
                entrees = entrees_ref.order_by('date_creation', direction=firestore.Query.DESCENDING).stream()
                
                for entree in entrees:
                    data = entree.to_dict()
                    self.add_entree_item(entree.id, data)
            else:
                # Données de démo
                for i, entree in enumerate(DemoData.entrees):
                    self.add_entree_item(f"entree_{i}", entree)
                    
        except Exception as e:
            print(f"Erreur chargement entrées: {e}")
    
    def add_entree_item(self, entree_id, data):
        item = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(100),
            padding=dp(5)
        )
        
        with item.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=item.pos, size=item.size)
        
        total = data['quantite'] * data['prix_unitaire']
        date_str = datetime.fromisoformat(data['date_creation']).strftime('%d/%m/%Y %H:%M')
        
        # Ligne 1: Produit et quantité
        ligne1 = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        ligne1.add_widget(Label(
            text=data['produit_nom'],
            font_size=dp(16),
            color=(0, 0, 0, 1)
        ))
        ligne1.add_widget(Label(
            text=f"+{data['quantite']} unités",
            font_size=dp(16),
            color=(0.2, 0.6, 0.2, 1)
        ))
        
        # Ligne 2: Fournisseur et total
        ligne2 = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        ligne2.add_widget(Label(
            text=f"Fourn.: {data.get('fournisseur', 'N/A')}",
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1)
        ))
        ligne2.add_widget(Label(
            text=f"Total: {total:.2f}€",
            font_size=dp(14),
            color=(0.2, 0.6, 0.2, 1)
        ))
        
        # Ligne 3: Date et gérant
        ligne3 = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        ligne3.add_widget(Label(
            text=date_str,
            font_size=dp(11),
            color=(0.5, 0.5, 0.5, 1)
        ))
        ligne3.add_widget(Label(
            text=f"Par: {data.get('gerant_nom', 'N/A')}",
            font_size=dp(11),
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        item.add_widget(ligne1)
        item.add_widget(ligne2)
        item.add_widget(ligne3)
        self.entrees_list.add_widget(item)
    
    def add_entree(self, instance):
        self.show_entree_popup()
    
    def show_entree_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Sélection produit
        produit_spinner = Spinner(
            text='Sélectionner produit',
            size_hint_y=None,
            height=dp(50)
        )
        
        # Charger tous les produits
        produits = []
        if self.db and not DEMO_MODE:
            produits_ref = self.db.collection('produits')
            produits_docs = produits_ref.stream()
            for produit in produits_docs:
                data = produit.to_dict()
                produits.append({
                    'id': produit.id,
                    'nom': data['nom'],
                    'prix': data['prix_unitaire']
                })
        else:
            for prod_id, data in DemoData.produits.items():
                produits.append({
                    'id': prod_id,
                    'nom': data['nom'],
                    'prix': data['prix_unitaire']
                })
        
        produit_spinner.values = [p['nom'] for p in produits]
        if produits:
            produit_spinner.text = produit_spinner.values[0]
        
        quantite_input = TextInput(
            hint_text='Quantité',
            size_hint_y=None,
            height=dp(50),
            input_filter='int'
        )
        
        prix_input = TextInput(
            hint_text='Prix unitaire',
            size_hint_y=None,
            height=dp(50),
            input_filter='float'
        )
        
        fournisseur_input = TextInput(
            hint_text='Fournisseur (optionnel)',
            size_hint_y=None,
            height=dp(50)
        )
        
        # Auto-remplir le prix
        def on_produit_select(spinner, text):
            if produits and spinner.text != 'Sélectionner produit':
                index = spinner.values.index(text)
                prix_input.text = str(produits[index]['prix'])
        
        produit_spinner.bind(text=on_produit_select)
        
        content.add_widget(Label(text='Produit:', size_hint_y=None, height=dp(30)))
        content.add_widget(produit_spinner)
        content.add_widget(Label(text='Quantité:', size_hint_y=None, height=dp(30)))
        content.add_widget(quantite_input)
        content.add_widget(Label(text='Prix unitaire:', size_hint_y=None, height=dp(30)))
        content.add_widget(prix_input)
        content.add_widget(Label(text='Fournisseur:', size_hint_y=None, height=dp(30)))
        content.add_widget(fournisseur_input)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        save_btn = Button(text='Enregistrer', background_color=(0.2, 0.8, 0.2, 1))
        cancel_btn = Button(text='Annuler', background_color=(0.8, 0.8, 0.8, 1))
        
        popup = Popup(title='Nouvelle entrée stock', content=content, size_hint=(0.9, 0.8))
        
        def save_entree(instance):
            try:
                if produit_spinner.text == 'Sélectionner produit':
                    self.show_popup("Erreur", "Veuillez sélectionner un produit")
                    return
                
                if not quantite_input.text or not prix_input.text:
                    self.show_popup("Erreur", "Quantité et prix sont obligatoires")
                    return
                
                index = produit_spinner.values.index(produit_spinner.text)
                produit_selectionne = produits[index]
                quantite = int(quantite_input.text)
                prix = float(prix_input.text)
                fournisseur = fournisseur_input.text.strip() or None
                
                if quantite <= 0:
                    self.show_popup("Erreur", "La quantité doit être positive")
                    return
                
                entree_data = {
                    'produit_id': produit_selectionne['id'],
                    'produit_nom': produit_selectionne['nom'],
                    'quantite': quantite,
                    'prix_unitaire': prix,
                    'fournisseur': fournisseur,
                    'gerant_id': App.get_running_app().root.get_screen('main').user_id,
                    'gerant_nom': App.get_running_app().root.get_screen('main').user_data['nom_complet'],
                    'date_creation': datetime.now().isoformat()
                }
                
                if self.db and not DEMO_MODE:
                    # Enregistrer l'entrée
                    self.db.collection('entrees_stock').add(entree_data)
                    
                    # Mettre à jour le stock
                    produit_ref = self.db.collection('produits').document(produit_selectionne['id'])
                    produit_ref.update({'stock_actuel': firestore.Increment(quantite)})
                else:
                    # Mode démo
                    DemoData.entrees.append(entree_data)
                    # Mettre à jour le stock
                    DemoData.produits[produit_selectionne['id']]['stock_actuel'] += quantite
                
                self.load_entrees()
                popup.dismiss()
                self.show_popup("Succès", "Entrée de stock enregistrée avec succès")
                
            except ValueError:
                self.show_popup("Erreur", "Veuillez vérifier les nombres (quantité, prix)")
            except Exception as e:
                self.show_popup("Erreur", f"Erreur: {str(e)}")
        
        save_btn.bind(on_release=save_entree)
        cancel_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class AlertesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.create_interface()
    
    def create_interface(self):
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=dp(10))
        
        back_btn = Button(
            text='← Retour',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        
        title = Label(
            text='Alertes Stock',
            font_size=dp(20),
            color=(0.2, 0.4, 0.6, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label())  # Espace vide
        layout.add_widget(header)
        
        # Liste des alertes
        scroll = ScrollView()
        self.alertes_list = GridLayout(
            cols=1,
            spacing=dp(5),
            padding=dp(10),
            size_hint_y=None
        )
        self.alertes_list.bind(minimum_height=self.alertes_list.setter('height'))
        scroll.add_widget(self.alertes_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def load_alertes(self):
        self.alertes_list.clear_widgets()
        
        try:
            produits_alerte = []
            if self.db and not DEMO_MODE:
                produits_ref = self.db.collection('produits')
                produits = produits_ref.stream()
                for produit in produits:
                    data = produit.to_dict()
                    if data['stock_actuel'] <= data['stock_min']:
                        produits_alerte.append((produit.id, data))
            else:
                for prod_id, data in DemoData.produits.items():
                    if data['stock_actuel'] <= data['stock_min']:
                        produits_alerte.append((prod_id, data))
            
            if not produits_alerte:
                self.alertes_list.add_widget(Label(
                    text='Aucune alerte de stock',
                    font_size=dp(18),
                    color=(0.3, 0.3, 0.3, 1),
                    size_hint_y=None,
                    height=dp(100)
                ))
                return
            
            for prod_id, data in produits_alerte:
                self.add_alerte_item(prod_id, data)
                    
        except Exception as e:
            print(f"Erreur chargement alertes: {e}")
    
    def add_alerte_item(self, produit_id, data):
        item = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=dp(80),
            padding=dp(5)
        )
        
        # Couleur selon le niveau d'alerte
        if data['stock_actuel'] == 0:
            bg_color = (0.9, 0.3, 0.3, 1)  # Rouge pour rupture
            statut = "RUPTURE"
        else:
            bg_color = (1, 0.6, 0.2, 1)    # Orange pour stock bas
            statut = "STOCK BAS"
        
        with item.canvas.before:
            Color(*bg_color)
            Rectangle(pos=item.pos, size=item.size)
        
        # Informations produit
        info_layout = BoxLayout(orientation='vertical')
        
        nom_label = Label(
            text=data['nom'],
            size_hint_y=0.5,
            font_size=dp(16),
            color=(1, 1, 1, 1)
        )
        
        details_label = Label(
            text=f"Code: {data['code']} | Stock: {data['stock_actuel']}",
            size_hint_y=0.25,
            font_size=dp(12),
            color=(1, 1, 1, 1)
        )
        
        alerte_label = Label(
            text=f"Minimum: {data['stock_min']} | Statut: {statut}",
            size_hint_y=0.25,
            font_size=dp(12),
            color=(1, 1, 1, 1)
        )
        
        info_layout.add_widget(nom_label)
        info_layout.add_widget(details_label)
        info_layout.add_widget(alerte_label)
        item.add_widget(info_layout)
        
        self.alertes_list.add_widget(item)

class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.create_interface()
    
    def create_interface(self):
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=dp(10))
        
        back_btn = Button(
            text='← Retour',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        
        title = Label(
            text='Statistiques',
            font_size=dp(20),
            color=(0.2, 0.4, 0.6, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Label())
        layout.add_widget(header)
        
        # Contenu des statistiques
        scroll = ScrollView()
        self.stats_content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.stats_content.bind(minimum_height=self.stats_content.setter('height'))
        scroll.add_widget(self.stats_content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def load_stats(self):
        self.stats_content.clear_widgets()
        
        try:
            # Statistiques des ventes
            if self.db and not DEMO_MODE:
                ventes_ref = self.db.collection('ventes')
                ventes = ventes_ref.stream()
                
                total_ventes = 0
                total_ca = 0
                produits_vendus = defaultdict(int)
                ca_par_produit = defaultdict(float)
                
                for vente in ventes:
                    data = vente.to_dict()
                    quantite = data['quantite']
                    prix = data['prix_unitaire']
                    total = quantite * prix
                    
                    total_ventes += quantite
                    total_ca += total
                    produits_vendus[data['produit_nom']] += quantite
                    ca_par_produit[data['produit_nom']] += total
                    
            else:
                total_ventes = sum(v['quantite'] for v in DemoData.ventes)
                total_ca = sum(v['quantite'] * v['prix_unitaire'] for v in DemoData.ventes)
                
                produits_vendus = defaultdict(int)
                ca_par_produit = defaultdict(float)
                for vente in DemoData.ventes:
                    produits_vendus[vente['produit_nom']] += vente['quantite']
                    ca_par_produit[vente['produit_nom']] += vente['quantite'] * vente['prix_unitaire']
            
            # Affichage des statistiques générales
            stats_general = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
            
            stats_general.add_widget(self.create_stat_card(f"{total_ventes}", "Total Ventes", (0.2, 0.6, 0.8, 1)))
            stats_general.add_widget(self.create_stat_card(f"{total_ca:.2f}€", "Chiffre Affaires", (0.2, 0.8, 0.3, 1)))
            
            self.stats_content.add_widget(stats_general)
            
            # Top produits par quantité
            self.stats_content.add_widget(Label(
                text="Top Produits (Quantité):",
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                color=(0.2, 0.4, 0.6, 1)
            ))
            
            produits_tries = sorted(produits_vendus.items(), key=lambda x: x[1], reverse=True)[:5]
            for produit, quantite in produits_tries:
                produit_item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40)
                )
                produit_item.add_widget(Label(
                    text=produit,
                    text_size=(dp(200), None),
                    halign='left'
                ))
                produit_item.add_widget(Label(text=str(quantite)))
                self.stats_content.add_widget(produit_item)
            
            # Top produits par CA
            self.stats_content.add_widget(Label(
                text="Top Produits (CA):",
                size_hint_y=None,
                height=dp(30),
                font_size=dp(16),
                color=(0.2, 0.4, 0.6, 1)
            ))
            
            ca_tries = sorted(ca_par_produit.items(), key=lambda x: x[1], reverse=True)[:5]
            for produit, ca in ca_tries:
                produit_item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40)
                )
                produit_item.add_widget(Label(
                    text=produit,
                    text_size=(dp(200), None),
                    halign='left'
                ))
                produit_item.add_widget(Label(text=f"{ca:.2f}€"))
                self.stats_content.add_widget(produit_item)
                
        except Exception as e:
            print(f"Erreur chargement stats: {e}")
            self.stats_content.add_widget(Label(
                text="Erreur lors du chargement des statistiques",
                color=(0.8, 0.2, 0.2, 1)
            ))
    
    def create_stat_card(self, value, title, color):
        card = BoxLayout(orientation='vertical')
        with card.canvas.before:
            Color(*color)
            Rectangle(pos=card.pos, size=card.size)
        
        value_label = Label(text=value, font_size=dp(18), color=(1,1,1,1))
        title_label = Label(text=title, font_size=dp(12), color=(1,1,1,1))
        
        card.add_widget(value_label)
        card.add_widget(title_label)
        
        return card

class UsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.create_interface()
    
    def create_interface(self):
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=dp(10))
        
        back_btn = Button(
            text='← Retour',
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        
        title = Label(
            text='Utilisateurs',
            font_size=dp(20),
            color=(0.2, 0.4, 0.6, 1)
        )
        
        add_btn = Button(
            text='+ Ajouter',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_release=self.add_user)
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(add_btn)
        layout.add_widget(header)
        
        # Liste des utilisateurs
        scroll = ScrollView()
        self.users_list = GridLayout(
            cols=1,
            spacing=dp(5),
            padding=dp(10),
            size_hint_y=None
        )
        self.users_list.bind(minimum_height=self.users_list.setter('height'))
        scroll.add_widget(self.users_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def load_users(self):
        self.users_list.clear_widgets()
        
        try:
            if self.db and not DEMO_MODE:
                users_ref = self.db.collection('users')
                users = users_ref.stream()
                
                for user in users:
                    data = user.to_dict()
                    self.add_user_item(user.id, data)
            else:
                for user_id, data in DemoData.users.items():
                    self.add_user_item(user_id, data)
                    
        except Exception as e:
            print(f"Erreur chargement utilisateurs: {e}")
    
    def add_user_item(self, user_id, data):
        item = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=dp(70),
            padding=dp(5)
        )
        
        with item.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=item.pos, size=item.size)
        
        # Informations utilisateur
        info_layout = BoxLayout(orientation='vertical')
        
        nom_label = Label(
            text=data['nom_complet'],
            size_hint_y=0.5,
            font_size=dp(16),
            color=(0, 0, 0, 1)
        )
        
        details_label = Label(
            text=f"Utilisateur: {data['username']} | Rôle: {data['role']}",
            size_hint_y=0.5,
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1)
        )
        
        info_layout.add_widget(nom_label)
        info_layout.add_widget(details_label)
        item.add_widget(info_layout)
        
        # Boutons d'action (sauf pour l'utilisateur courant)
        current_user_id = App.get_running_app().root.get_screen('main').user_id
        if user_id != current_user_id:
            btn_layout = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(2))
            
            edit_btn = Button(
                text='Modifier',
                size_hint_y=0.5,
                background_color=(1, 0.6, 0, 1),
                color=(1, 1, 1, 1),
                font_size=dp(10)
            )
            
            delete_btn = Button(
                text='Supprimer',
                size_hint_y=0.5,
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                font_size=dp(10)
            )
            
            edit_btn.bind(on_release=lambda x: self.edit_user(user_id, data))
            delete_btn.bind(on_release=lambda x: self.delete_user(user_id, data['nom_complet']))
            
            btn_layout.add_widget(edit_btn)
            btn_layout.add_widget(delete_btn)
            item.add_widget(btn_layout)
        
        self.users_list.add_widget(item)
    
    def add_user(self, instance):
        self.show_user_popup()
    
    def edit_user(self, user_id, data):
        self.show_user_popup(user_id, data)
    
    def delete_user(self, user_id, nom):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=f"Supprimer l'utilisateur {nom} ?"))
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        confirm_btn = Button(text='Oui', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Non')
        
        popup = Popup(title='Confirmation', content=content, size_hint=(0.8, 0.4))
        
        def confirm_delete(instance):
            try:
                if self.db and not DEMO_MODE:
                    self.db.collection('users').document(user_id).delete()
                else:
                    DemoData.users.pop(user_id, None)
                
                self.load_users()
                popup.dismiss()
                self.show_popup("Succès", "Utilisateur supprimé avec succès")
            except Exception as e:
                self.show_popup("Erreur", f"Erreur suppression: {str(e)}")
        
        confirm_btn.bind(on_release=confirm_delete)
        cancel_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup.open()
    
    def show_user_popup(self, user_id=None, data=None):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Champs du formulaire
        username_input = TextInput(
            hint_text="Nom d'utilisateur", 
            text=data['username'] if data else '',
            size_hint_y=None,
            height=dp(50)
        )
        nom_input = TextInput(
            hint_text='Nom complet', 
            text=data['nom_complet'] if data else '',
            size_hint_y=None,
            height=dp(50)
        )
        
        role_spinner = Spinner(
            text=data['role'] if data else 'gerant',
            values=('admin', 'gerant'),
            size_hint_y=None,
            height=dp(50)
        )
        
        password_input = TextInput(
            hint_text='Mot de passe' if not data else 'Nouveau mot de passe (laisser vide pour inchangé)',
            password=True,
            size_hint_y=None,
            height=dp(50)
        )
        
        confirm_password_input = TextInput(
            hint_text='Confirmer mot de passe',
            password=True,
            size_hint_y=None,
            height=dp(50)
        )
        
        content.add_widget(Label(text="Nom d'utilisateur:", size_hint_y=None, height=dp(30)))
        content.add_widget(username_input)
        content.add_widget(Label(text='Nom complet:', size_hint_y=None, height=dp(30)))
        content.add_widget(nom_input)
        content.add_widget(Label(text='Rôle:', size_hint_y=None, height=dp(30)))
        content.add_widget(role_spinner)
        content.add_widget(Label(text='Mot de passe:', size_hint_y=None, height=dp(30)))
        content.add_widget(password_input)
        content.add_widget(Label(text='Confirmation:', size_hint_y=None, height=dp(30)))
        content.add_widget(confirm_password_input)
        
        # Boutons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        save_btn = Button(text='Enregistrer', background_color=(0.2, 0.8, 0.2, 1))
        cancel_btn = Button(text='Annuler', background_color=(0.8, 0.8, 0.8, 1))
        
        popup = Popup(
            title='Ajouter utilisateur' if not data else 'Modifier utilisateur', 
            content=content, 
            size_hint=(0.9, 0.8)
        )
        
        def save_user(instance):
            try:
                if not all([username_input.text, nom_input.text, role_spinner.text]):
                    self.show_popup("Erreur", "Tous les champs sont obligatoires")
                    return
                
                if not data and (not password_input.text or not confirm_password_input.text):
                    self.show_popup("Erreur", "Le mot de passe est obligatoire pour un nouvel utilisateur")
                    return
                
                if password_input.text and password_input.text != confirm_password_input.text:
                    self.show_popup("Erreur", "Les mots de passe ne correspondent pas")
                    return
                
                user_data = {
                    'username': username_input.text,
                    'nom_complet': nom_input.text,
                    'role': role_spinner.text,
                }
                
                if password_input.text:
                    user_data['password'] = hashlib.sha256(password_input.text.encode()).hexdigest()
                elif data:
                    # Garder l'ancien mot de passe
                    user_data['password'] = data['password']
                
                if self.db and not DEMO_MODE:
                    if user_id:
                        self.db.collection('users').document(user_id).update(user_data)
                    else:
                        self.db.collection('users').add(user_data)
                else:
                    if user_id:
                        DemoData.users[user_id].update(user_data)
                    else:
                        new_id = f"user_{len(DemoData.users) + 1}"
                        user_data['id'] = new_id
                        DemoData.users[new_id] = user_data
                
                self.load_users()
                popup.dismiss()
                self.show_popup("Succès", "Utilisateur enregistré avec succès")
                
            except Exception as e:
                self.show_popup("Erreur", f"Erreur: {str(e)}")
        
        save_btn.bind(on_release=save_user)
        cancel_btn.bind(on_release=popup.dismiss)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class LeTousgestionsApp(App):
    def build(self):
        self.title = "LeTousgestions Mobile"
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ProduitsScreen(name='produits'))
        sm.add_widget(VentesScreen(name='ventes'))
        sm.add_widget(EntreesScreen(name='entrees'))
        sm.add_widget(AlertesScreen(name='alertes'))
        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(UsersScreen(name='users'))
        
        return sm

if __name__ == '__main__':
    LeTousgestionsApp().run()
