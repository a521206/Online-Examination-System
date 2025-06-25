from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('questions', '0009_exam_model_num_questions'),
    ]
    operations = [
        migrations.AddField(
            model_name='question_db',
            name='question_image',
            field=models.ImageField(upload_to='question_images/', blank=True, null=True, help_text='Image for the question (optional)'),
        ),
        migrations.AddField(
            model_name='question_db',
            name='solution_image',
            field=models.ImageField(upload_to='solution_images/', blank=True, null=True, help_text='Image for the solution/answer (optional)'),
        ),
    ] 