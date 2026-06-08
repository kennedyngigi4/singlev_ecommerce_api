from apps.products.models.models import Product, ProductVariant
from apps.orders.models import Order, OrderItem

class VendorService:

    @staticmethod
    def get_dashboard_data(user):

        total_products = ProductVariant.objects.filter(
            product__created_by=user
        ).count()

        out_of_stock_products = ProductVariant.objects.filter(
            product__created_by=user, is_active=False
        ).count()

        pending_orders = OrderItem.objects.filter(
            product__product__created_by=user, order__status="pending"
        ).count()


        orders_intransit = OrderItem.objects.filter(
            product__product__created_by=user, order__status="in_transit"
        ).count()

        data = {
            "total_products": total_products,
            "out_of_stock_products": out_of_stock_products,
            "pending_orders": pending_orders,
            "orders_intransit": orders_intransit
        }

        return data

