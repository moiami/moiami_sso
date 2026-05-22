from src.data.models.user import User


def test_check_password_accepts_correct_password() -> None:
    user = User("alice", "secret123", "Alice", "Smith", "alice@example.com")

    assert user.check_password("secret123") is True


def test_check_password_rejects_wrong_password() -> None:
    user = User("alice", "secret123", "Alice", "Smith", "alice@example.com")

    assert user.check_password("wrong-password") is False
