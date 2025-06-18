import io, requests
from ..core.config import settings

def add_file(data: bytes, name: str) -> str:
    files = {'file': (name, io.BytesIO(data))}
    r = requests.post(f"{settings.IPFS_API_URL}/api/v0/add", files=files, timeout=120)
    r.raise_for_status()
    return r.json()['Hash']
