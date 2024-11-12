import os
import time
import threading
import hashlib
import httpx
from .const import CF_API_TOKEN


def asdicts(items):
    return [i.dict() for i in items]

def debounce(wait):
    def decorator(fn):
        timer = None
        def debounced(*args, **kwargs):
            nonlocal timer
            def call_it():
                fn(*args, **kwargs)
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(wait, call_it)
            timer.start()
        return debounced
    return decorator

def get_hash(t):
    return hashlib.sha256(str(t).encode('utf-8')).hexdigest()


async def purge_cf_cache():
    CF_API_TOKEN = os.getenv('CF_API_TOKEN')
    if not CF_API_TOKEN:
        return 'CF_API_TOKEN is unset.'

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.cloudflare.com/client/v4/zones/91c982d0d1a8eb1e3402e917693fbb53/purge_cache',
                headers={
                    'Authorization': f'Bearer {CF_API_TOKEN}',
                    'Content-Type': 'application/json'
                },
                json={'purge_everything': True},
                timeout=30.0
            )
            result = response.json()
            if not result.get('success'):
                return f'Cache purge failed: {result.get("errors")}'
            return
    except httpx.TimeoutException:
        return 'Request timeout'
    except httpx.RequestError as e:
        return f'Request failed: {str(e)}'
    except Exception as e:
        raise e

    return None
