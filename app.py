from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from models import Base, User, Restaurant, Review, ReviewComment
from config import Config
from naver import fetch_from_naver

app = Flask(__name__)
app.config.from_object(Config)

# DB 없으면 생성, id:root / pwd:1234 로 지정해둔 상태. .
pre_engine = create_engine('mysql+pymysql://root:1234@localhost/')
with pre_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{app.config['DB_NAME']}` DEFAULT CHARACTER SET UTF8;"))

engine = create_engine(
    app.config['SQLALCHEMY_DATABASE_URI'], 
    pool_pre_ping=True
)
# scoped_session ?
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# 테이블 생성
Base.metadata.create_all(engine)




# 로그인 확인
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# 로그인 및 게시판 선택화면
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        db = SessionLocal()
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.query(User).filter_by(username=username).first()
        db.close()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        flash('로그인 정보가 올바르지 않습니다.')
        return redirect(url_for('index'))

    return render_template('index.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = SessionLocal()
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if not username or not password:
            flash('모든 필드를 입력해주세요.')
            db.close()
            return redirect(url_for('register'))
        if password != password2:
            flash('비밀번호가 일치하지 않습니다.')
            db.close()
            return redirect(url_for('register'))
        # 중복 체크
        exists = db.query(User).filter(
            (User.username == username)).first()
        if exists:
            flash('이미 사용 중인 이름입니다.')
            db.close()
            return redirect(url_for('register'))
        
        # 회원가입 성공 시, db에 추가
        new_user = User(username=username, password=password)
        db.add(new_user)
        db.commit()
        db.close()

        flash('회원가입이 완료되었습니다.')
        return redirect(url_for('index'))

    return render_template('register.html')


# 맛집 목록 (검색 + 정렬 + 네이버 API 초기 로딩)
@app.route('/<string:board>')
def list_restaurants(board):
    q    = request.args.get('q', default="", type=str) # 검색어
    sort = request.args.get('sort', default="", type=str)

    db = SessionLocal()

    existing_count = db.query(Restaurant).filter_by(category=board).count()

    # DB에 내역이 없다면 API에서 맛집 내역 불러오기..
    if existing_count == 0:
        for item in fetch_from_naver(board):
            if not db.query(Restaurant).filter_by(name=item['name'], category=board).first():
                db.add(Restaurant(**item))
        db.commit()

    query = db.query(Restaurant).filter_by(category=board)
    if q:
        pattern = f"%{q}%"
        query = query.filter(Restaurant.name.ilike(pattern))

    if sort == 'rating':
        query = query.order_by(Restaurant.avg_rating.desc())
    else:
        query = query.order_by(Restaurant.name.asc())

    restaurants = query.all()
    db.close()

    return render_template('restaurants.html',
                           board=board,
                           restaurants=restaurants,
                           search_query=q,
                           sort_option=sort)

# rest_id 음식점의 리뷰 목록 확인
@app.route('/<string:board>/<int:rest_id>', methods=['GET', 'POST'])
def restaurant_reviews(board, rest_id):
    db = SessionLocal()
    restaurant = db.query(Restaurant).get(rest_id)
    if not restaurant:
        db.close()
        return "Not Found", 404    
    
    # eager loading: db.close이전에 필요한 내역 가져오기
    reviews = db.query(Review)\
                .options(joinedload(Review.user),
                         joinedload(Review.comments).joinedload(ReviewComment.user))\
                .filter_by(restaurant_id=rest_id)\
                .order_by(Review.created_at.desc())\
                .all()
    db.close()    
    return render_template(
        'restaurant_detail.html',
        board=board,
        restaurant=restaurant,
        reviews=reviews
    )

# 특정 리뷰 상세페이지
@app.route('/<string:board>/<int:rest_id>/<int:review_id>')
def review_detail(board, rest_id, review_id):
    db = SessionLocal()
    review = db.query(Review).filter_by(id=review_id, restaurant_id=rest_id).first()
    if not review:
        db.close()
        return "Not Found", 404

    reviews = db.query(Review)\
                .filter_by(restaurant_id=rest_id)\
                .order_by(Review.created_at.desc())\
                .all()
    db.close()
    return render_template('restaurant_detail.html',
                           board=board,
                           review=review)

# 리뷰 작성
@app.route('/<string:board>/<int:rest_id>/review', methods=['POST'])
@login_required
def add_review(board, rest_id):
    rating  = request.form.get('rating', type=int)
    comment = request.form.get('comment', type=str)

    if rating is None or rating < 1 or rating > 5:
        flash('평점은 1~5 사이로 선택해주세요.')
        return redirect(url_for('restaurant_reviews', board=board, rest_id=rest_id))
    if not comment or not comment.strip():
        flash('후기 내용을 작성해주세요.')
        return redirect(url_for('restaurant_reviews', board=board, rest_id=rest_id))

    db = SessionLocal()
    restaurant = db.query(Restaurant).get(rest_id)
    if not restaurant:
        db.close()
        return "Not Found", 404

    old_reviews = db.query(Review).filter_by(restaurant_id=rest_id).all()
    old_cnt = len(old_reviews)
    old_sum = sum(r.rating for r in old_reviews)

    new_rev = Review(
        restaurant_id=rest_id,
        user_id      = session['user_id'],
        rating       = rating,
        comment      = comment.strip()
    )
    db.add(new_rev)

    # 평균 평점 계산하기 (처음 계산 시 DivisionByZero 떠서 old_vals 필요한듯)
    rev_cnt = old_cnt + 1
    rating_sum = old_sum + rating
    restaurant.avg_rating = round(rating_sum / rev_cnt, 2)

    db.commit()
    db.close()

    flash('후기를 등록했습니다.')
    return redirect(url_for('restaurant_reviews', board=board, rest_id=rest_id))

@app.route('/comment/<int:review_id>', methods=['POST'])
@login_required
def add_comment(review_id):
    comment_text = request.form.get("comment", "").strip()
    if not comment_text:
        flash("댓글 내용을 작성해주세요")
        return redirect(request.referrer or url_for('index'))
    
    db = SessionLocal()
    review = db.query(Review).get(review_id)
    if not review:
        db.close()
        return "REV Not Found", 404
    
    new_comment = ReviewComment(
        review_id = review_id,
        user_id = session['user_id'],
        comment = comment_text
    )
    db.add(new_comment)
    db.commit()
    db.close()

    flash('댓글이 등록되었습니다.')
    return redirect(request.referrer or url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
