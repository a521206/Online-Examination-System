from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_stu_question_llm_explanation_and_more'),
        ('questions', '0009_exam_model_num_questions'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_type', models.CharField(choices=[('wrong_question', 'Wrong question'), ('wrong_solution', 'Wrong solution'), ('too_hard', 'Too hard'), ('not_relevant', 'Not relevant'), ('other', 'Other')], max_length=20)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.Question_DB')),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.stuexamattempt')),
            ],
        ),
        migrations.CreateModel(
            name='PaperFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.Exam_Model')),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.stuexamattempt')),
            ],
        ),
    ] 