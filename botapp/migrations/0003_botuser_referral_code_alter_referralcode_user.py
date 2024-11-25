# Generated by Django 5.1.3 on 2024-11-24 20:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botapp', '0002_alter_referralcode_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='referral_code',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='botapp.referralcode'),
        ),
        migrations.AlterField(
            model_name='referralcode',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='referral_code_obj', to='botapp.botuser'),
        ),
    ]