from django.db import models

from common.models import BaseModel


class Product(BaseModel):
    """Stores a single product entry."""

    wb_id = models.PositiveIntegerField(
        unique=True,
        db_index=True,
        verbose_name="Артикул Wildberries"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    price = models.PositiveIntegerField(verbose_name="Цена")
    discounted_price = models.PositiveIntegerField(verbose_name="Цена со скидкой")
    rating = models.FloatField(null=True, blank=True, verbose_name="Рейтинг")
    reviews_count = models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")
    brand = models.CharField(max_length=100, verbose_name="Бренд")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.wb_id}] {self.name}'