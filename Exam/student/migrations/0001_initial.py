# Generated by Django 5.2.3 on 2025-06-21 04:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('questions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stu_Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=100)),
                ('optionA', models.CharField(blank=True, default='', max_length=100)),
                ('optionB', models.CharField(blank=True, default='', max_length=100)),
                ('optionC', models.CharField(blank=True, default='', max_length=100)),
                ('optionD', models.CharField(blank=True, default='', max_length=100)),
                ('answer', models.CharField(blank=True, default='', max_length=200)),
                ('choice', models.CharField(blank=True, default='', max_length=10)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=200)),
                ('stream', models.CharField(blank=True, max_length=50)),
                ('picture', models.ImageField(blank=True, upload_to='student_profile_pics')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Student Info',
            },
        ),
        migrations.CreateModel(
            name='StuExamAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('score', models.IntegerField(default=0)),
                ('random_qids', models.CharField(blank=True, max_length=500, null=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.exam_model')),
                ('qpaper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.question_paper')),
                ('questions', models.ManyToManyField(to='student.stu_question')),
                ('student', models.ForeignKey(limit_choices_to={'groups__name': 'Student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StuResults_DB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempts', models.ManyToManyField(to='student.stuexamattempt')),
                ('student', models.ForeignKey(limit_choices_to={'groups__name': 'Student'}, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
