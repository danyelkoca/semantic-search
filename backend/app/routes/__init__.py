from backend.app.routes.best_sellers import router as best_seller_router
from backend.app.routes.health import router as health_router
from backend.app.routes.products import router as products_router
from backend.app.routes.trending import router as trending_router

routers = [products_router, health_router, trending_router, best_seller_router]
