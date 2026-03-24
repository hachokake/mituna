# 📊 Guide des Statistiques Avancées - Mituna

## Vue d'ensemble

Le nouvel onglet **Statistiques Avancées** offre une analyse complète et professionnelle des réponses à vos sondages avec des graphiques interactifs et des indicateurs clés de performance (KPI).

## 🎯 Fonctionnalités Principales

### 1. **Tableau de Bord des Statistiques Générales**

Quatre indicateurs clés affichés en haut de page:
- **Réponses Totales**: Nombre total de participants au sondage
- **Questions**: Nombre total de questions dans le sondage
- **Taux de Complétion**: Pourcentage moyen de questions répondues par participant
- **Statut du Sondage**: Actif ou Inactif

### 2. **Graphique d'Évolution Temporelle**

- Affiche l'évolution des réponses sur les **30 derniers jours**
- Graphique en ligne interactif avec Chart.js
- Permet de visualiser les tendances et les pics de participation
- Survolez les points pour voir le détail par jour

### 3. **Statistiques par Question**

#### Pour les questions à choix (Single/Multiple):
- **Graphique en barres horizontales** pour chaque option
- Affichage du nombre de votes et du pourcentage
- **Informations clés**:
  - Total des votes
  - Taux de réponse
  - Réponse la plus populaire
  - Nombre de votes maximum

#### Pour les questions de type notation (Rating):
- **Graphique en barres colorées** pour chaque note (1 à 5 étoiles)
- Dégradé de couleurs: Rouge (1⭐) → Vert (5⭐)
- **Informations clés**:
  - Note moyenne sur 5
  - Total des évaluations
  - Taux de réponse
  - Note la plus fréquente (mode)

#### Pour les questions textuelles:
- **Statistiques textuelles**:
  - Nombre total de réponses textuelles
  - Taux de réponse
  - Longueur moyenne des réponses (en caractères)
- **Échantillon de réponses**: Affichage des 10 premières réponses pour lecture rapide

## 📥 Export PDF

### Télécharger les Statistiques

Un bouton en bas de page permet d'exporter **toutes les statistiques en PDF**:

```
🔽 Télécharger les Statistiques (PDF)
```

**Fonctionnement**:
1. Cliquez sur le bouton
2. Le système capture automatiquement toute la page avec graphiques
3. Génération d'un PDF multi-pages haute qualité
4. Téléchargement automatique: `Statistiques_Nom-du-sondage_2026-03-24.pdf`

**Caractéristiques**:
- Format A4 professionnel
- Résolution haute qualité (scale × 2)
- Tous les graphiques inclus
- Pagination automatique si contenu long

## 🚀 Accès aux Statistiques

### Depuis le Dashboard Admin:
1. Connectez-vous à l'admin: `/admin/`
2. Dans le tableau des sondages
3. Cliquez sur l'icône **📈** (Statistiques avancées) pour chaque sondage

### Depuis la page Résultats:
1. Sur la page des résultats d'un sondage
2. Cliquez sur le bouton **"Statistiques Avancées"** en haut

### Navigation:
- **Résultats Simples** → **Statistiques Avancées** (et vice versa)
- Retour au tableau de bord depuis les deux pages

## 📱 Responsive Design

L'interface des statistiques est **100% responsive**:
- ✅ Desktop: Graphiques larges et détaillés
- ✅ Tablette: Adaptation automatique en 2 colonnes
- ✅ Smartphone: Graphiques empilés verticalement, lecture optimisée

## 🎨 Design Professionnel

### Palette de Couleurs:
- **En-tête**: Dégradé vert (#10b981 → #059669)
- **Graphiques**: 8 couleurs vibrantes et distinctes
- **Cartes**: Fond blanc avec bordures subtiles
- **Hover effects**: Animations au survol pour interactivité

### Typographie:
- Titres: Police bold, grande taille
- Valeurs statistiques: Très grandes et gras (font-weight: 800)
- Labels: Petites majuscules espacées (uppercase, letter-spacing)

## 🔍 Informations Calculées

### Taux de Réponse:
```
(Nombre de réponses à la question / Nombre total de participants) × 100
```

### Taux de Complétion:
```
(Nombre total de réponses / (Nombre de questions × Nombre de participants)) × 100
```

### Note Moyenne (Rating):
```
Somme de toutes les notes / Nombre de notes
```

### Pourcentage par Choix:
```
(Votes pour ce choix / Total des votes) × 100
```

## 🛠️ Technologies Utilisées

- **Chart.js 4.4.0**: Bibliothèque de graphiques interactifs
- **jsPDF 2.5.1**: Génération de PDF côté client
- **html2canvas 1.4.1**: Capture d'écran HTML vers image
- **Font Awesome 6.4**: Icônes professionnelles
- **Bootstrap 5**: Framework CSS responsive

## 📊 Exemples d'Utilisation

### Cas d'usage 1: Analyse de Satisfaction
Un sondage de satisfaction client avec questions de notation:
- Visualisez rapidement la note moyenne
- Identifiez les questions avec les notes les plus basses
- Export PDF pour présentation aux managers

### Cas d'usage 2: Sondage d'Opinion
Sondage avec choix multiples:
- Identifiez les réponses les plus populaires
- Comparez les taux de réponse entre questions
- Graphiques en barres colorées pour rapports

### Cas d'usage 3: Enquête Qualitative
Questions ouvertes textuelles:
- Consultez un échantillon des réponses
- Analysez la longueur moyenne des réponses
- Évaluez le taux de participation

## ⚡ Performance

Le système est optimisé pour gérer de grands volumes:
- ✅ Jusqu'à **1 500+ réponses** sans ralentissement
- ✅ Préchargement des données avec `prefetch_related()`
- ✅ Calculs statistiques efficaces
- ✅ Rendu graphique optimisé (Chart.js)

## 🆘 Résolution de Problèmes

### Le graphique ne s'affiche pas:
- Vérifiez que JavaScript est activé dans votre navigateur
- Rechargez la page (F5)
- Vérifiez votre connexion internet (Chart.js chargé depuis CDN)

### L'export PDF échoue:
- Assurez-vous d'utiliser un navigateur moderne (Chrome, Firefox, Edge)
- Vérifiez que les pop-ups ne sont pas bloqués
- Attendez le chargement complet des graphiques avant d'exporter

### Les graphiques sont tronqués sur mobile:
- Faites tourner votre appareil en mode paysage pour une meilleure vue
- Zoomez avec deux doigts pour voir les détails
- Les graphiques s'adaptent automatiquement à la largeur d'écran

## 📈 Évolutions Futures (Suggestions)

Fonctionnalités possibles:
- Export Excel/CSV des données brutes
- Comparaison entre plusieurs sondages
- Filtres avancés (date, participant, etc.)
- Graphiques supplémentaires (courbes, camemberts, radar)
- Partage de statistiques publiques (lien unique)

---

**Mituna** - Plateforme de Sondages 100% Congolaise 🇨🇩

Pour toute question ou suggestion: contactez l'administrateur de votre plateforme.
