import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import re

# Dictionnaire de traductions
TRANSLATIONS = {
    'en': {
        'language_title': 'Select Language',
        'language_prompt': 'Choose your preferred language:',
        'mod_type_title': 'Select Mod Type',
        'mod_type_prompt': 'Choose the type of mod you want to update:',
        'fabric': 'Fabric',
        'forge': 'Forge (not working)',
        'select_button': 'Select',
        'select_jar_title': 'Select Mod JAR file',
        'jar_file_type': 'JAR files',
        'no_file_selected': 'No file selected',
        'version_title': 'Minecraft Version',
        'enter_version': 'Enter the desired Minecraft version:',
        'submit': 'Submit',
        'version_required': 'Please enter a version',
        'file_not_found': 'Configuration file not found',
        'success_title': 'Success',
        'success_message': 'Mod updated! New version saved: ',
        'error_title': 'Error'
    },
    'es': {
        'language_title': 'Seleccionar Idioma',
        'language_prompt': 'Elija su idioma preferido:',
        'mod_type_title': 'Seleccionar Tipo de Mod',
        'mod_type_prompt': 'Elija el tipo de mod que desea actualizar:',
        'fabric': 'Fabric',
        'forge': 'Forge',
        'select_button': 'Seleccionar',
        'select_jar_title': 'Seleccione el archivo JAR del Mod',
        'jar_file_type': 'Archivos JAR',
        'no_file_selected': 'No se seleccionó ningún archivo',
        'version_title': 'Versión de Minecraft',
        'enter_version': 'Ingrese la versión de Minecraft deseada:',
        'submit': 'Enviar',
        'version_required': 'Por favor, ingrese una versión',
        'file_not_found': 'Archivo de configuración no encontrado',
        'success_title': 'Éxito',
        'success_message': 'Mod actualizado. Nueva versión guardada: ',
        'error_title': 'Error'
    },
    'fr': {
        'language_title': 'Sélection de la Langue',
        'language_prompt': 'Choisissez votre langue préférée :',
        'mod_type_title': 'Sélection du Type de Mod',
        'mod_type_prompt': 'Choisissez le type de mod à mettre à jour :',
        'fabric': 'Fabric',
        'forge': 'Forge',
        'select_button': 'Sélectionner',
        'select_jar_title': 'Sélectionnez le fichier Mod (.jar)',
        'jar_file_type': 'Fichiers JAR',
        'no_file_selected': 'Aucun fichier sélectionné',
        'version_title': 'Version Minecraft',
        'enter_version': 'Entrez la version Minecraft souhaitée :',
        'submit': 'Soumettre',
        'version_required': 'Veuillez entrer une version',
        'file_not_found': 'Fichier de configuration non trouvé',
        'success_title': 'Succès',
        'success_message': 'Mod mis à jour ! Nouvelle version sauvegardée : ',
        'error_title': 'Erreur'
    }
}

