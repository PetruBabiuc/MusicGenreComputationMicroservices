class SongGenresPack:
    def __init__(self, remaining_slices: int):
        self.remaining_slices = remaining_slices
        self.genres_to_counts: dict[str, int] = {}
