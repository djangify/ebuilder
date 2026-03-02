from django.db import migrations


def migrate_shop_promo_blocks(apps, schema_editor):
    ShopPromoBlock = apps.get_model("shop", "ShopPromoBlock")
    ContentThreeColumn = apps.get_model("content", "ThreeColumnBlock")

    for old_block in ShopPromoBlock.objects.all():
        shop_settings = old_block.shop_settings
        container = shop_settings.content_container

        ContentThreeColumn.objects.create(
            container=container,
            order=old_block.order,
            published=old_block.published,
            col_1_title=old_block.col_1_title,
            col_1_image=old_block.col_1_image,
            col_1_body=old_block.col_1_body,
            col_2_title=old_block.col_2_title,
            col_2_image=old_block.col_2_image,
            col_2_body=old_block.col_2_body,
            col_3_title=old_block.col_3_title,
            col_3_image=old_block.col_3_image,
            col_3_body=old_block.col_3_body,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0004_migrate_page_three_columns"),
        ("shop", "0019_remove_shopfaqitem_faq_block_delete_shopfaqblock_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_shop_promo_blocks, migrations.RunPython.noop),
    ]
