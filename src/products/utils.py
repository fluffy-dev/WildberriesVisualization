import requests
from typing import List, Dict, Any


def get_catalogs_wb() -> List[Dict[str, Any]]:
    """Gets the full Wildberries catalog."""
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json'
    headers = {'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def _get_data_from_category(catalogs_wb: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Recursively traverses the catalog to extract category data."""
    catalog_data = []
    for item in catalogs_wb:
        catalog_data.append({
            'name': item.get('name'),
            'shard': item.get('shard'),
            'url': item.get('url'),
            'query': item.get('query')
        })
        if 'childs' in item:
            catalog_data.extend(_get_data_from_category(item['childs']))
    return catalog_data


def _search_category_in_catalog(url: str, catalog_list: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    """Finds a user-provided category URL in the full catalog."""
    path = url.split('https://www.wildberries.ru')[-1]
    for catalog in catalog_list:
        if catalog.get('url') == path:
            return catalog
    return None


def _parse_page(page: int, shard: str, query: str) -> Dict[str, Any]:
    """Fetches and parses a single page of products."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"}
    url = (f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub'
           f'&dest=-1257786&locale=ru&page={page}&sort=popular&spp=0&{query}')
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}


def fetch_products_from_url(category_url: str) -> List[Dict[str, Any]]:
    """
    Fetches all product data from a given Wildberries category URL.

    Args:
        category_url: The full URL to the product category.

    Returns:
        A list of dictionaries, where each dictionary represents a product.
    """
    full_catalog = get_catalogs_wb()
    if not full_catalog:
        return []

    all_categories = _get_data_from_category(full_catalog)
    target_category = _search_category_in_catalog(category_url, all_categories)

    if not target_category or not target_category.get('shard') or not target_category.get('query'):
        return []

    products_data = []
    for page in range(1, 51):  # WB gives up to 50 pages
        page_data = _parse_page(page=page, shard=target_category['shard'], query=target_category['query'])
        products = page_data.get('data', {}).get('products', [])
        if not products:
            break
        products_data.extend(products)

    return products_data