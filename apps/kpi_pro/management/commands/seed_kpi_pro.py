"""Enrichit les données réelles qui alimentent les 150 KPI de KPI's RH Pro.

La plupart des 100 KPI Employés se calculent déjà depuis les données existantes
(inscriptions, scores, compétences, évaluations 360°...). Cette commande comble
les quelques trous identifiés par audit sur les données seed_enterprise : aucune
classe virtuelle/présence, aucun message de forum, aucun certificat délivré,
aucune recommandation IA — ce qui faisait ressortir des KPI à zéro pour la
catégorie Assiduité, IA & Analytique, etc. Idempotente : peut être relancée sans
dupliquer les données déjà créées.
"""
import random
import secrets
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.core.constants import Roles

THREAD_TITLES = [
    "Question sur le module 3", "Retour d'expérience sur l'exercice pratique",
    "Difficulté avec le quiz final", "Astuce pour progresser plus vite",
    "Partage de ressources complémentaires", "Retard sur le calendrier ?",
]
POST_SNIPPETS = [
    "Merci pour cette formation, très clair !",
    "Quelqu'un a compris l'exercice 2 ?",
    "J'ai eu le même souci, voici comment je l'ai résolu.",
    "Super contenu, merci au formateur.",
    "Est-ce que quelqu'un peut m'expliquer ce point ?",
    "Top, ça débloque bien des choses, merci pour le partage.",
]
VIRTUAL_CLASS_TITLES = [
    "Session live — Questions/Réponses", "Atelier pratique en direct",
    "Classe virtuelle — Approfondissement", "Webinaire de clôture de module",
    "Coaching collectif", "Revue de projet en groupe", "Masterclass thématique",
    "Session de rattrapage",
]
LEARNER_ROLES = {Roles.EMPLOYEE, Roles.MANAGER, Roles.STUDENT}


