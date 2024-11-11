from src.utils.shape import Rect


def test_init_with_rect():
    class MockRect:
        x0 = 1
        y0 = 2
        x1 = 3
        y1 = 4
        width = 2
        height = 2
        is_empty = False
        is_valid = True
        is_infinite = False

    mock_rect = MockRect()
    rect = Rect(rect=mock_rect)

    assert rect["x0"] == mock_rect.x0
    assert rect["y0"] == mock_rect.y0
    assert rect["x1"] == mock_rect.x1
    assert rect["y1"] == mock_rect.y1
    assert rect["width"] == mock_rect.width
    assert rect["height"] == mock_rect.height
    assert rect["is_empty"] == mock_rect.is_empty
    assert rect["is_valid"] == mock_rect.is_valid
    assert rect["is_infinite"] == mock_rect.is_infinite


def test_init_with_coords():
    coords = (1, 2, 3, 4)
    rect = Rect(coords=coords)

    assert rect["x0"] == coords[0]
    assert rect["y0"] == coords[1]
    assert rect["x1"] == coords[2]
    assert rect["y1"] == coords[3]
    assert rect["width"] == coords[2] - coords[0]
    assert rect["height"] == coords[3] - coords[1]
    assert not rect["is_empty"]
    assert rect["is_valid"]
    assert not rect["is_infinite"]


def test_extract_coordinates_from_rect():
    coords = (1, 2, 3, 4)
    result = Rect.extract_coordinates_from_rect(coords)

    assert result["x0"] == coords[0]
    assert result["y0"] == coords[1]
    assert result["x1"] == coords[2]
    assert result["y1"] == coords[3]
    assert result["width"] == coords[2] - coords[0]
    assert result["height"] == coords[3] - coords[1]
