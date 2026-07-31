"""Référentiel des 150 KPI LMS PRO Enterprise (100 Employés + 50 Formateurs).

Chaque entrée définit la METADATA d'un indicateur (code, libellé, unité, objectif).
Les VALEURS sont calculées en direct depuis la base par apps.kpi_pro.engine — ce fichier
ne contient aucune donnée mesurée, uniquement le référentiel (objectifs = cibles de gestion,
pas des données constatées).
"""

# op: 'gte' (>=), 'lte' (<=), 'none' (pas de statut calculé — indicateur informatif)
EMPLOYEE_CATEGORIES = [
    {
        'id': 'A', 'label': "Engagement dans la Formation", 'chart': 'bar',
        'kpis': [
            ('KPI 1', 'inscription_rate', "Taux d'inscription aux formations", '%', 'gte', 90),
            ('KPI 2', 'participation_rate', "Taux de participation", '%', 'gte', 80),
            ('KPI 3', 'weekly_connection_rate', "Taux de connexion hebdomadaire", '%', 'gte', 85),
            ('KPI 4', 'avg_time_per_week_hours', "Temps moyen/plateforme par semaine", 'h', 'gte', 3),
            ('KPI 5', 'avg_courses_followed', "Nombre de formations suivies", 'nb', 'gte', 5),
            ('KPI 6', 'avg_paths_completed', "Nombre de parcours terminés", 'nb', 'gte', 3),
            ('KPI 7', 'completion_rate', "Taux de complétion", '%', 'gte', 80),
            ('KPI 8', 'dropout_rate', "Taux d'abandon", '%', 'lte', 10),
            ('KPI 9', 'avg_sessions_per_week', "Sessions par semaine (moy.)", 'nb', 'gte', 4),
            ('KPI 10', 'recent_activity_rate', "Activité récente (actifs ≤ 7 jours)", '%', 'gte', 85),
        ],
    },
    {
        'id': 'B', 'label': "Assiduité", 'chart': 'donut_heatmap',
        'kpis': [
            ('KPI 11', 'virtual_attendance_rate', "Présence aux classes virtuelles", '%', 'gte', 90),
            ('KPI 12', 'punctuality_rate', "Ponctualité (sessions à l'heure)", '%', 'gte', 85),
            ('KPI 13', 'justified_absences', "Nombre d'absences justifiées", 'nb', 'lte', 5),
            ('KPI 14', 'late_count', "Nombre de retards", 'nb', 'lte', 3),
            ('KPI 15', 'workshop_participation_rate', "Participation aux ateliers", '%', 'gte', 75),
            ('KPI 16', 'forum_participation_rate', "Participation aux forums", '%', 'gte', 60),
            ('KPI 17', 'practical_work_rate', "Participation aux travaux pratiques", '%', 'gte', 80),
            ('KPI 18', 'video_full_watch_rate', "Temps de visionnage vidéos (complet)", '%', 'gte', 85),
            ('KPI 19', 'document_read_rate', "Temps de lecture documents", '%', 'gte', 70),
            ('KPI 20', 'deadline_respect_rate', "Respect des échéances (devoirs)", '%', 'gte', 90),
        ],
    },
    {
        'id': 'C', 'label': "Performance Pédagogique", 'chart': 'line_histogram',
        'kpis': [
            ('KPI 21', 'avg_global_score', "Score moyen global", '%', 'gte', 75),
            ('KPI 22', 'best_score', "Meilleur score individuel", '%', 'none', None),
            ('KPI 23', 'worst_score', "Score le plus faible", '%', 'alert_lte', 40),
            ('KPI 24', 'avg_exams_passed', "Nombre d'examens réussis", 'nb', 'none', None),
            ('KPI 25', 'avg_exams_failed', "Nombre d'examens échoués", 'nb', 'lte', 2),
            ('KPI 26', 'exam_success_rate', "Taux de réussite aux examens", '%', 'gte', 80),
            ('KPI 27', 'avg_attempts', "Nombre de tentatives moyen", 'nb', 'lte', 3),
            ('KPI 28', 'avg_days_to_pass', "Temps moyen pour réussir (jours)", 'j', 'lte', 14),
            ('KPI 29', 'score_trend_mom', "Évolution des notes (mois n vs n-1)", 'pts', 'gte', 0),
            ('KPI 30', 'monthly_progress', "Progression mensuelle", '%/mois', 'gte', 2),
            ('KPI 31', 'yearly_progress', "Progression annuelle", '%/an', 'gte', 15),
            ('KPI 32', 'difficulties_detected', "Difficultés détectées (quiz < 50%)", 'nb', 'lte', 3),
            ('KPI 33', 'hardest_modules', "Modules les plus difficiles", 'liste', 'none', None),
            ('KPI 34', 'best_mastered_modules', "Modules les mieux maîtrisés", 'liste', 'none', None),
            ('KPI 35', 'global_mastery_level', "Niveau global de maîtrise", '%', 'gte', 75),
        ],
    },
    {
        'id': 'D', 'label': "Compétences", 'chart': 'radar_heatmap',
        'kpis': [
            ('KPI 36', 'skills_acquired', "Nombre de compétences acquises", 'nb', 'gte', 8),
            ('KPI 37', 'avg_skill_level_pct', "Niveau moyen de compétence", '%', 'gte', 75),
            ('KPI 38', 'critical_skills_mastered', "Compétences critiques maîtrisées", '%', 'gte', 100),
            ('KPI 39', 'skills_gap_count', "Compétences manquantes (gap)", 'nb', 'lte', 0),
            ('KPI 40', 'skill_gap_global', "Skill Gap global (écart requis/actuel)", '%', 'lte', 15),
            ('KPI 41', 'expired_skills', "Compétences expirées (> 2 ans)", 'nb', 'lte', 0),
            ('KPI 42', 'certified_skills', "Compétences certifiées officiellement", 'nb', 'gte', 3),
            ('KPI 43', 'skill_progress_6m', "Progression des compétences (6 mois)", 'pts', 'gte', 10),
            ('KPI 44', 'job_coverage_rate', "Couverture compétences du poste", '%', 'gte', 100),
            ('KPI 45', 'versatility_index', "Indice de polyvalence", 'nb postes', 'gte', 2),
            ('KPI 46', 'technical_level', "Niveau technique", '%', 'gte', 80),
            ('KPI 47', 'business_level', "Niveau métier", '%', 'gte', 80),
            ('KPI 48', 'behavioral_level', "Niveau comportemental", '%', 'gte', 75),
            ('KPI 49', 'digital_level', "Niveau numérique / digital", '%', 'gte', 70),
            ('KPI 50', 'igc_index', "Indice global de compétences (IGC)", '%', 'gte', 78),
        ],
    },
    {
        'id': 'E', 'label': "Développement Professionnel", 'chart': 'bar',
        'kpis': [
            ('KPI 51', 'dev_objectives_reached', "Objectifs de développement atteints", '%', 'gte', 100),
            ('KPI 52', 'dev_objectives_late', "Objectifs en retard", 'nb', 'lte', 0),
            ('KPI 53', 'pdi_completion', "PDI (Plan Dev. Individuel) réalisé", '%', 'gte', 80),
            ('KPI 54', 'official_certifications', "Certifications officielles obtenues", 'nb', 'gte', 2),
            ('KPI 55', 'training_hours_done', "Heures de formation réalisées", 'h', 'gte', 40),
            ('KPI 56', 'training_hours_left', "Heures de formation restantes", 'h', 'lte', 5),
            ('KPI 57', 'recommended_trainings_done', "Formations recommandées terminées", '%', 'gte', 75),
            ('KPI 58', 'mandatory_trainings_done', "Formations obligatoires terminées", '%', 'gte', 100),
            ('KPI 59', 'promotion_eligibility', "Éligibilité à une promotion", 'Score', 'gte', 80),
            ('KPI 60', 'mobility_readiness', "Préparation à la mobilité interne", '%', 'gte', 70),
        ],
    },
    {
        'id': 'F', 'label': "Performance Opérationnelle", 'chart': 'bar_roi',
        'kpis': [
            ('KPI 61', 'productivity_before', "Productivité avant formation", '%', 'none', None),
            ('KPI 62', 'productivity_after', "Productivité après formation", '%', 'gte_delta', 15),
            ('KPI 63', 'quality_evolution', "Évolution de la qualité (erreurs)", '%', 'gte_delta', 10),
            ('KPI 64', 'error_reduction', "Réduction des erreurs opérationnelles", '%', 'lte', -20),
            ('KPI 65', 'processing_time_reduction', "Temps de traitement (tâches clés)", '%', 'lte', -15),
            ('KPI 66', 'procedure_respect', "Respect des procédures", '%', 'gte', 95),
            ('KPI 67', 'internal_satisfaction', "Satisfaction client interne/externe", '%', 'gte', 85),
            ('KPI 68', 'post_training_incidents', "Nombre d'incidents post-formation", 'nb', 'lte', 0),
            ('KPI 69', 'sla_respect', "Respect des SLA", '%', 'gte', 98),
            ('KPI 70', 'innovations_proposed', "Innovations proposées", 'nb', 'gte', 1),
            ('KPI 71', 'problem_resolution_rate', "Taux de résolution de problèmes", '%', 'gte', 80),
            ('KPI 72', 'business_goals_reached', "Atteinte des objectifs métier", '%', 'gte', 100),
            ('KPI 73', 'strategic_projects_contrib', "Contribution aux projets stratégiques", '%', 'gte', 70),
            ('KPI 74', 'global_performance_score', "Score de performance globale", '%', 'gte', 80),
            ('KPI 75', 'training_roi', "ROI individuel de la formation", '%', 'gte', 500),
        ],
    },
    {
        'id': 'G', 'label': "Soft Skills", 'chart': 'radar',
        'kpis': [
            ('KPI 76', 'leadership', "Leadership", '%', 'gte', 70),
            ('KPI 77', 'communication', "Communication", '%', 'gte', 75),
            ('KPI 78', 'teamwork', "Travail d'équipe", '%', 'gte', 80),
            ('KPI 79', 'adaptability', "Adaptabilité", '%', 'gte', 70),
            ('KPI 80', 'time_management', "Gestion du temps", '%', 'gte', 75),
            ('KPI 81', 'stress_management', "Gestion du stress", '%', 'gte', 65),
            ('KPI 82', 'creativity', "Créativité & Innovation", '%', 'gte', 60),
            ('KPI 83', 'initiative', "Esprit d'initiative", '%', 'gte', 70),
            ('KPI 84', 'decision_making', "Prise de décision", '%', 'gte', 72),
            ('KPI 85', 'emotional_intelligence', "Intelligence émotionnelle", '%', 'gte', 70),
        ],
    },
    {
        'id': 'H', 'label': "Évaluation 360°", 'chart': 'radar_multi',
        'kpis': [
            ('KPI 86', 'eval_self', "Auto-évaluation", '%', 'none', None),
            ('KPI 87', 'eval_manager', "Évaluation du manager", '%', 'none', None),
            ('KPI 88', 'eval_hr', "Évaluation RH", '%', 'none', None),
            ('KPI 89', 'eval_peers', "Évaluation des collègues", '%', 'none', None),
            ('KPI 90', 'eval_internal_clients', "Évaluation clients internes", '%', 'none', None),
            ('KPI 91', 'eval_trainers', "Évaluation des formateurs", '%', 'none', None),
            ('KPI 92', 'eval_progress', "Progression depuis dernière éval.", 'pts', 'gte', 0),
            ('KPI 93', 'leadership_potential', "Potentiel de leadership", '%', 'gte', 70),
            ('KPI 94', 'succession_index', "Indice de succession", '%', 'gte', 60),
            ('KPI 95', 'global_360_score', "Score global 360°", '%', 'gte', 78),
        ],
    },
    {
        'id': 'I', 'label': "IA & Analytique", 'chart': 'scatter_donut',
        'kpis': [
            ('KPI 96', 'dropout_risk_ai', "Risque d'abandon (IA)", '%', 'alert_gte', 65),
            ('KPI 97', 'failure_probability_ai', "Probabilité d'échec (IA)", '%', 'alert_gte', 50),
            ('KPI 98', 'evolution_potential_ai', "Potentiel d'évolution (IA)", '%', 'gte', 70),
            ('KPI 99', 'ai_recommendation', "Recommandation IA de formation", 'liste', 'none', None),
            ('KPI 100', 'lpi_index', "Learning Performance Index (LPI)", '%', 'gte', 80),
        ],
    },
]

