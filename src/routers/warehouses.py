from fastapi import APIRouter

warehouse_routes = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@warehouse_routes.get(
    "/{warehouse_id}/products/{product_id}",
    response_model=None,
    description="Возвращает информацию текущем запасе товара в конкретном складе",
)
async def get_product_info(warehouse_id: int, product_id: int):
    return {"warehouse_id": warehouse_id, "product_id": product_id}
