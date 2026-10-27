# src/repository.py — абстракция над источником
class ReviewRepository:
    def get_reviews(self, start_date, end_date) -> List[Review]:
        """Код не знает, откуда данные — из файла или из БД"""
        ...
