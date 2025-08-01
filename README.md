# Atlas Technique — Projet machineMonitor

---
## Sommaire

1. [Contexte et objectifs](#1-Contexte-et-objectifs)
2. [architecture générale](#2-architecture-générale)
3. [Structure du projet](#3-Structure-du-projet)
4. [Outils](#4-Outils)
   - [4.1 Token Manager](#41-Token-Manager)
   - [4.2 Machine Manager](#42-machine-manager)
   - [4.3 Logger](#43-logger)
   - [4.4 API (FastAPI)](#44-api-fastapi)
   - [4.5 Base de données SQLite](#45-base-de-données-sqlite)
5. [Glossaire et annexes](#5-glossaire-et-annexes)

---

## 1. Contexte et objectifs
**Contexte métier** : 

L’entreprise gère un parc de machines-outils en usine. 
Elle souhaite digitaliser la gestion de son parc machine industriel et des accès employés. 
Le besoin exprimé est double :
- **Suivi structuré des équipements** : état, localisation, informations techniques.
- **Gestion des utilisateurs** : identification, autorisations, traçabilité des interventions.

**L’objectif de ce projet est de proposer une interface unifiée pour** :
- la gestion des **machines industrielles**,
- le suivi **des utilisateurs et de leurs autorisations**,
- le **logging** des actions et événements.

L’outil a été conçu pour répondre aux besoins d’un environnement industriel :
- multi-utilisateurs,
- suivi des opérations (log complet),
- sécurité et simplicité d’accès,
- gestion granulaire des droits d’accès et d’édition.

Il permet une **centralisation** des données, une **traçabilité complète**, et une **interface graphique claire** (PySide2).

---

## 2. architecture générale
Le projet s’organise autour d’une architecture modulaire Python/PySide2/SQLite/REST API, chaque module remplissant un rôle clair dans le fonctionnement global. 

| Module         | Rôle principal                                | Interface         |
|----------------|-----------------------------------------------|-------------------|
| `tokenManager` | Gestion des employés et droits d’accès        | UI (PySide2)      |
| `machineManager` | Gestion et édition des machines               | UI (PySide2)      |
| `logger`       | Journalisation automatique des modifications  | UI (PySide2)      |
| `api`          | Accès distant aux données via FastAPI         | API REST          |
| `sqlLib`       | Accès centralisé aux données SQLite           | Backend SQLite    |

Ces outils interagissent avec une **base de données locale** (JSON et SQLite) et peuvent être facilement migrés vers un serveur ou scalés à distance.

**Approche choisie :**

 - SQLite : base embarquée ACID, introspection, légèreté. 
 - DDL : tables = onglets Excel, colonnes typées, PK/FK, NOT NULL. 
 - sqlLib.py : couche d’accès SQL réutilisable, commit/rollback. 
 - FastAPI : framework ASGI déclaratif, Swagger UI auto. 
 - Uvicorn : serveur ASGI performant. 
 - Pydantic : validation/sérialisation JSON ↔ Python. 
 - cURL : tests CLI des endpoints. 


**Fonctionnement global** :

Chacun peut fonctionner **indépendamment**, mais ils partagent :
- un **dossier commun de données** (`/data/...`)
- des **librairies communes** (stringLib, uiLib, infoLib, sqlLib)
- un **workflow homogène** (UI → Data → Log → API)


```
     ┌──────────────┐
     │ Utilisateur  │
     └────┬─────────┘
          │ (UI)
     ┌────▼─────┐                 ┌──────────────┐
     │ PySide2  │  <----------->  │  FastAPI     │
     └────┬─────┘                 └──────────────┘
          │                           │
          ▼                           ▼
  ┌──────────────┐        ┌─────────────────────┐
  │ JSON (local) │  <-->  │ SQLite (SQL Sync)   │
  └──────────────┘        └─────────────────────┘
```

---


## 3. Structure du projet

```
machineMonitor/
│
├── __init__.py
├── README.md
│
├── api/
│   ├── __init__.py
│   ├── core.py
│   ├── main.py
│   ├── models.py
│   └── test.py
│
├── data/
│   ├── employs/*.json    <- nom de l'employe
│   ├── machines/*.json    <- nom de la machine
│   └── logs/*.json    <- uuid du log
│
├── library/
│   └── general/
│       ├── infoLib.py
│       ├── sqlLib.py
│       ├── stringLib.py
│       └── uiLib.py
│
├── logger/
│   ├── core.py
│   ├── main.py
│   └── ui.py
│
├── machineManager/
│   ├── core.py
│   ├── main.py
│   └── ui.py
│
└── tokenManager/
    ├── core.py
    ├── main.py
    └── ui.py

```

---

## 4. Outils

### 4.1 token Manager
#### Module : tokenManager

### Problématique ciblée

Certaines opérations critiques ou modules sensibles (accès admin, suppression, validation, etc.) doivent être protégés par un mécanisme de contrôle d'accès simple mais sûr. Le module `tokenManager` répond à ce besoin en permettant la génération, le suivi, et la gestion de jetons d'accès temporaires.

Ce système de jeton remplace une authentification complexe (LDAP, OAuth) dans un contexte local-first sans infrastructure IT lourde.

---

### Intégration dans le workflow

Le module peut être appelé par d'autres composants (logger, API) pour vérifier les droits ou valider une opération critique.

Fonctionne en conjonction avec :

- le Logger : traçabilité des actions liées à un token
- l'API : contrôle d'accès si la route requiert un token valide

---

### Utilisateurs ciblés

- Superviseurs
- Chefs d'équipe
- Administrateurs

---

### Fonctions principales et validation

#### Interface UI (`tokenManager.ui`)

- Liste des tokens existants
- Champs : nom de l'utilisateur, usage, date de création, durée, statut (actif/expiré)
- Boutons : `add`, `delete`, `copy`, `filter`
- Création de token UUID avec horodatage

Tests effectués :

- Génération de token avec durée prédéfinie
- Suppression de token
- Filtrage par validité ou nom
- Copie du token dans le presse-papiers

#### Fonctionnement interne (`tokenManager.main`)

- Initialisation de l'UI avec la liste des tokens depuis JSON
- Validation de la durée et nom avant création
- Utilisation de `uuid.uuid4()` pour un identifiant unique
- Mise à jour automatique du statut (actif/expiré)

#### Backend (`tokenManager.core`)

- `generateToken(user, duration, usage)` : crée un dictionnaire formaté avec date de création et date limite
- `writeToken(tokenData)` : écrit dans `/data/tokens/<uuid>.json`
- `readTokens()` : charge tous les tokens existants pour affichage ou vérification
- `deleteToken(uuid)` : supprime le fichier correspondant
- `isTokenValid(token)` : retourne True si date limite > date actuelle

---

### Lien avec les autres outils

- **Logger** : peut enregistrer les actions faites sous un token
- **API** : certaines routes peuvent exiger un token dans l'en-tête HTTP
- **UI générales** : les boutons sensibles peuvent être conditionnés à un token actif

---

### Utilisation concrète

#### Lancer le gestionnaire de tokens

```bash
python -m machineMonitor.tokenManager.main
```

#### Utiliser l'interface

- **Ajouter un token** : bouton ➕ `add`, remplir nom/usage/durée, `save`
- **Copier un token** : bouton `copy` à côté du champ UUID
- **Supprimer** : bouton 🗑️ `delete`, confirmer
- **Filtrer** : menu en haut : `Tous`, `Actifs`, `Expirés`, etc.

---

### Données utilisées

Fichiers JSON stockés dans `data/tokens/*.json`

Exemple :

```json
{
  "uuid": "3d1b126e-9cf6-432e-8c4b-cb19b7412ec4",
  "user": "Jean Dupont",
  "usage": "Accès Logger",
  "created_at": "2025-07-28T15:12:00",
  "valid_until": "2025-08-28T15:12:00",
  "status": "active"
}
```

---


### 4.2 Machine Manager
#### Module : MachineManager

#### Problématique ciblée
Dans un contexte industriel de suivi d'équipements, il est impératif de pouvoir :
- centraliser les données des machines (identité, statut, secteur, fabricant, etc.)
- ajouter, modifier ou supprimer les machines simplement
- visualiser les informations à jour et laisser des commentaires ou historiques

Ce module répond au besoin de gestion directe des machines via une interface accessible aux opérateurs, chefs d’équipe ou superviseurs.

---

#### Intégration dans le workflow
Le `MachineManager` est l’un des modules principaux. Il exploite la base de données locale (JSON ou SQLite selon implémentation), fournit un CRUD visuel pour les machines et s’intègre au Logger (commentaires horodatés, tracking des actions).

Il est utilisé :
- en local via UI (PySide2)
- potentiellement via API REST dans une suite plus large

---

#### Utilisateurs ciblés
- Opérateurs : ajout de commentaires, consultation
- Responsables de secteur : ajout/suppression de machines
- Superviseurs : contrôle global, modifications critiques

---

#### Fonctions principales et validation
##### Interface UI (`machineManager.ui`)
- Combobox de sélection de machine
- Boutons : `edit`, `add`, `delete`
- Champs modifiables selon mode
- Bloc "commentaire" repliable
- Boutons `save`, `cancel`

Validé manuellement :
- ajout : machine non dupliquée, champs requis remplis
- modification : champs activés, feedback visuel
- suppression : boîte de confirmation

##### Fonctionnement général (`machineManager.main`)
- `mode`: 'read' / 'edit' / 'add' → interface réactive
- `fillUi()` : remplit les champs depuis les fichiers JSON
- `updateField()` : met à jour les champs selon machine sélectionnée
- `checkGivenInfo()` : empêche les doublons, vérifie la complétude
- `saveNewMachineInfo()` : écrit les données dans le fichier JSON associé
- `foldCommand()` : toggle d'affichage commentaire

Couplé au logger pour garder trace des actions utilisateurs (hors implémentation directe dans ce module).

##### Backend (`machineManager.core`)
- `getMachineData()` : parse les fichiers JSON dans `/data/machines`
- `addEntry(name, data)` : écrit ou remplace le fichier JSON de la machine
- `deleteEntry(name)` : supprime le fichier associé
- `NEEDED_INFOS` : dictionnaire des champs requis (secteur, usage, etc.)

---

#### Lien avec les autres outils
- **Logger** : chaque ajout/modification peut être historisé (si couplé à un appel logger)
- **TokenManager** : seuls les utilisateurs avec droits suffisants (lead/supervisor) peuvent modifier ou supprimer
- **API** (optionnel) : ce module peut être encapsulé dans une route POST/PUT/DELETE

---

#### Utilisation concrète
##### Lancer le manager
```bash
python -m machineMonitor.machineManager.main
```

##### Utiliser l'interface
- **Ajouter une machine** : bouton ➕ `add`, remplir les champs, `save`
- **Modifier** : bouton ✏️ `edit`, faire les changements, `save`
- **Supprimer** : bouton 🗑️ `delete`, confirmer
- **Commentaires** : cliquer sur `- commentaire` pour déplier, écrire

---

#### Données utilisées
- `data/machines/*.json` : 1 fichier par machine (nom = identifiant unique)
```json
{
  "sector": "1A",
  "usage": "CNC",
  "manufacturer": "Mazak",
  "serial_number": "123456",
  "year_of_acquisition": "2019",
  "in_service": "Oui",
  "comment": "Changement de courroie prévu en août."
}
```

---

#### Tests et vérifications
- Interface manuellement testée (ajout, édition, suppression)
- Validation des champs → pas de vide ni doublon autorisé
- Fichiers JSON inspectés en sortie → structure conforme

---

#### Sécurité / Accès
Aucun contrôle intégré dans ce module — doit être couplé à un `TokenManager` ou équivalent pour limiter les droits d’accès aux actions critiques (`edit`, `delete`).

---

### 4.3 token Manager
#### Module : Logger (core + UI + Viewer)


#### Problématique ciblée

Dans un environnement industriel, la traçabilité des actions humaines est essentielle. Le logger permet :

- de garder une trace des interventions, incidents, entretiens ou remarques,
- de dater, structurer et centraliser les commentaires,
- de réduire la perte d'information sur les opérations manuelles.

Ce module vise à fournir un carnet de bord digital associé aux machines, exploitables aussi bien par les opérateurs que par les superviseurs.

---

#### Intégration dans le workflow

Le `Logger` est un module transversal :

- alimenté via une interface UI (commentaire horodaté sur une machine ou un poste),
- lié à l'utilisateur actif (via nom ou token),
- les données sont stockées localement au format JSON, puis synchronisées avec SQLite pour un usage API.

Il est utilisé :

- en local via UI PySide2
- en lecture depuis l'API REST (endpoints logs)

---

#### Utilisateurs ciblés

- Opérateurs : saisie des commentaires sur machine/poste
- Responsables : validation, complétion, vérification des historiques
- Maintenance / QSE : exploitation des logs pour analyse

---

#### Fonctions principales et validation

##### Interface UI (`logger.ui`)

- Liste des machines disponibles
- Zone de saisie texte pour le commentaire
- Menu déroulant pour catégorie/type d'intervention
- Boutons `add`, `edit`, `delete`, `save`
- Champs de date, heure, utilisateur auto-remplis

Validations assurées :

- pas d'écriture sans texte ou machine sélectionnée
- modification impossible si log verrouillé
- suppression avec confirmation

##### Fonctionnement général (`logger.main`)

- `mode`: read / write / edit
- `loadLogs()` : lecture des JSON
- `saveLog()` : écriture ou mise à jour du fichier log (UUID)
- `filterLogs()` : permet la recherche par machine, date, utilisateur

##### Backend (`logger.core`)

- `getAllLogs()` : parse tous les fichiers JSON dans `/data/logs`
- `addLogEntry()` : crée un fichier avec UUID, timestamp, metadata, commentaire
- `deleteLogEntry()` : supprime un fichier spécifique
- `updateLogEntry()` : édite un commentaire

##### Viewer (inclus dans UI)

- Liste des logs triables par date
- Filtres dynamiques (par utilisateur, machine, type d'intervention)
- Affichage du contenu en mode lecture seule

Testé manuellement :

- ajout, modification, suppression
- tri et filtre
- comportement en erreur (machine absente, champ vide)

---

#### Lien avec les autres outils

- **MachineManager** : chaque machine dispose de ses propres logs historisés
- **TokenManager** : le champ "utilisateur" peut être prérempli via token actif
- **API** : tous les logs sont synchronisés dans la base SQLite pour consultation via requêtes REST (GET /logs)

---

#### Utilisation concrète

##### Lancer le logger

```bash
python -m machineMonitor.logger.main
```

##### Ajouter un log

- Sélectionner une machine
- Renseigner le type et le commentaire
- Cliquer sur `save`

##### Modifier ou supprimer

- Sélectionner un log existant
- Cliquer sur `edit` ou `delete` puis valider

##### Utiliser les filtres

- Choisir des critères dans les menus déroulants
- Les logs affichés s’adaptent dynamiquement

---

#### Données utilisées

- `data/logs/*.json` : 1 fichier par log (nommé via UUID)

```json
{
  "uuid": "8300c91a-fc2b-43d8-93ac-4d1b33b82fdb",
  "timestamp": "2025-07-25T14:37:00",
  "machine": "toto",
  "user": "antoine",
  "type": "maintenance",
  "comment": "changement de buse fait."
}
```

