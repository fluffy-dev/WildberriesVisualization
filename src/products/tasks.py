from celery import shared_task

from .services import sync_products_from_wildberries


@shared_task
def run_wildberries_parser(category_url: str):
    """
    Celery task to run the Wildberries parser service.

    Args:
        category_url: The URL of the category to parse.
    """
    sync_products_from_wildberries(category_url=category_url)