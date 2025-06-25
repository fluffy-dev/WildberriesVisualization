from typing import Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Product
from .utils import fetch_products_from_url


def product_update_or_create(product_data: Dict[str, Any]) -> Product:
    """
    Creates or updates a product instance from raw data.

    Args:
        product_data: A dictionary containing product information.

    Returns:
        The created or updated Product instance.
    """
    wb_id = product_data.get('id')
    if not wb_id:
        raise ValidationError("Product data must contain an 'id'.")

    product, created = Product.objects.update_or_create(
        wb_id=wb_id,
        defaults={
            'name': product_data.get('name', ''),
            'price': int(product_data.get('priceU', 0) / 100),
            'discounted_price': int(product_data.get('salePriceU', 0) / 100),
            'rating': product_data.get('rating'),
            'reviews_count': product_data.get('feedbacks', 0),
            'brand': product_data.get('brand', 'Unknown'),
        }
    )
    product.full_clean()
    return product


@transaction.atomic
def sync_products_from_wildberries(category_url: str) -> int:
    """
    Fetches products from a Wildberries category and saves them to the database.

    Args:
        category_url: The URL of the category to parse.

    Returns:
        The number of products that were successfully synced.
    """
    products_raw_data = fetch_products_from_url(category_url)

    synced_products_count = 0
    for product_data in products_raw_data:
        try:
            product_update_or_create(product_data)
            synced_products_count += 1
        except ValidationError:
            continue

    return synced_products_count