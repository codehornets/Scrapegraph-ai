class Rect(dict):
    def __init__(self, rect=None, coords=None):
        if rect is not None:
            dict.__init__(
                self,
                height=rect.height,
                width=rect.width,
                x0=rect.x0,
                x1=rect.x1,
                y0=rect.y0,
                y1=rect.y1,
                is_empty=rect.is_empty,
                is_valid=rect.is_valid,
                is_infinite=rect.is_infinite,
            )
        elif coords is not None:
            x0, y0, x1, y1 = coords
            dict.__init__(
                self,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                width=x1 - x0,
                height=y1 - y0,
                is_empty=False,
                is_valid=True,
                is_infinite=False,
            )
        else:
            raise ValueError("Either 'rect' or 'coords' must be provided.")

    @staticmethod
    def extract_coordinates_from_rect(rect):
        x0, y0, x1, y1 = rect
        return {
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            "width": x1 - x0,
            "height": y1 - y0,
        }
