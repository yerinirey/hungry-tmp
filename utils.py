# gpt_generated; 평점 예쁘게 나타내는 마크업 유틸 써보기
from markupsafe import Markup

def render_stars(rating: float) -> str:
    full_stars = int(rating)
    half_star = 1 if 0.25 <= rating - full_stars < 0.75 else 0
    if rating - full_stars >= 0.75:
        full_stars += 1
        half_star = 0
    empty_stars = 5 - full_stars - half_star

    stars = '★' * full_stars
    if half_star:
        stars += '★'  # 반개짜리가 없네
    stars += '☆' * empty_stars
    return Markup(stars)
