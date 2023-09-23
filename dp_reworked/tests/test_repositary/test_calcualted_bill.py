import pytest
from src.core import split_bill_calculate  # Replace 'your_module' with the actual module name
from src.domain import CustomItem  # Import your CustomItem model here

@pytest.mark.parametrize("participants, custom_item, number, expected_result", [
    (["Participant 1", "Participant 2", "Participant 3"], CustomItem(price=100.0), 3, 100.0),
    (["Participant 1"], CustomItem(price=50.0), 2, 100.0),
])
def test_split_bill_calculate(participants, custom_item, number, expected_result):
    result = split_bill_calculate(participants, custom_item, number)
    assert result == expected_result
