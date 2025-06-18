from collections import defaultdict

class OrderManager:
    def __init__(self):
        self.orders = defaultdict(list)

    def add_item(self, user_id, item_key, menu):
        item = menu.get(item_key)
        if item:
            self.orders[user_id].append(item)

    def get_order_summary(self, user_id):
        order = self.orders.get(user_id, [])
        if not order:
            return "Корзина пуста."
        lines = [f"{item['title']} — {item['price']}₽" for item in order]
        total = sum(item['price'] for item in order)
        return "🧾 Ваш заказ:\n" + "\n".join(lines) + f"\n\n💰 Итого: {total}₽"

    def clear_order(self, user_id):
        self.orders[user_id] = []