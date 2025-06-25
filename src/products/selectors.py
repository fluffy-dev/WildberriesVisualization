import django_filters
from django.db.models.query import QuerySet

from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="discounted_price", lookup_expr='gte')
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr='gte')
    min_reviews_count = django_filters.NumberFilter(field_name="reviews_count", lookup_expr='gte')

    class Meta:
        model = Product
        fields = ['min_price', 'min_rating', 'min_reviews_count']


def product_list(*, filters=None) -> QuerySet[Product]:
    """
    Returns a filtered and sorted list of products.

    Args:
        filters: A dictionary of filters to apply.

    Returns:
        A QuerySet of Product instances.
    """
    filters = filters or {}
    qs = Product.objects.all()
    return ProductFilter(filters, qs).qs