TRAINER_CATEGORIES = [
    {
        'id': 'A', 'label': "Préparation Pédagogique", 'chart': 'bar',
        'kpis': [
            ('KPI F1', 'content_quality', "Qualité des supports pédagogiques", '%', 'gte', 80),
            ('KPI F2', 'content_freshness', "Actualisation des contenus (≤ 6 mois)", '%', 'gte', 100),
            ('KPI F3', 'course_structuring', "Structuration des cours", '%', 'gte', 85),
            ('KPI F4', 'objectives_respect', "Respect des objectifs pédagogiques", '%', 'gte', 100),
            ('KPI F5', 'resource_diversity', "Pertinence et diversité des ressources", '%', 'gte', 80),
        ],
    },
    {
        'id': 'B', 'label': "Animation des Formations", 'chart': 'bar',
        'kpis': [
            ('KPI F6', 'clarity', "Clarté des explications (notes apprenants)", '%', 'gte', 80),
            ('KPI F7', 'subject_mastery', "Maîtrise du sujet (éval. expert)", '%', 'gte', 90),
            ('KPI F8', 'communication_quality', "Qualité de la communication", '%', 'gte', 80),
            ('KPI F9', 'audience_engagement', "Capacité à captiver l'auditoire", '%', 'gte', 75),
            ('KPI F10', 'time_management', "Gestion du temps (respect planning)", '%', 'gte', 90),
            ('KPI F11', 'question_reactivity_hours', "Gestion des questions (réactivité)", 'min', 'lte', 4),
            ('KPI F12', 'dynamism', "Dynamisme et énergie perçue", '%', 'gte', 78),
            ('KPI F13', 'interactivity', "Interactivité avec les apprenants", '%', 'gte', 70),
            ('KPI F14', 'practical_demo_quality', "Qualité des démonstrations pratiques", '%', 'gte', 85),
            ('KPI F15', 'level_adaptation', "Adaptation au niveau des apprenants", '%', 'gte', 80),
        ],
    },
    {
        'id': 'C', 'label': "Satisfaction des Apprenants", 'chart': 'bar',
        'kpis': [
            ('KPI F16', 'avg_satisfaction', "Note moyenne de satisfaction", '%', 'gte', 85),
            ('KPI F17', 'nps', "NPS (Net Promoter Score)", 'pts', 'gte', 30),
            ('KPI F18', 're_enrollment_rate', "Taux de réinscription (cours suivants)", '%', 'gte', 60),
            ('KPI F19', 'positive_comments_rate', "% Commentaires positifs", '%', 'gte', 80),
            ('KPI F20', 'avg_response_time_hours', "Temps moyen réponse aux questions", 'h', 'lte', 4),
            ('KPI F21', 'perceived_availability', "Disponibilité perçue", '%', 'gte', 80),
            ('KPI F22', 'answer_quality', "Qualité des réponses (éval. pairs)", '%', 'gte', 85),
            ('KPI F23', 'personalized_support', "Accompagnement personnalisé", '%', 'gte', 70),
            ('KPI F24', 'global_satisfaction', "Satisfaction globale (Q-sort)", '%', 'gte', 88),
            ('KPI F25', 'learner_loyalty', "Fidélisation des apprenants (retour)", '%', 'gte', 50),
        ],
    },
    {
        'id': 'D', 'label': "Performance & Production de Contenu", 'chart': 'bar',
        'kpis': [
            ('KPI F26', 'learner_success_rate', "Taux de réussite des apprenants", '%', 'gte', 78),
            ('KPI F27', 'learner_progress_pts', "Progression moyenne des apprenants", 'pts', 'gte', 10),
            ('KPI F28', 'completion_rate', "Taux de complétion des formations", '%', 'gte', 80),
            ('KPI F29', 'dropout_rate', "Taux d'abandon", '%', 'lte', 15),
            ('KPI F30', 'eval_difficulty_balance', "Difficulté équilibrée des éval. (score moy.)", '%', 'range', (60, 80)),
            ('KPI F31', 'theory_practice_ratio', "Équilibre théorie / pratique", 'ratio', 'ratio', (40, 60)),
            ('KPI F32', 'learner_certifications', "Certifications obtenues par les apprenants", 'nb', 'gte', 2),
            ('KPI F33', 'pedagogical_goals_reached', "Atteinte des objectifs pédagogiques", '%', 'gte', 90),
            ('KPI F34', 'final_level_reached', "Niveau moyen acquis en fin de formation", '%', 'gte', 75),
            ('KPI F35', 'impact_90d', "Impact mesuré 90j après formation", '%', 'gte', 70),
            ('KPI F36', 'courses_published_year', "Formations publiées dans l'année", 'nb', 'gte', 4),
            ('KPI F37', 'modules_created', "Modules / chapitres créés", 'nb', 'gte', 20),
            ('KPI F38', 'quizzes_created', "Quiz et évaluations créés", 'nb', 'gte', 30),
            ('KPI F39', 'content_update_frequency', "Fréquence de mise à jour des contenus", 'mois', 'lte', 6),
            ('KPI F40', 'content_reuse_rate', "Taux de réutilisation des contenus", '%', 'gte', 40),
        ],
    },
    {
        'id': 'F', 'label': "Innovation & Professionnalisme", 'chart': 'bar',
        'kpis': [
            ('KPI F41', 'ai_usage', "Utilisation de l'IA dans la pédagogie", '%', 'gte', 50),
            ('KPI F42', 'gamification_usage', "Gamification intégrée", '%', 'gte', 60),
            ('KPI F43', 'case_studies_per_course', "Études de cas réels utilisées", 'nb/form.', 'gte', 2),
            ('KPI F44', 'simulations_per_course', "Simulations et exercices pratiques", 'nb/form.', 'gte', 3),
            ('KPI F45', 'pedagogical_innovation', "Innovation des méthodes pédagogiques", 'score', 'gte', 70),
            ('KPI F46', 'deadline_respect', "Respect des délais (livrables)", '%', 'gte', 100),
            ('KPI F47', 'schedule_respect', "Respect du calendrier de formation", '%', 'gte', 95),
            ('KPI F48', 'contractual_respect', "Respect des engagements contractuels", '%', 'gte', 100),
            ('KPI F49', 'hr_collaboration', "Collaboration RH et managers", '%', 'gte', 85),
            ('KPI F50', 'tpi_score', "TPI — Trainer Performance Index", 'pts', 'gte', 80),
        ],
    },
]

