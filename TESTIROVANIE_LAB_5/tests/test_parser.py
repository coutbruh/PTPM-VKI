import unittest
from pathlib import Path

from src.database import DatabaseRepository
from src.parser import ForumParser, ParsedComment


FIXTURE = Path(__file__).parent / "fixtures" / "forum_page.html"


class TestForumParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = ForumParser()
        self.html = FIXTURE.read_text(encoding="utf-8")

    # ---------- parse_html ----------
    def test_parse_extracts_valid_posts(self):
        posts = self.parser.parse_html(self.html)
        ids = [p.id for p in posts]
        self.assertEqual(ids, [101, 102])          # обманки отброшены
        self.assertEqual(posts[0].name, "alice")
        self.assertEqual(posts[1].name, "bob")

    def test_parse_preserves_inner_html(self):
        posts = self.parser.parse_html(self.html)
        self.assertIn("<b>Привет</b>", posts[0].message)
        self.assertIn("<i>первый</i>", posts[0].message)

    def test_parse_empty_html_returns_empty(self):
        self.assertEqual(self.parser.parse_html("<html></html>"), [])

    # ---------- save_to_db ----------
    def test_save_to_db_inserts_rows(self):
        repo = DatabaseRepository(":memory:")
        posts = [
            ParsedComment(1, "alice", "hello"),
            ParsedComment(2, "bob", "hi"),
        ]
        saved = self.parser.save_to_db(posts, repo)
        self.assertEqual(saved, 2)
        self.assertEqual(repo.get_by_id(1)["name"], "alice")
        repo.close()

    def test_save_to_db_skips_duplicates(self):
        repo = DatabaseRepository(":memory:")
        repo.add(1, "alice", "old")
        posts = [ParsedComment(1, "alice", "new")]
        saved = self.parser.save_to_db(posts, repo)
        self.assertEqual(saved, 0)
        self.assertEqual(repo.get_by_id(1)["message"], "old")
        repo.close()


if __name__ == "__main__":
    unittest.main()