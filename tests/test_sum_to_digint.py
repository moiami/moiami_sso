import pytest

@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (10, 15, 25),
        (0, 5, 5),
        (-3, -7, -10),
        (-5, 10, 5),
    ],
)
def test_sum_to_digint(a: int, b: int, expected: int) -> None:
    assert a+b == expected
