from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("restaurants", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="restaurant",
            old_name="fssai_license_number",
            new_name="fssai_number",
        ),
    ]
