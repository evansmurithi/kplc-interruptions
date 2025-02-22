# Generated by Django 2.2 on 2019-07-01 23:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('interruptions', '0003_interruptionpdftext'),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Notification',
            new_name='NotificationAccount',
        ),
        migrations.CreateModel(
            name='NotificationPDFQueue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier of an object', primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, help_text='Date and time an object was created')),
                ('updated', models.DateTimeField(db_index=True, default=django.utils.timezone.now, help_text='Date and time an object was updated')),
                ('is_processed', models.BooleanField(default=False)),
                ('processed_on', models.DateTimeField()),
                ('pdf_text', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='pdf_queue', to='interruptions.InterruptionPdfText')),
            ],
            options={
                'ordering': ('-updated', '-created'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier of an object', primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, help_text='Date and time an object was created')),
                ('updated', models.DateTimeField(db_index=True, default=django.utils.timezone.now, help_text='Date and time an object was updated')),
                ('status', models.CharField(choices=[('SUCCESS', 'Success'), ('FAILURE', 'Failure')], max_length=7)),
                ('message', models.TextField(blank=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='account_logs', to='notifications.NotificationAccount')),
            ],
            options={
                'ordering': ('-updated', '-created'),
                'abstract': False,
            },
        ),
    ]
