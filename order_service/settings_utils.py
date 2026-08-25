def normalize_base_url(value: str) -> str:
    value = value.strip()
    if not value.startswith(('http://', 'https://')):
        value = f'http://{value}'
    return value.rstrip('/')
