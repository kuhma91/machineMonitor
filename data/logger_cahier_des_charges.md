## Cahier des charges – Logger de machines

### 1. Objectif
Fournir un outil de logging manuel, léger et autonome, permettant de tracer toutes les interventions et incidents liés à un parc de machines industrielles.

### 2. Rôles et permissions
- **Usager** : peut uniquement créer des logs
- **Lead** : peut créer et consulter tous les logs
- **Superviseur** : peut créer, consulter et modifier les logs existants

### 3. Structure des données
Chaque log contient :
- **id** (généré automatiquement, UUID)
- **timestamp** (date et heure automatiques, ISO8601)
- **username** (OS login)
- **machineName** (sélection via ComboBox, liste issue du MachineManager)
- **logType** (enum : error, info, empty_consumable, reload)
- **message** (texte libre, court)
- **projectId** (identifiant projet/commande)
- **modifiedBy** (login modificateur, auto)
- **modifiedAt** (date/heure modif, auto)

### 4. Stockage et purge
- **Dossier permanent** : `data/logger/` contenant le fichier JSON principal
- **Dossier temporaire** : `data/_TEMP/logger/<username>/` pour sauvegardes inachevées
- Purge automatique : suppression des logs temporaires de plus de 3 jours à chaque lancement

### 5. Interface utilisateur
- Calquée sur le MachineManager : une seule fenêtre pour créer, éditer et supprimer
- **Boutons** : Add (créer), Edit (modifier), Sub (supprimer)
- **UI de création** : ComboBox pour `machineName`, champs obligatoires, bouton `save` désactivé tant que tous les champs ne sont pas remplis
- **UI de modification** : accès aux logs existants, activation des champs modifiables, enregistrement des champs `modifiedBy` et `modifiedAt`

### 6. Workflow
1. **Création** : l’usager clique sur « Add », remplit tous les champs et valide.
2. **Consultation** : le lead peut ouvrir la liste des logs, filtrer par machine, type ou date.
3. **Édition** : le superviseur sélectionne un log, clique sur « Edit », modifie et enregistre ; les champs `modifiedBy` et `modifiedAt` sont mis à jour.

---
Ce cahier des charges servira de référence pour le développement du Logger avant la migration ultérieure vers SQL + API.

