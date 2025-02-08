# EnterpriseIA

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

*Système de Gestion d'Intelligence Artificielle pour Entreprises*

</div>

## 📋 Vue d'ensemble

EnterpriseIA est une plateforme Python robuste conçue pour gérer et déployer des services d'intelligence artificielle en entreprise. Elle s'appuie sur une architecture modulaire avec MySQL pour assurer :

- 👥 Gestion multi-utilisateurs
- 🔒 Contrôle d'accès basé sur les rôles (RBAC)
- 📊 Audit complet des actions
- ✅ Conformité aux normes d'entreprise

## ✨ Fonctionnalités principales

- **Gestion des Utilisateurs**
  - Authentification sécurisée
  - Système de rôles (Admin, DPO, Employé)
  - Hachage des mots de passe

- **Services IA**
  - Intégration locale via Mistral/Ollama
  - Support API OpenAI
  - Filtrage automatique des données sensibles

- **Sécurité & Conformité**
  - Journalisation détaillée
  - Anonymisation des données
  - Gestion des consentements

## 🚀 Démarrage rapide

### Prérequis

```bash
# Python 3.8+
python --version

# MySQL
mysql --version
```

### Installation

```bash
# Cloner le projet
git clone https://github.com/votre-username/enterpriseIA.git
cd enterpriseIA

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres
```

### Configuration de la base de données

```bash
# Initialiser la base de données
python initialize_database.py
```

### Lancement

```bash
python main.py
```

## 🏗️ Architecture

```
enterpriseIA/
├── app/
│   ├── gui/           # Interfaces utilisateur
│   ├── models/        # Modèles de données
│   ├── modules/       # Modules fonctionnels
│   └── system.py      # Logique principale
├── .env               # Configuration
├── databaseHandler.py # Gestion BDD
└── main.py           # Point d'entrée
```

## 👥 Rôles utilisateurs

| Rôle    | Permissions |
|---------|-------------|
| Admin   | Configuration système, gestion des utilisateurs |
| DPO     | Audit, rapports de conformité |
| Employé | Utilisation du chat IA |

## 🔒 Variables d'environnement

```env
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_NAME=enterpriseia
DB_PORT=3306
OPEN_AI_KEY=your-key
```

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 📧 Contact

Marc Arold ROSEMOND - [@LinkedIn](https://www.linkedin.com/in/marc-arold-rosemond/)

Lien du projet: [https://github.com/Marc-Arold/enterpriseIA](https://github.com/Marc-Arold/enterpriseia/tree/master/enterpriseIA)
