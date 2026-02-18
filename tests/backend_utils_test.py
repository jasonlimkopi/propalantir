from backend.src.utils import get_prop_list

def test_get_prop_list():
    mock_data = "tests/mock_data/mock_realis_processed.csv"
    mock_prop_list = get_prop_list(mock_data)
    assert isinstance(mock_prop_list, list)
    assert len(mock_prop_list) > 0