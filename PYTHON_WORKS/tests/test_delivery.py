import unittest
from src.Delivery import calculate_delivery_cost


#def calculate_delivery_cost(weight: float,
#  distance: int, package_type: str, is_express: bool = False)
#  -> tuple:
# return -1, "0000-00-00"

#    # TODO: Проверить физические ограничения на вес и дистанцию (границы до 50кг и 5000км)
   # if weight < 0.1 or weight > 50.0 or distance < 1 or distance > 5000:
   #     return -1, "0000-00-00"
class UnitTestDelivery(unittest.TestCase):
    def test_UncorrectDeliveryTypeUnitTest(self):
        cost,date=calculate_delivery_cost(1.0,100,"безолаберный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_fragile_adds_300(self):
        # 700 + 300 = 1000
        cost, _ = calculate_delivery_cost(1.0, 100, "хрупкий")
        self.assertEqual(cost, 1000)

    def test_dangerous_adds_1000(self):
        # 700 + 1000 = 1700
        cost, _ = calculate_delivery_cost(1.0, 100, "опасный")
        self.assertEqual(cost, 1700)

    def test_regular_no_surcharge(self):
        cost, _ = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)
    
    def test_delivery_date_for_1000km(self):
        # 1000//500=2 → 2026-09-05
        _, date = calculate_delivery_cost(1.0, 1000, "обычный")
        self.assertEqual(date, "2026-09-05")

    def test_delivery_date_for_5000km(self):
        # 5000//500=10 → 2026-09-13
        _, date = calculate_delivery_cost(1.0, 5000, "обычный")
        self.assertEqual(date, "2026-09-13")

    def test_delivery_date_format(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertRegex(date, r"^\d{4}-\d{2}-\d{2}$")
    def test_distance_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 0, "обычный")
        self.assertEqual(cost, -1)

    def test_distance_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 5001, "обычный")
        self.assertEqual(cost, -1)

    def test_distance_at_minimum_boundary_is_valid(self):
        cost, date = calculate_delivery_cost(1.0, 1, "обычный")
        self.assertNotEqual(cost, -1)

    def test_express_should_be_more_expensive_than_regular(self):
            """Экспресс должен быть ДОРОЖЕ обычной доставки."""
            regular, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
            express, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
            self.assertGreater(
                express, regular,
                f"Экспресс ({express}) должен быть дороже обычной ({regular})")
    def test_express_delivery_date_not_zero_days(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        self.assertNotEqual(
            date, "2026-09-03",
            "Экспресс-доставка не может быть в день отправки")    
    def test_weight_10_applies_coefficient_1_2(self):
    # 700 * 1.2 = 840
        cost, _ = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, 840)

    def test_weight_20_applies_coefficient_1_5(self):
        # 700 * 1.5 = 1050
        cost, _ = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(cost, 1050)
    def test_weight_below_minimum_returns_error(self):
        cost, _ = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)

    def test_weight_above_maximum_returns_error(self):
        cost, _ = calculate_delivery_cost(50.1, 100, "обычный")
        self.assertEqual(cost, -1)