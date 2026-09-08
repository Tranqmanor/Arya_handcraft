"""用户地址簿(每人最多 6 条)。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.users import get_current_user_dep
from app.db.session import get_db
from app.models import Address, User
from app.schemas.order import AddressIn, AddressOut
from app.services.orders import MAX_ADDRESSES_PER_USER

router = APIRouter(prefix="/addresses", tags=["addresses"])


def _get_own_address(db: Session, user: User, address_id: int) -> Address:
    address = db.get(Address, address_id)
    if address is None or address.user_id != user.id:
        raise HTTPException(status_code=404, detail="地址不存在")
    return address


def _clear_default(db: Session, user: User, keep_id: int | None = None) -> None:
    stmt = select(Address).where(Address.user_id == user.id, Address.is_default.is_(True))
    for address in db.scalars(stmt).all():
        if keep_id is None or address.id != keep_id:
            address.is_default = False


@router.get("", response_model=list[AddressOut])
def list_addresses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    return list(
        db.scalars(
            select(Address).where(Address.user_id == user.id).order_by(Address.is_default.desc(), Address.id.desc())
        ).all()
    )


@router.post("", response_model=AddressOut)
def create_address(
    payload: AddressIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    count = db.scalar(select(func.count(Address.id)).where(Address.user_id == user.id)) or 0
    if int(count) >= MAX_ADDRESSES_PER_USER:
        raise HTTPException(status_code=400, detail=f"最多保存 {MAX_ADDRESSES_PER_USER} 个地址")

    address = Address(user_id=user.id, **payload.model_dump())
    if address.is_default:
        _clear_default(db, user)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    payload: AddressIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    address = _get_own_address(db, user, address_id)
    for field, value in payload.model_dump().items():
        setattr(address, field, value)
    if address.is_default:
        _clear_default(db, user, keep_id=address.id)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_dep),
):
    address = _get_own_address(db, user, address_id)
    db.delete(address)
    db.commit()
    return {"detail": "已删除"}