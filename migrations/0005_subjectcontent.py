# Generated by Django 5.0.7 on 2024-10-15 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learn", "0004_alter_subject_options_rename_name_subject_subject_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubjectContent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("grade", models.IntegerField()),
                ("subject", models.CharField(max_length=100)),
                ("content", models.TextField()),
            ],
        ),
    ]
