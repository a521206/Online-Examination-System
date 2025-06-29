# Generated by Django 5.2.3 on 2025-06-22 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_question_db_questions_q_profess_c6182a_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question_db',
            name='question_type',
            field=models.CharField(choices=[('MCQ', 'Multiple Choice'), ('SHORT', 'Short Answer')], default='MCQ', help_text='Type of question: MCQ or Short Answer', max_length=10),
        ),
        migrations.AddField(
            model_name='question_db',
            name='short_answer_expected',
            field=models.TextField(blank=True, help_text='Model answer for short answer questions (optional)', null=True),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='answer',
            field=models.CharField(blank=True, help_text='For MCQ: correct option; For short: expected answer (optional)', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionA',
            field=models.TextField(blank=True, help_text='Option A (supports HTML/markdown formatting)', null=True),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionB',
            field=models.TextField(blank=True, help_text='Option B (supports HTML/markdown formatting)', null=True),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionC',
            field=models.TextField(blank=True, help_text='Option C (supports HTML/markdown formatting)', null=True),
        ),
        migrations.AlterField(
            model_name='question_db',
            name='optionD',
            field=models.TextField(blank=True, help_text='Option D (supports HTML/markdown formatting)', null=True),
        ),
    ]
