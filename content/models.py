from django.db import models


class ContentContainer(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ============================================
# UNIFIED FAQ BLOCKS
# ============================================


class FAQBlock(models.Model):
    container = models.ForeignKey(
        "content.ContentContainer",
        on_delete=models.CASCADE,
        related_name="faq_blocks",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional section title like 'Frequently Asked Questions'",
    )
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ Block"
        verbose_name_plural = "FAQ Blocks"

    def __str__(self):
        return self.title or f"FAQ Block #{self.pk}"


class FAQItem(models.Model):
    faq_block = models.ForeignKey(
        FAQBlock,
        on_delete=models.CASCADE,
        related_name="items",
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"

    def __str__(self):
        return self.question[:50]


class ThreeColumnBlock(models.Model):
    container = models.ForeignKey(
        "ContentContainer",
        on_delete=models.CASCADE,
        related_name="three_column_blocks",
    )

    order = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=True)

    col_1_title = models.CharField(max_length=255, blank=True)
    col_1_image = models.ImageField(upload_to="three_columns/", blank=True, null=True)
    col_1_body = models.TextField(blank=True)

    col_2_title = models.CharField(max_length=255, blank=True)
    col_2_image = models.ImageField(upload_to="three_columns/", blank=True, null=True)
    col_2_body = models.TextField(blank=True)

    col_3_title = models.CharField(max_length=255, blank=True)
    col_3_image = models.ImageField(upload_to="three_columns/", blank=True, null=True)
    col_3_body = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"ThreeColumnBlock #{self.pk}"