class Command(BaseCommand):
    help = "Alimente les données réelles (assiduité, forums, certificats, recommandations IA) derrière les KPI's RH Pro, pour chaque employé d'une entreprise."

    def add_arguments(self, parser):
        parser.add_argument('--company', type=int, default=None, help="ID de l'entreprise racine à traiter (défaut : toutes)")

    def handle(self, *args, **options):
        from apps.tenants.models import Company

        company_id = options.get('company')
        companies = Company.objects.filter(pk=company_id) if company_id else Company.objects.filter(parent__isnull=True)

        if not companies:
            self.stdout.write(self.style.WARNING('Aucune entreprise trouvée.'))
            return

        for company in companies:
            self.stdout.write(self.style.MIGRATE_HEADING(f'--- {company.name} ---'))
            with transaction.atomic():
                self.seed_company(company)

        self.stdout.write(self.style.SUCCESS('Terminé.'))

    def seed_company(self, company):
        from apps.accounts.models import User

        company_ids = company.get_descendant_ids()
        users = list(User.objects.filter(company_id__in=company_ids, role__in=LEARNER_ROLES))
        if not users:
            self.stdout.write('  (aucun employé, ignoré)')
            return

        self.seed_certificates(users)
        classes = self.seed_virtual_classes(company, users)
        self.seed_attendance(classes, users)
        self.seed_forum(company, users)
        self.seed_recommendations(users)

    # ── Certificats pour les formations déjà complétées ─────────────────────
    def seed_certificates(self, users):
        from apps.certificates.models import Certificate, CertificateTemplate
        from apps.certificates.services import sign_certificate
        from apps.courses.models import Enrollment

        template = CertificateTemplate.objects.filter(is_default=True).first() or CertificateTemplate.objects.first()
        completed = Enrollment.objects.filter(
            user__in=users, status=Enrollment.STATUS_COMPLETED, course__certificate_enabled=True
        ).select_related('course', 'user')

        created = 0
        for enrollment in completed:
            if Certificate.objects.filter(user=enrollment.user, course=enrollment.course).exists():
                continue
            number = f'LMSPRO-{secrets.token_hex(6).upper()}'
            code = secrets.token_urlsafe(16)
            cert = Certificate.objects.create(
                user=enrollment.user, course=enrollment.course, template=template,
                certificate_number=number, verification_code=code,
            )
            cert.digital_signature = sign_certificate(number, code)
            cert.save(update_fields=['digital_signature'])
            created += 1
        self.stdout.write(f'  Certificats créés : {created}')

    # ── Classes virtuelles réalistes (liées aux cours suivis quand possible) ─
    def seed_virtual_classes(self, company, users):
        from apps.courses.models import Chapter, Enrollment
        from apps.virtual_classes.models import VirtualClass

        existing = list(VirtualClass.objects.filter(company=company))
        if len(existing) >= 6:
            self.stdout.write(f'  Classes virtuelles existantes : {len(existing)} (conservées)')
            return existing

        course_ids = list(Enrollment.objects.filter(user__in=users).values_list('course_id', flat=True).distinct())
        chapters = list(Chapter.objects.filter(section__course_id__in=course_ids)[:20])
        now = timezone.now()

        created = []
        for _ in range(8 - len(existing)):
            days_ago = random.randint(3, 150)
            start = now - timedelta(days=days_ago, hours=random.randint(0, 20))
            end = start + timedelta(minutes=random.choice([60, 90, 120]))
            vc = VirtualClass.objects.create(
                chapter=random.choice(chapters) if chapters else None,
                company=company,
                title=random.choice(VIRTUAL_CLASS_TITLES),
                provider=random.choice(['zoom', 'teams', 'meet', 'jitsi']),
                scheduled_start=start,
                scheduled_end=end,
            )
            created.append(vc)
        self.stdout.write(f'  Classes virtuelles créées : {len(created)}')
        return existing + created

    # ── Présences (ponctualité et durée variables pour un KPI réaliste) ─────
    def seed_attendance(self, classes, users):
        from apps.virtual_classes.models import VirtualClassAttendance

        created = 0
        for vc in classes:
            duration_s = max(60, int((vc.scheduled_end - vc.scheduled_start).total_seconds()))
            sample_size = max(1, int(len(users) * random.uniform(0.5, 0.85)))
            for user in random.sample(users, k=min(sample_size, len(users))):
                if VirtualClassAttendance.objects.filter(virtual_class=vc, user=user).exists():
                    continue
                roll = random.random()
                if roll < 0.7:
                    delay_seconds = random.randint(-120, 240)  # à l'heure (tolérance 5 min)
                elif roll < 0.9:
                    delay_seconds = random.randint(300, 900)  # léger retard
                else:
                    delay_seconds = random.randint(900, 1800)  # retard important
                joined_at = vc.scheduled_start + timedelta(seconds=delay_seconds)
                duration = int(duration_s * random.uniform(0.55, 1.0))
                VirtualClassAttendance.objects.create(
                    virtual_class=vc, user=user, joined_at=joined_at,
                    left_at=joined_at + timedelta(seconds=duration), duration_seconds=duration,
                )
                created += 1
        self.stdout.write(f'  Présences créées : {created}')

    # ── Participation aux forums ─────────────────────────────────────────────
    def seed_forum(self, company, users):
        from apps.social.models import ForumPost, ForumThread

        threads = list(ForumThread.objects.filter(company=company))
        if len(threads) < len(THREAD_TITLES):
            for title in THREAD_TITLES:
                thread, _ = ForumThread.objects.get_or_create(
                    company=company, title=title, defaults={'author': random.choice(users)}
                )
                if thread not in threads:
                    threads.append(thread)

        participants = random.sample(users, k=max(1, int(len(users) * 0.4)))
        created = 0
        for user in participants:
            thread = random.choice(threads)
            if ForumPost.objects.filter(thread=thread, author=user).exists():
                continue
            ForumPost.objects.create(thread=thread, author=user, content=random.choice(POST_SNIPPETS))
            created += 1
        self.stdout.write(f'  Messages de forum créés : {created}')

    # ── Recommandations IA de formation ──────────────────────────────────────
    def seed_recommendations(self, users):
        from apps.ai_engine.models import CourseRecommendation
        from apps.courses.models import Course, Enrollment

        published = list(Course.objects.filter(status=Course.STATUS_PUBLISHED))
        if not published:
            return

        created = 0
        for user in users:
            enrolled_ids = set(Enrollment.objects.filter(user=user).values_list('course_id', flat=True))
            candidates = [c for c in published if c.id not in enrolled_ids]
            if not candidates:
                continue
            for course in random.sample(candidates, k=min(2, len(candidates))):
                _, was_created = CourseRecommendation.objects.get_or_create(
                    user=user, course=course,
                    defaults={
                        'score': round(random.uniform(60, 98), 2),
                        'reason': 'Basé sur vos compétences et votre progression récente',
                    },
                )
                if was_created:
                    created += 1
        self.stdout.write(f'  Recommandations IA créées : {created}')
