import unittest
import sqlite3

from src.database import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self) -> None:
        self.repo.close()

    # ---------- add ----------
    def test_add_success(self):
        self.assertTrue(self.repo.add(1, "alice", "hello"))
        row = self.repo.get_by_id(1)
        self.assertEqual(row["name"], "alice")
        self.assertEqual(row["message"], "hello")

    def test_add_duplicate_id_raises(self):
        self.repo.add(1, "alice", "hello")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add(1, "bob", "another")

    def test_add_validates_message_length(self):
        with self.assertRaises(ValueError):
            self.repo.add(2, "alice", "x" * 9000)

    def test_add_validates_name_type(self):
        with self.assertRaises(TypeError):
            self.repo.add(3, 123, "hello")

    # ---------- get_by_id ----------
    def test_get_by_id_found(self):
        self.repo.add(5, "carol", "msg")
        self.assertEqual(self.repo.get_by_id(5)["message"], "msg")

    def test_get_by_id_missing_returns_none(self):
        self.assertIsNone(self.repo.get_by_id(999))

    # ---------- get_by_name ----------
    def test_get_by_name_returns_all(self):
        self.repo.add(1, "alice", "a")
        self.repo.add(2, "alice", "b")
        self.repo.add(3, "bob", "c")
        rows = self.repo.get_by_name("alice")
        self.assertEqual(len(rows), 2)

    def test_get_by_name_empty(self):
        self.assertEqual(self.repo.get_by_name("nobody"), [])

    # ---------- update ----------
    def test_update_success(self):
        self.repo.add(1, "alice", "old")
        self.assertTrue(self.repo.update(1, "new"))
        self.assertEqual(self.repo.get_by_id(1)["message"], "new")

    def test_update_missing_id_returns_false(self):
        self.assertFalse(self.repo.update(42, "new"))

    def test_update_validates_length(self):
        self.repo.add(1, "alice", "old")
        with self.assertRaises(ValueError):
            self.repo.update(1, "y" * 9000)

    # ---------- delete ----------
    def test_delete_success(self):
        self.repo.add(1, "alice", "msg")
        self.assertTrue(self.repo.delete(1))
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_missing_returns_false(self):
        self.assertFalse(self.repo.delete(123))


if __name__ == "__main__":
    unittest.main()