# Sous-ensemble des 50 KPI Formateurs directement perceptibles par un apprenant
# (les autres — formations publiées, quiz créés, usage IA, respect des délais
# contractuels… — sont objectifs et déjà calculés depuis les données réelles de
# cours/sessions ; on ne demande pas à un apprenant de "noter" un nombre de quiz créés).
RATABLE_TRAINER_KPIS = [
    ('content_quality', "Qualité des supports pédagogiques"),
    ('course_structuring', "Structuration du cours"),
    ('objectives_respect', "Le cours a respecté ses objectifs annoncés"),
    ('resource_diversity', "Diversité et pertinence des ressources"),
    ('clarity', "Clarté des explications"),
    ('subject_mastery', "Maîtrise du sujet"),
    ('communication_quality', "Qualité de la communication"),
    ('audience_engagement', "Capacité à capter l'attention"),
    ('time_management', "Gestion du temps (respect du planning)"),
    ('dynamism', "Dynamisme et énergie"),
    ('interactivity', "Interactivité avec les apprenants"),
    ('practical_demo_quality', "Qualité des démonstrations pratiques"),
    ('level_adaptation', "Adaptation à votre niveau"),
    ('avg_satisfaction', "Satisfaction générale"),
    ('perceived_availability', "Disponibilité perçue"),
    ('answer_quality', "Qualité des réponses apportées"),
    ('personalized_support', "Accompagnement personnalisé"),
    ('global_satisfaction', "Satisfaction globale"),
    ('eval_difficulty_balance', "Niveau de difficulté des évaluations approprié"),
    ('theory_practice_ratio', "Bon équilibre théorie / pratique"),
    ('pedagogical_innovation', "Méthodes pédagogiques innovantes"),
]

