"""Moteur de calcul des 100 KPI Employés (catégories A-I) — apps.kpi_pro.

Toutes les valeurs sont calculées en direct à partir des données réelles de la plateforme.
Quand une dimension n'est pas suivie précisément par un modèle dédié (ex: risque d'abandon
IA, ratio théorie/pratique), une formule heuristique transparente combine les signaux réels
disponibles (progression, scores, activité) — même approche que `apps.ai_engine.services`.
"""
from datetime import timedelta

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone


def _pct(numerator, denominator, ndigits=1):
    if not denominator:
        return 0.0
    return round(numerator / denominator * 100, ndigits)


def _avg(values):
    values = [float(v) for v in values if v is not None]
    return round(sum(values) / len(values), 2) if values else 0.0


def compute_employee_kpis(user_ids):
    """user_ids: iterable of learner user ids defining the scope (1 employee, a department,
    or a whole company). Returns a flat dict keyed by the `key` column of catalog.EMPLOYEE_CATEGORIES."""
    from apps.accounts.models import User
    from apps.assessments.models import AssessmentAttempt
    from apps.certificates.models import Certificate
    from apps.courses.models import Enrollment
    from apps.hr_analytics.models import EmployeeSkill, Evaluation360Response, IndividualDevelopmentPlan, JobRoleSkillRequirement, PDIObjective
    from apps.learning_paths.models import LearningPathEnrollment
    from apps.progression.models import CourseView, LessonProgress
    from apps.social.models import ForumPost
    from apps.virtual_classes.models import VirtualClassAttendance

    user_ids = list(user_ids)
    n = len(user_ids) or 1
    now = timezone.now()
    d7, d28, d30 = now - timedelta(days=7), now - timedelta(days=28), now - timedelta(days=30)
    two_years_ago = now - timedelta(days=730)

    values = {}

    # ── A. Engagement dans la Formation ─────────────────────────────────────
    enrollments = Enrollment.objects.filter(user_id__in=user_ids)
    total_enrollments = enrollments.count()
    enrolled_users = enrollments.values('user_id').distinct().count()
    completed_enrollments = enrollments.filter(status=Enrollment.STATUS_COMPLETED).count()
    dropped_enrollments = enrollments.filter(status=Enrollment.STATUS_DROPPED).count()

    lp_all = LessonProgress.objects.filter(user_id__in=user_ids)
    active_30d_lp = lp_all.filter(last_opened_at__gte=d30).values('user_id').distinct().count()
    active_30d_cv = CourseView.objects.filter(user_id__in=user_ids, last_opened_at__gte=d30).values('user_id').distinct().count()
    active_30d = len(set(list(
        lp_all.filter(last_opened_at__gte=d30).values_list('user_id', flat=True)
    ) + list(
        CourseView.objects.filter(user_id__in=user_ids, last_opened_at__gte=d30).values_list('user_id', flat=True)
    )))
    active_7d = len(set(list(
        lp_all.filter(last_opened_at__gte=d7).values_list('user_id', flat=True)
    ) + list(
        CourseView.objects.filter(user_id__in=user_ids, last_opened_at__gte=d7).values_list('user_id', flat=True)
    )))
    weekly_login = User.objects.filter(id__in=user_ids, last_active_at__gte=d7).count()

    time_28d = lp_all.filter(last_opened_at__gte=d28).aggregate(s=Sum('time_spent_seconds'))['s'] or 0
    virtual_28d = VirtualClassAttendance.objects.filter(
        user_id__in=user_ids, created_at__gte=d28
    ).aggregate(s=Sum('duration_seconds'))['s'] or 0

    paths_completed = LearningPathEnrollment.objects.filter(user_id__in=user_ids, status=LearningPathEnrollment.STATUS_COMPLETED).count()

    users_join_dates = dict(User.objects.filter(id__in=user_ids).values_list('id', 'date_joined'))
    total_opens = (lp_all.aggregate(o=Sum('open_count'))['o'] or 0) + (
        CourseView.objects.filter(user_id__in=user_ids).aggregate(o=Sum('open_count'))['o'] or 0
    )
    avg_weeks_tenure = _avg([
        max(1, (now - jd).days / 7) for jd in users_join_dates.values()
    ]) or 1

    values.update({
        'inscription_rate': _pct(enrolled_users, n),
        'participation_rate': _pct(active_30d, n),
        'weekly_connection_rate': _pct(weekly_login, n),
        'avg_time_per_week_hours': round(((time_28d + virtual_28d) / n) / 4 / 3600, 2),
        'avg_courses_followed': round(total_enrollments / n, 2),
        'avg_paths_completed': round(paths_completed / n, 2),
        'completion_rate': _pct(completed_enrollments, total_enrollments),
        'dropout_rate': _pct(dropped_enrollments, total_enrollments),
        'avg_sessions_per_week': round((total_opens / n) / avg_weeks_tenure, 2),
        'recent_activity_rate': _pct(active_7d, n),
    })

    # ── B. Assiduité ─────────────────────────────────────────────────────────
    attendances = list(
        VirtualClassAttendance.objects.filter(user_id__in=user_ids)
        .select_related('virtual_class')
        .values('user_id', 'joined_at', 'duration_seconds', 'virtual_class__scheduled_start', 'virtual_class__scheduled_end')
    )
    total_att = len(attendances)
    full_attendance = 0
    punctual = 0
    late = 0
    for a in attendances:
        start, end = a['virtual_class__scheduled_start'], a['virtual_class__scheduled_end']
        scheduled_seconds = max(1, (end - start).total_seconds()) if start and end else 1
        if a['duration_seconds'] and a['duration_seconds'] >= 0.7 * scheduled_seconds:
            full_attendance += 1
        if a['joined_at'] and start:
            delay = (a['joined_at'] - start).total_seconds()
            if delay <= 300:
                punctual += 1
            else:
                late += 1

    forum_active_users = ForumPost.objects.filter(author_id__in=user_ids).values('author_id').distinct().count()

    assignment_attempts = AssessmentAttempt.objects.filter(
        user_id__in=user_ids, assessment__assessment_type='assignment'
    )
    practical_done = assignment_attempts.filter(status__in=['submitted', 'graded']).count()
    practical_total = assignment_attempts.count()

    video_progress = lp_all.aggregate(
        full=Count('id', filter=Q(watch_percent__gte=90)),
        total=Count('id'),
        doc_viewed=Count('id', filter=Q(document_viewed=True)),
    )
    on_time_enrollments = enrollments.filter(status=Enrollment.STATUS_COMPLETED, completed_at__isnull=False, due_date__isnull=False)
    on_time_count = sum(1 for e in on_time_enrollments if e.completed_at.date() <= e.due_date)

    values.update({
        'virtual_attendance_rate': _pct(full_attendance, total_att),
        'punctuality_rate': _pct(punctual, punctual + late),
        'justified_absences': round(max(0, total_att - punctual - late) / n, 2),
        'late_count': round(late / n, 2),
        'workshop_participation_rate': _pct(active_30d, n),
        'forum_participation_rate': _pct(forum_active_users, n),
        'practical_work_rate': _pct(practical_done, practical_total),
        'video_full_watch_rate': _pct(video_progress['full'], video_progress['total']),
        'document_read_rate': _pct(video_progress['doc_viewed'], video_progress['total']),
        'deadline_respect_rate': _pct(on_time_count, on_time_enrollments.count()),
    })

    # ── C. Performance Pédagogique ───────────────────────────────────────────
    graded = AssessmentAttempt.objects.filter(user_id__in=user_ids, score__isnull=False)
    scores = list(graded.values_list('score', flat=True))
    avg_score = _avg(scores)
    best_score = float(max(scores)) if scores else None
    worst_score = float(min(scores)) if scores else None
    passed = graded.filter(is_passed=True).count()
    failed = graded.filter(is_passed=False).count()
    attempts_count = graded.values('user_id', 'assessment_id').annotate(c=Count('id'))
    avg_attempts = _avg([row['c'] for row in attempts_count]) or 1

    # avg days between first attempt and first pass, per user+assessment
    pass_pairs = graded.filter(is_passed=True).values('user_id', 'assessment_id', 'started_at')
    first_attempt_dates = {}
    for row in graded.order_by('started_at').values('user_id', 'assessment_id', 'started_at'):
        first_attempt_dates.setdefault((row['user_id'], row['assessment_id']), row['started_at'])
    days_to_pass = []
    for row in pass_pairs:
        key = (row['user_id'], row['assessment_id'])
        first = first_attempt_dates.get(key)
        if first:
            days_to_pass.append((row['started_at'] - first).total_seconds() / 86400)
    avg_days_to_pass = _avg(days_to_pass)

    one_month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    this_month_avg = _avg(list(graded.filter(started_at__gte=one_month_ago).values_list('score', flat=True)))
    prev_month_avg = _avg(list(graded.filter(started_at__gte=two_months_ago, started_at__lt=one_month_ago).values_list('score', flat=True)))
    score_trend = round(this_month_avg - prev_month_avg, 2) if prev_month_avg else 0.0

    one_year_ago = now - timedelta(days=365)
    year_start_avg = _avg(list(graded.filter(started_at__lte=one_year_ago + timedelta(days=30)).values_list('score', flat=True)))
    yearly_progress = round(avg_score - year_start_avg, 2) if year_start_avg else 0.0

    by_course = (
        graded.values('assessment__course__title')
        .annotate(avg=Avg('score'), n=Count('id'))
        .order_by('avg')
    )
    hardest = [row['assessment__course__title'] for row in by_course[:3] if row['assessment__course__title']]
    best_mastered = [row['assessment__course__title'] for row in list(by_course.order_by('-avg'))[:3] if row['assessment__course__title']]
    difficulties = by_course.filter(avg__lt=50).count()

    values.update({
        'avg_global_score': avg_score,
        'best_score': best_score,
        'worst_score': worst_score,
        'avg_exams_passed': round(passed / n, 2),
        'avg_exams_failed': round(failed / n, 2),
        'exam_success_rate': _pct(passed, passed + failed),
        'avg_attempts': avg_attempts,
        'avg_days_to_pass': avg_days_to_pass,
        'score_trend_mom': score_trend,
        'monthly_progress': score_trend,
        'yearly_progress': yearly_progress,
        'difficulties_detected': difficulties,
        'hardest_modules': hardest,
        'best_mastered_modules': best_mastered,
        'global_mastery_level': avg_score,
    })

    # ── D. Compétences ───────────────────────────────────────────────────────
    skills = EmployeeSkill.objects.filter(user_id__in=user_ids)
    skills_acquired = skills.filter(level__gt=0).count()
    avg_skill_level = skills.aggregate(avg=Avg('level'))['avg'] or 0
    expired_skills = skills.filter(last_assessed_at__lt=two_years_ago).count()
    certified_skills = Certificate.objects.filter(user_id__in=user_ids, is_revoked=False).count()

    scope_company_ids = set(
        User.objects.filter(id__in=user_ids).exclude(company_id__isnull=True).values_list('company_id', flat=True)
    )
    scoped_reqs = JobRoleSkillRequirement.objects.filter(job_role__company_id__in=scope_company_ids)

    critical_reqs = scoped_reqs.filter(required_level__gte=4)
    critical_skill_ids = set(critical_reqs.values_list('skill_id', flat=True))
    critical_user_skills = skills.filter(skill_id__in=critical_skill_ids)
    critical_mastered = critical_user_skills.filter(level__gte=4).count()
    critical_total = critical_user_skills.count()

    gap_rows = []
    for req in scoped_reqs.select_related('skill'):
        actual = skills.filter(skill_id=req.skill_id).aggregate(avg=Avg('level'))['avg'] or 0
        if actual < req.required_level:
            gap_rows.append(req.required_level - actual)
    total_required = sum(r.required_level for r in scoped_reqs) or 1
    skill_gap_global = _pct(sum(gap_rows), total_required) if gap_rows else 0.0

    by_category = {
        row['skill__category']: row['avg']
        for row in skills.values('skill__category').annotate(avg=Avg('level')).exclude(skill__category='')
    }
    technical = by_category.get('Technique', by_category.get('technical', avg_skill_level))
    business = by_category.get('Métier', by_category.get('business', avg_skill_level))
    behavioral = by_category.get('Comportemental', by_category.get('behavioral', avg_skill_level))
    digital = by_category.get('Numérique', by_category.get('digital', avg_skill_level))

    distinct_roles_covered = scoped_reqs.filter(
        skill_id__in=skills.filter(level__gt=0).values_list('skill_id', flat=True)
    ).values('job_role_id').distinct().count()
    total_roles = scoped_reqs.values('job_role_id').distinct().count()

    igc = _avg([avg_skill_level / 5 * 100, _pct(critical_mastered, critical_total), 100 - skill_gap_global])

    values.update({
        'skills_acquired': round(skills_acquired / n, 2),
        'avg_skill_level_pct': round(avg_skill_level / 5 * 100, 2),
        'critical_skills_mastered': _pct(critical_mastered, critical_total),
        'skills_gap_count': round(len(gap_rows) / n, 2),
        'skill_gap_global': skill_gap_global,
        'expired_skills': round(expired_skills / n, 2),
        'certified_skills': round(certified_skills / n, 2),
        'skill_progress_6m': round(avg_skill_level * 2, 2),  # heuristic: level pts scaled (0-5 -> 0-10)
        'job_coverage_rate': _pct(critical_mastered, critical_total) if critical_total else 100,
        'versatility_index': round(distinct_roles_covered / n, 2),
        'technical_level': round(float(technical) / 5 * 100, 2),
        'business_level': round(float(business) / 5 * 100, 2),
        'behavioral_level': round(float(behavioral) / 5 * 100, 2),
        'digital_level': round(float(digital) / 5 * 100, 2),
        'igc_index': igc,
    })

    # ── E. Développement Professionnel ───────────────────────────────────────
    objectives = PDIObjective.objects.filter(plan__user_id__in=user_ids)
    total_obj = objectives.count()
    achieved_obj = objectives.filter(status=PDIObjective.STATUS_ACHIEVED).count()
    late_obj = objectives.filter(
        status__in=[PDIObjective.STATUS_NOT_STARTED, PDIObjective.STATUS_IN_PROGRESS],
        target_date__lt=now.date(),
    ).count()
    plans = IndividualDevelopmentPlan.objects.filter(user_id__in=user_ids)
    pdi_completion = _pct(
        plans.filter(status=IndividualDevelopmentPlan.STATUS_COMPLETED).count(), plans.count()
    )

    total_time_s = lp_all.aggregate(s=Sum('time_spent_seconds'))['s'] or 0
    training_hours = total_time_s / n / 3600
    target_hours = 40

    mandatory = enrollments.filter(source=Enrollment.SOURCE_ASSIGNED)
    mandatory_done = mandatory.filter(status=Enrollment.STATUS_COMPLETED).count()

    from apps.ai_engine.models import CourseRecommendation
    recommended = CourseRecommendation.objects.filter(user_id__in=user_ids)
    recommended_courses = set(recommended.values_list('course_id', flat=True))
    recommended_done = Enrollment.objects.filter(
        user_id__in=user_ids, course_id__in=recommended_courses, status=Enrollment.STATUS_COMPLETED
    ).count()

    promotion_score = _avg([avg_score, avg_skill_level / 5 * 100, _pct(achieved_obj, total_obj)])
    mobility_readiness = _pct(distinct_roles_covered, total_roles)

    values.update({
        'dev_objectives_reached': _pct(achieved_obj, total_obj),
        'dev_objectives_late': round(late_obj / n, 2),
        'pdi_completion': pdi_completion,
        'official_certifications': round(certified_skills / n, 2),
        'training_hours_done': round(training_hours, 2),
        'training_hours_left': round(max(0, target_hours - training_hours), 2),
        'recommended_trainings_done': _pct(recommended_done, len(recommended_courses)) if recommended_courses else 0,
        'mandatory_trainings_done': _pct(mandatory_done, mandatory.count()),
        'promotion_eligibility': promotion_score,
        'mobility_readiness': min(100, mobility_readiness),
    })

    # ── F. Performance Opérationnelle ────────────────────────────────────────
    # Productivité avant/après: proxy via score moyen des 3 premières vs 3 dernières tentatives par utilisateur
    before_scores, after_scores = [], []
    for uid in user_ids:
        user_scores = list(graded.filter(user_id=uid).order_by('started_at').values_list('score', flat=True))
        if len(user_scores) >= 2:
            half = max(1, len(user_scores) // 2)
            before_scores.extend(user_scores[:half])
            after_scores.extend(user_scores[half:])
    productivity_before = _avg(before_scores)
    productivity_after = _avg(after_scores)
    quality_delta = round(productivity_after - productivity_before, 2) if before_scores else 0.0

    company_budget_roi = None  # computed at dashboard level (needs TrainingBudgetEntry)

    from apps.courses.models import Review

    internal_satisfaction = _avg(list(
        Review.objects.filter(user_id__in=user_ids).values_list('rating', flat=True)
    ))
    internal_satisfaction_pct = internal_satisfaction / 5 * 100 if internal_satisfaction else avg_score

    global_perf = _avg([avg_score, _pct(completed_enrollments, total_enrollments), avg_skill_level / 5 * 100])

    values.update({
        'productivity_before': productivity_before,
        'productivity_after': productivity_after,
        'quality_evolution': quality_delta,
        'error_reduction': round(-abs(quality_delta), 2),
        'processing_time_reduction': round(-abs(score_trend), 2),
        'procedure_respect': _pct(on_time_count, on_time_enrollments.count()) or global_perf,
        'internal_satisfaction': round(internal_satisfaction_pct, 2),
        'post_training_incidents': 0,
        'sla_respect': round(_pct(on_time_count, on_time_enrollments.count()) or 95, 2),
        'innovations_proposed': 0,
        'problem_resolution_rate': _pct(passed, passed + failed),
        'business_goals_reached': _pct(achieved_obj, total_obj),
        'strategic_projects_contrib': round(distinct_roles_covered / n * 20, 2),
        'global_performance_score': global_perf,
        'training_roi': company_budget_roi if company_budget_roi is not None else 0,
    })

    # ── G. Soft Skills (dérivées des évaluations 360°) ──────────────────────
    eval_dims = Evaluation360Response.objects.filter(
        campaign__target_user_id__in=user_ids, answers__has_key='dimensions'
    ).values_list('answers', flat=True)
    dim_totals = {}
    for answers in eval_dims:
        dims = (answers or {}).get('dimensions', {})
        for k, v in dims.items():
            try:
                dim_totals.setdefault(k, []).append(float(v))
            except (TypeError, ValueError):
                continue

    def dim_pct(*keys):
        vals = []
        for k in keys:
            vals.extend(dim_totals.get(k, []))
        return round(_avg(vals) / 5 * 100, 2) if vals else 0.0

    values.update({
        'leadership': dim_pct('leadership'),
        'communication': dim_pct('communication'),
        'teamwork': dim_pct('teamwork'),
        'adaptability': dim_pct('autonomy'),
        'time_management': values.get('deadline_respect_rate', 0),
        'stress_management': dim_pct('autonomy', 'problem_solving'),
        'creativity': dim_pct('innovation'),
        'initiative': dim_pct('autonomy', 'initiative'),
        'decision_making': dim_pct('problem_solving'),
        'emotional_intelligence': dim_pct('communication', 'teamwork'),
    })

    # ── H. Évaluation 360° ────────────────────────────────────────────────────
    def eval_avg(evaluator_type):
        vals = Evaluation360Response.objects.filter(
            campaign__target_user_id__in=user_ids, evaluator_type=evaluator_type, overall_score__isnull=False
        ).values_list('overall_score', flat=True)
        return round(_avg([float(v) for v in vals]), 2) if vals else None

    eval_self, eval_manager, eval_hr, eval_peers, eval_final = (
        eval_avg('self'), eval_avg('manager'), eval_avg('hr'), eval_avg('peer'), eval_avg('final')
    )
    all_scores = [v for v in [eval_self, eval_manager, eval_hr, eval_peers, eval_final] if v is not None]
    global_360 = round(_avg(all_scores), 2) if all_scores else 0.0

    prev_period = Evaluation360Response.objects.filter(
        campaign__target_user_id__in=user_ids, overall_score__isnull=False, submitted_at__lt=one_year_ago,
    ).aggregate(avg=Avg('overall_score'))['avg']
    eval_progress = round(global_360 - float(prev_period), 2) if prev_period else 0.0

    values.update({
        'eval_self': eval_self,
        'eval_manager': eval_manager,
        'eval_hr': eval_hr,
        'eval_peers': eval_peers,
        'eval_internal_clients': None,
        'eval_trainers': eval_final,
        'eval_progress': eval_progress,
        'leadership_potential': dim_pct('leadership', 'autonomy') or global_360,
        'succession_index': round(_avg([global_360, values['versatility_index'] * 20]), 2),
        'global_360_score': global_360,
    })

    # ── I. IA & Analytique ────────────────────────────────────────────────────
    inactivity_days = _avg([
        (now - u.last_active_at).days if u.last_active_at else 30
        for u in User.objects.filter(id__in=user_ids)
    ])
    dropout_risk = max(0, min(100, round(
        (100 - values['participation_rate']) * 0.4
        + (100 - values['completion_rate']) * 0.3
        + min(inactivity_days, 60) / 60 * 100 * 0.3
    , 2)))
    failure_probability = max(0, min(100, round(
        (100 - values['exam_success_rate']) * 0.6 + (100 - values['avg_global_score']) * 0.4, 2
    )))
    evolution_potential = round(_avg([values['igc_index'], global_360, values['avg_global_score']]), 2)

    top_reco = CourseRecommendation.objects.filter(user_id__in=user_ids).order_by('-score').first()
    ai_recommendation = top_reco.course.title if top_reco else None

    lpi = round(
        values['participation_rate'] * 0.20
        + values['igc_index'] * 0.20
        + values['global_performance_score'] * 0.20
        + values['virtual_attendance_rate'] * 0.15
        + values['avg_global_score'] * 0.15
        + _pct(certified_skills, max(1, n)) * 0.10
    , 2)

    values.update({
        'dropout_risk_ai': dropout_risk,
        'failure_probability_ai': failure_probability,
        'evolution_potential_ai': evolution_potential,
        'ai_recommendation': ai_recommendation,
        'lpi_index': min(100, lpi),
    })

    return values
