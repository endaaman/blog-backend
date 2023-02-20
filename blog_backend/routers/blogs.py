from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_blogs


router = APIRouter(
    prefix='/blogs',
    dependencies=[Depends(get_watcher)],
    tags=['blogs'],
)


fake_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get('/')
async def get_all():
    blogs = await
    return fake_db


@router.get('/{item_id}')
async def get_item(item_id: str):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name": fake_db[item_id]["name"], "item_id": item_id}
