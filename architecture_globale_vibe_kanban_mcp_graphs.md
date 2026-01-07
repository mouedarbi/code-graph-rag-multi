# Architecture cible — Pilotage d’agents LLM déterministe et aware

## 1. Objectif
Construire un système où :
- le LLM **n’est jamais source de vérité**
- l’awareness (où on en est, pourquoi, quoi respecter) est **host-side**
- le code, les décisions et les tâches sont **traçables et auditables**
- plusieurs clients LLM (CLI, Kanban) peuvent coopérer **sans réexpliquer le contexte**

---

## 2. Briques existantes (déjà fonctionnelles)

### 2.1 Vibe Kanban (socle)
- Gestion des **Projects / Tasks / Attempts**
- Exécution contrôlée des agents (Gemini, Qwen, Claude…)
- Agent Profiles (`default_profiles.json` + `profiles.json`)
- Logs, patches, worktrees Git
- Serveur **MCP** exposant les capacités Kanban

👉 Rôle : **orchestrateur**, **source de vérité opérationnelle**

---

### 2.2 Agents LLM (CLI et Kanban)
- Gemini CLI, Qwen CLI, etc.
- Exécutés :
  - soit directement dans Vibe Kanban
  - soit depuis le terminal utilisateur
- Tous peuvent se connecter aux MCP servers

👉 Rôle : **exécution**, jamais mémoire

---

### 2.3 Code-Graph-RAG (existant)
- Indexation du code
- Graphe structurel (fichiers, symboles, appels)
- Serveur **MCP** déjà présent

👉 Limite actuelle : **mono-repo**

---

## 3. Nouvelles briques à construire

### 3.1 Code-Graph-RAG multi-repo (brique 1)

#### But
- Indexer **plusieurs repositories**
- Fournir une vision structurelle fiable du code

#### Stockage
- **Memgraph** (ou équivalent)

#### Modèle minimal
- Repository
- File
- CodeSymbol

Chaque nœud est **scopé par repo_id**.

#### Règle clé
- Graphe **jetable / recalculable**
- Aucune donnée métier
- **READ-ONLY** pour les autres systèmes

#### Interface
- MCP Server exposant des requêtes :
  - list_repos
  - list_files(repo_id)
  - list_symbols(repo_id, file)
  - list_changed_symbols(repo_id, commit)

---

### 3.2 Graphe Projet / Awareness (brique 2)

#### But
- Stocker la **mémoire sémantique** du projet
- Décisions, exigences, fonctionnalités, historique

#### Stockage
- **Neo4j** (séparé de Memgraph)

#### Nœuds principaux
- Project
- Task
- Attempt
- Requirement
- Decision
- Feature
- Artifact
- CodeRef (référence vers le code, pas duplication)

#### Relations clés
- Task → HAS_ATTEMPT → Attempt
- Attempt → PRODUCED → Artifact
- Feature → DERIVED_FROM → Requirement
- Decision → JUSTIFIES → Feature
- Decision → SUPERSEDES → Decision
- Feature → IMPLEMENTED_BY → CodeRef

👉 Graphe **durable**, **versionné**, **jamais recalculé automatiquement**

---

## 4. Principe fondamental : séparation stricte

| Élément | Code-Graph | Graphe Projet |
|------|-----------|--------------|
| Nature | Structurel | Sémantique |
| Recalculable | Oui | Non |
| Source de vérité | Non | Oui |
| Écriture | Automatique | Contrôlée |
| Responsable | Code-Graph-RAG | Vibe Kanban |

👉 **Aucune écriture croisée directe**

---

## 5. Rôle du MCP (colle du système)

### 5.1 MCP Code-Graph
- Fournit des **faits techniques**
- Lecture seule

### 5.2 MCP Vibe Kanban
- Gestion des tasks / attempts
- Déclenchement des exécutions

### 5.3 Awareness Service (dans ou à côté de Vibe Kanban)
- Client MCP (Code-Graph)
- Écrivain unique de Neo4j
- Injecte le contexte au démarrage des attempts

---

## 6. Cycle réel d’exécution (exemple)

1. Task PLAN → produit des Artifacts (spec, requirements)
2. Vibe Kanban écrit Requirements / Decisions dans Neo4j
3. Task INIT démarre
4. Avant exécution :
   - récupération du PLAN validé
   - récupération des Decisions actives
   - récupération du snapshot Code-Graph
5. Injection d’un **context snapshot** dans l’agent
6. Code modifié
7. Vibe Kanban :
   - interroge MCP Code-Graph
   - identifie symboles touchés
   - crée CodeRef
   - relie Feature ↔ CodeRef

---

## 7. Gestion des corrections (anti-casse)

- Jamais modifier une Decision ou Requirement
- Toujours :
  - créer une nouvelle version
  - relier via SUPERSEDES

Le graphe permet :
- impact analysis
- rollback conceptuel
- audit

---

## 8. Ordre de construction recommandé

1. Rendre **Code-Graph-RAG multi-repo**
2. Définir le **schéma Neo4j minimal**
3. Créer le **pont MCP → Neo4j (host-side)**
4. Implémenter l’**injection automatique de contexte**
5. Étendre progressivement (tests, endpoints, UI)

---

## 9. Conclusion

- Vibe Kanban reste le **moteur**
- Les LLM restent des **exécutants**
- Le graphe projet devient la **mémoire vivante**
- Code-Graph-RAG fournit la **réalité du code**

👉 Architecture modulaire, robuste, évolutive, sans reconstruction future.

