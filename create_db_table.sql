DROP DATABASES IF EXISTS hungry_aix;
CREATE DATABASE hungry_aix default CHARACTER SET UTF8;
USE hungry_aix;


-- 사용자 테이블
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50)  NOT NULL UNIQUE,   
    password VARCHAR(100) NOT NULL,          -- Hashing 고민중 ?.. 나중엥..
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 식당 테이블
CREATE TABLE restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    address VARCHAR(255),
    latitude DOUBLE,
    longitude DOUBLE,
    phone VARCHAR(20),
    hours VARCHAR(100),
    avg_rating FLOAT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 리뷰 테이블
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT
    user_id INT
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- restaurant_id는 restaurants.id / user_id는 users.id를 참조한다는 내용 
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
);

COMMIT;