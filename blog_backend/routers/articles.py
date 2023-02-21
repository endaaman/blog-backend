from fastapi import APIRouter, Depends, HTTPException

from ..services import get_articles


router = APIRouter(
    prefix='/articles',
    tags=['articles'],
)

@router.get('/')
async def get_all():
    print('aaa')
    return await get_articles()