class ModVersionUpdater:
    def __init__(self):
        self.selected_language = None
        self.selected_mod_type = None

    def select_language(self):
        """Méthode de sélection de langue"""
        language_window = tk.Tk()
        language_window.title(TRANSLATIONS['en']['language_title'])
        language_window.geometry("300x250")

        label = tk.Label(language_window, text=TRANSLATIONS['en']['language_prompt'])
        label.pack(pady=20)

        language_var = tk.StringVar()

        languages = [
            ('English', 'en'),
            ('Español', 'es'),
            ('Français', 'fr')
        ]

        def on_language_select(lang):
            language_var.set(lang)
            language_window.destroy()

        for lang_name, lang_code in languages:
            btn = ttk.Button(
                language_window, 
                text=lang_name, 
                command=lambda code=lang_code: on_language_select(code),
                width=20
            )
            btn.pack(pady=10)

        language_window.mainloop()

        self.selected_language = language_var.get() or 'en'
        return self.selected_language

    def select_mod_type(self):
        """Méthode de sélection du type de mod"""
        t = TRANSLATIONS[self.selected_language]
        
        mod_type_window = tk.Tk()
        mod_type_window.title(t['mod_type_title'])
        mod_type_window.geometry("300x250")

        label = tk.Label(mod_type_window, text=t['mod_type_prompt'])
        label.pack(pady=20)

        mod_type_var = tk.StringVar()

        def on_mod_type_select(mod_type):
            mod_type_var.set(mod_type)
            mod_type_window.destroy()

        # Boutons pour Fabric et Forge
        fabric_btn = ttk.Button(
            mod_type_window, 
            text=t['fabric'], 
            command=lambda: on_mod_type_select('fabric'),
            width=20
        )
        fabric_btn.pack(pady=10)

        forge_btn = ttk.Button(
            mod_type_window, 
            text=t['forge'], 
            command=lambda: on_mod_type_select('forge'),
            width=20
        )
        forge_btn.pack(pady=10)

        mod_type_window.mainloop()

        self.selected_mod_type = mod_type_var.get()
        return self.selected_mod_type

    def convert_jar_to_zip(self, jar_path):
        """Convertit un fichier .jar en .zip"""
        zip_path = jar_path.replace('.jar', '.zip')
        os.rename(jar_path, zip_path)
        return zip_path

    def convert_zip_to_jar(self, zip_path):
        """Convertit un fichier .zip en .jar"""
        jar_path = zip_path.replace('.zip', '.jar')
        os.rename(zip_path, jar_path)
        return jar_path

    def modify_fabric_version(self, zip_path, new_version):
        """Modifie la version Minecraft dans fabric.mod.json"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('temp_mod_folder')
        
        fabric_mod_path = 'temp_mod_folder/fabric.mod.json'
        
        if not os.path.exists(fabric_mod_path):
            raise FileNotFoundError(TRANSLATIONS[self.selected_language]['file_not_found'])
        
        with open(fabric_mod_path, 'r', encoding='utf-8') as f:
            mod_config = json.load(f)
        
        mod_config['depends']['minecraft'] = f">={new_version}"
        
        with open(fabric_mod_path, 'w', encoding='utf-8') as f:
            json.dump(mod_config, f, indent=2)
        
        self._repack_zip(zip_path)

    def modify_forge_version(self, zip_path, new_version):
        """Modifie uniquement le second versionRange dans mods.toml"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('temp_mod_folder')
        
        # Chercher mods.toml dans META-INF
        mods_toml_path = None
        for root, dirs, files in os.walk('temp_mod_folder'):
            if 'mods.toml' in files:
                mods_toml_path = os.path.join(root, 'mods.toml')
                break
        
        if not mods_toml_path:
            raise FileNotFoundError(TRANSLATIONS[self.selected_language]['file_not_found'])
        
        # Lire le contenu du fichier
        with open(mods_toml_path, 'r', encoding='utf-8') as f:
            toml_content = f.read()
        
        # Trouver et remplacer uniquement le second versionRange
        # Utilisation d'une regex qui saute la première occurrence
        modified_content = re.sub(
            r'(versionRange=")([^"]*")(.+versionRange=")([^"]*")', 
            fr'\1\2\3[{new_version}]', 
            toml_content, 
            count=1  # Important : ne remplace que la première occurrence
        )
        
        # Écrire le contenu modifié
        with open(mods_toml_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        self._repack_zip(zip_path)

    def _repack_zip(self, zip_path):
        """Recrée l'archive ZIP avec les fichiers modifiés"""
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk('temp_mod_folder'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, 'temp_mod_folder')
                    zipf.write(file_path, arcname)
        
        # Nettoyer les fichiers temporaires
        import shutil
        shutil.rmtree('temp_mod_folder')

    def main_process(self):
        # Sélectionner la langue
        self.select_language()
        
        # Sélectionner le type de mod
        self.select_mod_type()
        
        t = TRANSLATIONS[self.selected_language]
        
        # Ouvrir une boîte de dialogue pour sélectionner le fichier .jar
        root = tk.Tk()
        root.withdraw()
        
        jar_path = filedialog.askopenfilename(
            title=t['select_jar_title'],
            filetypes=[(t['jar_file_type'], "*.jar")]
        )
        
        if not jar_path:
            messagebox.showerror(t['error_title'], t['no_file_selected'])
            return
        
        try:
            # Convertir JAR en ZIP
            zip_path = self.convert_jar_to_zip(jar_path)
            
            # Demander la version Minecraft
            version_window = tk.Tk()
            version_window.title(t['version_title'])
            version_window.geometry("300x150")
            
            label = tk.Label(version_window, text=t['enter_version'])
            label.pack(pady=10)
            
            version_entry = tk.Entry(version_window, width=30)
            version_entry.pack(pady=10)
            
            def on_submit():
                new_version = version_entry.get()
                if new_version:
                    version_window.destroy()
                    try:
                        # Modifier la version selon le type de mod
                        if self.selected_mod_type == 'fabric':
                            self.modify_fabric_version(zip_path, new_version)
                        else:  # forge
                            self.modify_forge_version(zip_path, new_version)
                        
                        converted_jar_path = self.convert_zip_to_jar(zip_path)
                        messagebox.showinfo(
                            t['success_title'], 
                            f"{t['success_message']}{converted_jar_path}"
                        )
                    except Exception as e:
                        messagebox.showerror(t['error_title'], str(e))
                else:
                    messagebox.showerror(t['error_title'], t['version_required'])
            
            submit_button = tk.Button(version_window, text=t['submit'], command=on_submit)
            submit_button.pack(pady=10)
            
            version_window.mainloop()
        
        except Exception as e:
            messagebox.showerror(t['error_title'], str(e))

def main():
    updater = ModVersionUpdater()
    updater.main_process()

if __name__ == "__main__":
    main()
