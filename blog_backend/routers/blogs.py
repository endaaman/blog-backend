from fastapi import APIRouter, Depends, HTTPException

# from ..dependencies import get_blogs


router = APIRouter(
    prefix='/blogs',
    # dependencies=[Depends(get_blogs)],
    tags=['blogs'],
)


fake_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get('/')
async def get_all():
    return []