TPI_WEIGHTS = [
    ('avg_satisfaction', "Satisfaction des apprenants", 0.25),
    ('learner_success_rate', "Réussite des apprenants", 0.20),
    ('completion_rate', "Taux de complétion", 0.15),
    ('content_quality', "Qualité des contenus", 0.15),
    ('interactivity', "Engagement des apprenants", 0.10),
    ('pedagogical_innovation', "Innovation pédagogique", 0.10),
    ('deadline_respect', "Respect des délais", 0.05),
]

LPI_WEIGHTS = [
    ('engagement_score', "Engagement", 0.20),
    ('skill_score', "Compétence", 0.20),
    ('performance_score', "Performance", 0.20),
    ('attendance_score', "Assiduité", 0.15),
    ('results_score', "Résultats", 0.15),
    ('certification_score', "Certification", 0.10),
]

BUDGET_BREAKDOWN_SHARES = [
    ('Main d\'œuvre Formateurs', 0.35),
    ('Contenus externes', 0.22),
    ('Hébergement & Licences', 0.18),
    ('Certifications', 0.12),
    ('Classes Virtuelles', 0.08),
    ('Animation & Ateliers', 0.05),
]


def status_for(op, target, value):
    """Compute a traffic-light status ('green'|'orange'|'red'|None) for a KPI value vs its objective."""
    if value is None or op == 'none':
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if op == 'gte':
        target = float(target)
        if value >= target:
            return 'green'
        if value >= target * 0.8:
            return 'orange'
        return 'red'
    if op == 'lte':
        target = float(target)
        if value <= target:
            return 'green'
        if value <= target * 1.2:
            return 'orange'
        return 'red'
    if op == 'alert_lte':
        target = float(target)
        return 'red' if value < target else 'green'
    if op == 'alert_gte':
        target = float(target)
        if value > target:
            return 'red'
        if value > target * 0.7:
            return 'orange'
        return 'green'
    if op == 'gte_delta':
        # value already expressed as the delta (points gained)
        target = float(target)
        if value >= target:
            return 'green'
        if value >= target * 0.5:
            return 'orange'
        return 'red'
    if op == 'range':
        lo, hi = target
        return 'green' if lo <= value <= hi else 'orange'
    if op == 'ratio':
        # target is (theory, practice) reference split — informative only
        return None
    return None


