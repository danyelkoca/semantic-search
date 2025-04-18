from app.routes.best_seller import router as best_seller_router
from app.routes.health import router as health_router
from app.routes.products import router as products_router
from app.routes.trending import router as trending_router

routers = [products_router, health_router, trending_router, best_seller_router]
