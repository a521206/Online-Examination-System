# Generated by Django 5.2.3 on 2025-06-21 07:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_question_db_questions_q_profess_c6182a_idx_and_more'),
        ('student', '0003_stuexamattempt_end_time'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stuexamattempt',
            options={'ordering': ['-started_at']},
        ),
        migrations.AddIndex(
            model_name='stuexamattempt',
            index=models.Index(fields=['student', 'exam'], name='student_stu_student_eb1170_idx'),
        ),
        migrations.AddIndex(
            model_name='stuexamattempt',
            index=models.Index(fields=['started_at'], name='student_stu_started_3133ae_idx'),
        ),
        migrations.AddIndex(
            model_name='stuexamattempt',
            index=models.Index(fields=['completed_at'], name='student_stu_complet_69680f_idx'),
        ),
        migrations.AddIndex(
            model_name='stuexamattempt',
            index=models.Index(fields=['student', 'exam', 'started_at'], name='student_stu_student_3a1981_idx'),
        ),
    ]
