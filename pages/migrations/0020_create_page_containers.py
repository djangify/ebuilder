from django.db import migrations


def create_page_containers(apps, schema_editor):
    Page = apps.get_model("pages", "Page")
    ContentContainer = apps.get_model("content", "ContentContainer")

    for page in Page.objects.all():
        if page.content_container_id is None:
            container = ContentContainer.objects.create(
                name=f"Container for {page.title}"
            )
            page.content_container = container
            page.save(update_fields=["content_container"])


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0019_page_content_container"),
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_page_containers, migrations.RunPython.noop),
    ]
