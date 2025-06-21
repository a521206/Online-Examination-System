from django.apps import AppConfig


class FacultyConfig(AppConfig):
    name = 'faculty'

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        
        @receiver(post_migrate, sender=self)
        def create_groups(sender, **kwargs):
            from django.contrib.auth.models import Group
            for group_name in ['Student', 'Professor']:
                Group.objects.get_or_create(name=group_name)
