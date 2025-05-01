import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from predict_traffic import load_data, train_model, predict_traffic
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os
import pandas as pd
from tkcalendar import DateEntry
from database import TrafficDatabase
import matplotlib.style as style

class TrafficPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prédiction de Trafic Réseau")
        self.root.geometry("1000x700")
        
        # Configuration du style
        self.configure_styles()
        
        # Variables
        self.model = None
        self.scaler = None
        self.df = None
        self.db = TrafficDatabase()
        
        # Création de l'interface
        self.create_widgets()
        
    def configure_styles(self):
        # Configuration du style global
        style.use('seaborn')
        
        # Configuration des styles ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Couleurs
        self.colors = {
            'primary': '#2196F3',
            'secondary': '#FFC107',
            'background': '#F5F5F5',
            'text': '#212121',
            'success': '#4CAF50',
            'error': '#F44336'
        }
        
        # Configuration des styles
        self.style.configure('TFrame', background=self.colors['background'])
        self.style.configure('TLabel', background=self.colors['background'], foreground=self.colors['text'])
        self.style.configure('TButton', 
                           background=self.colors['primary'],
                           foreground='white',
                           padding=10,
                           font=('Helvetica', 10, 'bold'))
        self.style.configure('TLabelframe', 
                           background=self.colors['background'],
                           foreground=self.colors['text'])
        self.style.configure('TLabelframe.Label', 
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=('Helvetica', 11, 'bold'))
        
    def create_widgets(self):
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Section de chargement des données
        data_frame = ttk.LabelFrame(main_frame, text="Chargement des données", padding="15")
        data_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(data_frame, text="Charger fichier CSV", command=self.load_csv).grid(row=0, column=0, padx=10)
        ttk.Button(data_frame, text="Utiliser données d'exemple", command=self.use_example_data).grid(row=0, column=1, padx=10)
        ttk.Button(data_frame, text="Charger depuis la base de données", command=self.load_from_database).grid(row=0, column=2, padx=10)
        
        # Section de prédiction
        prediction_frame = ttk.LabelFrame(main_frame, text="Prédiction", padding="15")
        prediction_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(prediction_frame, text="Date de prédiction (JJ/MM/AAAA):").grid(row=0, column=0, padx=5)
        self.date_entry = DateEntry(prediction_frame, 
                                  width=12,
                                  date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(prediction_frame, text="Prédire", command=self.make_prediction).grid(row=0, column=2, padx=5)
        
        # Section de résultats
        results_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="15")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.result_label = ttk.Label(results_frame, text="", font=('Helvetica', 12))
        self.result_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Section de graphique
        graph_frame = ttk.LabelFrame(main_frame, text="Graphique", padding="15")
        graph_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(3, weight=1)
        
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                df = pd.read_csv(file_path, header=None)
                if len(df.columns) < 2:
                    messagebox.showerror("Erreur", "Le fichier CSV doit contenir au moins deux colonnes")
                    return
                
                df.columns = ['timestamp', 'value'] + [f'col{i+3}' for i in range(len(df.columns)-2)]
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                def convert_to_bits(value):
                 if isinstance(value, str):
                    value = value.lower().strip()
                    if 'mb/s' in value:
                        return float(value.replace('mb/s', '').strip()) * 1_000_000
                    elif 'kb/s' in value:
                        return float(value.replace('kb/s', '').strip()) * 1_000
                    elif 'b/s' in value:
                          return float(value.replace('b/s', '').strip())
                 return float(value)
                
                df['value'] = df['value'].apply(convert_to_bits)
                
                self.db.add_traffic_data(df, source=os.path.basename(file_path))
                self.df = df
                self.train_model()
                messagebox.showinfo("Succès", "Données chargées avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def use_example_data(self):
        try:
            self.df = load_data()
            self.db.add_traffic_data(self.df, source="exemple")
            self.train_model()
            messagebox.showinfo("Succès", "Données d'exemple chargées avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def load_from_database(self):
        try:
            self.df = self.db.get_all_traffic_data()
            if self.df.empty:
                messagebox.showinfo("Information", "Aucune donnée trouvée dans la base de données.")
                return
            self.train_model()
            messagebox.showinfo("Succès", "Données chargées depuis la base de données avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement depuis la base de données: {str(e)}")
    
    def train_model(self):
        if self.df is not None and not self.df.empty:
            try:
                self.model, self.scaler = train_model(self.df)
                self.update_graph()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'entraînement du modèle: {str(e)}")
    
    def make_prediction(self):
        if self.model is None or self.scaler is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger des données!")
            return
        
        date_str = self.date_entry.get()
        try:
            prediction = predict_traffic(self.model, self.scaler, date_str)
            if prediction is not None:
                self.db.add_prediction(datetime.strptime(date_str, "%d/%m/%Y"), prediction)
                self.result_label.config(
                    text=f"Prédiction pour le {date_str}:\nTrafic prédit: {prediction:.2f} bits/s"
                )
                self.update_graph()
            else:
                messagebox.showerror("Erreur", "Format de date invalide. Utilisez le format JJ/MM/AAAA")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la prédiction: {str(e)}")
    
    def update_graph(self):
        if self.df is not None and not self.df.empty:
            try:
                self.ax.clear()
                self.ax.plot(self.df['timestamp'], self.df['value'], 
                           label='Données réelles',
                           color=self.colors['primary'],
                           linewidth=2)
                self.ax.set_title('Trafic réseau au fil du temps', 
                                fontsize=12, 
                                pad=20)
                self.ax.set_xlabel('Date', fontsize=10)
                self.ax.set_ylabel('Trafic (bits/s)', fontsize=10)
                self.ax.legend(fontsize=10)
                self.ax.grid(True, linestyle='--', alpha=0.7)
                self.ax.tick_params(axis='x', rotation=45)
                self.fig.tight_layout()
                self.canvas.draw()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du graphique: {str(e)}")

def main():
    root = tk.Tk()
    app = TrafficPredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()