def build_kpi_rows(categories, values):
    """Merge a catalog (EMPLOYEE_CATEGORIES or TRAINER_CATEGORIES) with a computed `values` dict,
    returning categories annotated with value/status for each KPI — ready for the frontend tables."""
    result = []
    for cat in categories:
        rows = []
        for code, key, label, unit, op, target in cat['kpis']:
            value = values.get(key)
            rows.append({
                'code': code, 'key': key, 'label': label, 'unit': unit,
                'objective': _format_objective(op, target, unit),
                'value': value,
                'status': status_for(op, target, value),
            })
        result.append({'id': cat['id'], 'label': cat['label'], 'chart': cat['chart'], 'kpis': rows})
    return result


def _format_objective(op, target, unit):
    if op == 'none' or target is None:
        return '—'
    if op == 'gte':
        return f'≥ {target}{"%" if unit == "%" else ""}'.replace('%%', '%') if unit == '%' else f'≥ {target}'
    if op == 'lte':
        return f'≤ {target}{"%" if unit == "%" else ""}'.replace('%%', '%') if unit == '%' else f'≤ {target}'
    if op == 'alert_lte':
        return f'Alerte < {target}'
    if op == 'alert_gte':
        return f'Alerte > {target}%'
    if op == 'gte_delta':
        return f'+{target} pts'
    if op == 'range':
        lo, hi = target
        return f'{lo}–{hi}%'
    if op == 'ratio':
        lo, hi = target
        return f'{lo}/{hi}'
    return '—'
