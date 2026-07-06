import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.core.models import Department, Subject, AcademicSession
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.feedback.models import FeedbackQuestion, TeacherAssignment

STANDARD_QUESTIONS = [
    "Teaching Quality",
    "Subject Knowledge",
    "Communication",
    "Behaviour",
    "Classroom Interaction",
    "Practical Knowledge",
    "Doubt Solving",
    "Discipline",
    "Punctuality",
    "Overall Satisfaction",
]


class Command(BaseCommand):
    help = (
        "Seeds demo data (department, subject, session, questions, one "
        "teacher, one student, one assignment) so the feedback flow can "
        "be tested end-to-end without manually clicking through Django admin. "
        "Safe to run multiple times -- it won't create duplicates."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Reset demo user passwords even if the users already exist.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data..."))

        # --- Department & Subject ---------------------------------------
        department, _ = Department.objects.get_or_create(
            code="CSE", defaults={"name": "Computer Science Engineering"}
        )
        subject, _ = Subject.objects.get_or_create(
            code="CS301",
            defaults={"name": "Django Web Development", "department": department, "semester": 5},
        )

        # --- Academic Session (open for feedback) ------------------------
        session, _ = AcademicSession.objects.get_or_create(
            name="2025-26 Odd Semester",
            defaults={
                "start_date": datetime.date(2025, 7, 1),
                "end_date": datetime.date(2025, 12, 31),
                "is_active": True,
                "feedback_open": True,
            },
        )
        if not session.is_active or not session.feedback_open:
            session.is_active = True
            session.feedback_open = True
            session.save()

        # --- Feedback Questions ------------------------------------------
        for i, text in enumerate(STANDARD_QUESTIONS, start=1):
            FeedbackQuestion.objects.get_or_create(text=text, defaults={"order": i, "is_active": True})

        # --- Demo Teacher --------------------------------------------------
        teacher_user, created = User.objects.get_or_create(
            username="teacher1",
            defaults={"email": "teacher1@example.com", "role": User.Role.TEACHER},
        )
        if created or options["reset_passwords"]:
            teacher_user.set_password("teacher@123")
            teacher_user.role = User.Role.TEACHER
            teacher_user.save()

        teacher, _ = Teacher.objects.get_or_create(
            user=teacher_user,
            defaults={
                "employee_id": "EMP001",
                "full_name": "Dr. Ramesh Sharma",
                "department": department,
                "designation": "Assistant Professor",
            },
        )
        teacher.subjects.add(subject)

        # --- Demo Student ---------------------------------------------------
        student_user, created = User.objects.get_or_create(
            username="student1",
            defaults={"email": "student1@example.com", "role": User.Role.STUDENT},
        )
        if created or options["reset_passwords"]:
            student_user.set_password("student@123")
            student_user.role = User.Role.STUDENT
            student_user.save()

        student, _ = Student.objects.get_or_create(
            user=student_user,
            defaults={
                "roll_number": "CSE2025001",
                "full_name": "Aryan Yadav",
                "department": department,
                "semester": 5,
            },
        )

        # --- Assignment: this student can now give feedback for this teacher ---
        TeacherAssignment.objects.get_or_create(
            teacher=teacher, subject=subject, student=student, session=session
        )

        self.stdout.write(self.style.SUCCESS("\nDemo data ready!\n"))
        self.stdout.write("Login credentials:")
        self.stdout.write(f"  Teacher -> username: teacher1 / password: teacher@123")
        self.stdout.write(f"  Student -> username: student1 / password: student@123")
        self.stdout.write(
            "\n(Your existing superuser account still works for the Admin dashboard.)"
        )
        self.stdout.write(
            f"\nStudent '{student.full_name}' is now assigned to teacher "
            f"'{teacher.full_name}' for subject '{subject.name}' in session "
            f"'{session.name}' -- ready to submit feedback at /student/teachers/"
        )
