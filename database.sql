-- =========================================================
-- BRAINQUEST KIDS - DATABASE
-- MySQL 8+
-- =========================================================

CREATE DATABASE IF NOT EXISTS brainquest
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE brainquest;

-- =========================================================
-- 1. CLASSES
-- =========================================================

CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL UNIQUE,
    education_level ENUM(
        'primary',
        'middle',
        'secondary'
    ) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 2. STUDENTS / USERS
-- =========================================================

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    phone VARCHAR(20),

    password VARCHAR(255) NOT NULL,

    role ENUM(
        'student',
        'teacher',
        'admin'
    ) DEFAULT 'student',

    class_id INT NOT NULL,

    profile_photo VARCHAR(255),

    city VARCHAR(100),

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


-- =========================================================
-- 3. ANIMALS
-- =========================================================

CREATE TABLE animals (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    category ENUM(
        'wild',
        'domestic',
        'bird',
        'sea',
        'insect',
        'farm',
        'reptile',
        'other'
    ) DEFAULT 'other',

    scientific_name VARCHAR(150),

    description TEXT,

    habitat VARCHAR(150),

    food VARCHAR(150),

    sound_name VARCHAR(100),

    sound_file VARCHAR(255),

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 4. PHOTOS
-- =========================================================

CREATE TABLE photos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(200) NOT NULL,

    description TEXT,

    image_path VARCHAR(255) NOT NULL,

    category VARCHAR(100),

    animal_id INT NULL,

    class_id INT NULL,

    uploaded_by INT NULL,

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (animal_id)
        REFERENCES animals(id)
        ON DELETE SET NULL,

    FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE SET NULL,

    FOREIGN KEY (uploaded_by)
        REFERENCES students(id)
        ON DELETE SET NULL
);


-- =========================================================
-- 5. VIDEOS
-- =========================================================

CREATE TABLE videos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(200) NOT NULL,

    description TEXT,

    video_path VARCHAR(500) NOT NULL,

    thumbnail_path VARCHAR(255),

    category VARCHAR(100),

    video_type ENUM(
        'education',
        'animal',
        'story',
        'drawing',
        'game',
        'other'
    ) DEFAULT 'education',

    class_id INT NULL,

    duration_seconds INT DEFAULT 0,

    uploaded_by INT NULL,

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE SET NULL,

    FOREIGN KEY (uploaded_by)
        REFERENCES students(id)
        ON DELETE SET NULL
);


-- =========================================================
-- 6. GAMES
-- =========================================================

CREATE TABLE games (
    id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(200) NOT NULL,

    description TEXT,

    game_type ENUM(
        'calculation',
        'image_matching',
        'memory',
        'quiz',
        'puzzle',
        'word',
        'animal',
        'spelling',
        'shape',
        'reaction',
        'sequence',
        'other'
    ) NOT NULL,

    difficulty ENUM(
        'easy',
        'medium',
        'hard'
    ) DEFAULT 'easy',

    class_id INT NULL,

    image_path VARCHAR(255),

    points INT DEFAULT 10,

    time_limit INT DEFAULT 60,

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE SET NULL
);


-- =========================================================
-- 7. QUESTIONS
-- =========================================================

CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    game_id INT NULL,

    question_text TEXT NOT NULL,

    question_image VARCHAR(255),

    option_a VARCHAR(500),

    option_b VARCHAR(500),

    option_c VARCHAR(500),

    option_d VARCHAR(500),

    correct_answer VARCHAR(500) NOT NULL,

    explanation TEXT,

    points INT DEFAULT 10,

    difficulty ENUM(
        'easy',
        'medium',
        'hard'
    ) DEFAULT 'easy',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 8. STORIES
-- =========================================================

CREATE TABLE stories (
    id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(200) NOT NULL,

    description TEXT,

    story_text LONGTEXT,

    cover_image VARCHAR(255),

    video_path VARCHAR(500),

    category ENUM(
        'animal',
        'cartoon',
        'moral',
        'science',
        'adventure',
        'educational',
        'other'
    ) DEFAULT 'educational',

    class_id INT NULL,

    reading_time INT DEFAULT 5,

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE SET NULL
);


-- =========================================================
-- 9. TASKS
-- =========================================================

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(200) NOT NULL,

    description TEXT,

    task_type ENUM(
        'study',
        'game',
        'reading',
        'drawing',
        'quiz',
        'video',
        'memory',
        'creative',
        'other'
    ) NOT NULL,

    class_id INT NULL,

    points INT DEFAULT 10,

    due_date DATE NULL,

    image_path VARCHAR(255),

    status ENUM(
        'active',
        'inactive'
    ) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE SET NULL
);


-- =========================================================
-- 10. STUDENT TASKS
-- =========================================================

CREATE TABLE student_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    task_id INT NOT NULL,

    status ENUM(
        'pending',
        'completed'
    ) DEFAULT 'pending',

    completed_at TIMESTAMP NULL,

    score INT DEFAULT 0,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    FOREIGN KEY (task_id)
        REFERENCES tasks(id)
        ON DELETE CASCADE,

    UNIQUE(student_id, task_id)
);


-- =========================================================
-- 11. DRAWINGS
-- =========================================================

CREATE TABLE drawings (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    title VARCHAR(200) NOT NULL,

    drawing_type ENUM(
        'free_draw',
        'coloring',
        'diagram',
        'challenge'
    ) DEFAULT 'free_draw',

    image_path VARCHAR(255),

    drawing_data LONGTEXT,

    score INT DEFAULT 0,

    teacher_comment TEXT,

    status ENUM(
        'saved',
        'submitted',
        'reviewed'
    ) DEFAULT 'saved',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 12. GAME SCORES
-- =========================================================

CREATE TABLE scores (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    game_id INT NOT NULL,

    score INT DEFAULT 0,

    correct_answers INT DEFAULT 0,

    wrong_answers INT DEFAULT 0,

    time_taken INT DEFAULT 0,

    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 13. XP / STUDENT LEVEL
-- =========================================================

CREATE TABLE student_xp (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL UNIQUE,

    total_xp INT DEFAULT 0,

    current_level INT DEFAULT 1,

    current_streak INT DEFAULT 0,

    longest_streak INT DEFAULT 0,

    last_activity_date DATE NULL,

    updated_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 14. BADGES
-- =========================================================

CREATE TABLE badges (
    id INT AUTO_INCREMENT PRIMARY KEY,

    badge_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT,

    icon_path VARCHAR(255),

    required_xp INT DEFAULT 0,

    badge_type ENUM(
        'learning',
        'memory',
        'game',
        'drawing',
        'story',
        'streak',
        'achievement'
    ) DEFAULT 'achievement',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 15. STUDENT BADGES
-- =========================================================

CREATE TABLE student_badges (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    badge_id INT NOT NULL,

    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    FOREIGN KEY (badge_id)
        REFERENCES badges(id)
        ON DELETE CASCADE,

    UNIQUE(student_id, badge_id)
);


-- =========================================================
-- 16. STUDENT PROGRESS
-- =========================================================

CREATE TABLE progress (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    subject VARCHAR(100),

    total_activities INT DEFAULT 0,

    completed_activities INT DEFAULT 0,

    total_score INT DEFAULT 0,

    average_score DECIMAL(5,2) DEFAULT 0.00,

    last_activity_date DATE NULL,

    updated_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    UNIQUE(student_id, subject)
);


-- =========================================================
-- 17. VIDEO WATCH HISTORY
-- =========================================================

CREATE TABLE video_history (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    video_id INT NOT NULL,

    watched_seconds INT DEFAULT 0,

    completed BOOLEAN DEFAULT FALSE,

    watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    FOREIGN KEY (video_id)
        REFERENCES videos(id)
        ON DELETE CASCADE,

    UNIQUE(student_id, video_id)
);


-- =========================================================
-- 18. STORY PROGRESS
-- =========================================================

CREATE TABLE story_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    story_id INT NOT NULL,

    completed BOOLEAN DEFAULT FALSE,

    score INT DEFAULT 0,

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP NULL,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    FOREIGN KEY (story_id)
        REFERENCES stories(id)
        ON DELETE CASCADE,

    UNIQUE(student_id, story_id)
);


-- =========================================================
-- 19. SAMPLE CLASSES
-- =========================================================

INSERT INTO classes
(class_name, education_level, description)
VALUES
('Class 1', 'primary', 'Primary Level 1'),
('Class 2', 'primary', 'Primary Level 2'),
('Class 3', 'primary', 'Primary Level 3'),
('Class 4', 'primary', 'Primary Level 4'),
('Class 5', 'primary', 'Primary Level 5'),

('Class 6', 'middle', 'Middle School Level 6'),
('Class 7', 'middle', 'Middle School Level 7'),
('Class 8', 'middle', 'Middle School Level 8'),

('Class 9', 'secondary', 'Secondary Level 9'),
('Class 10', 'secondary', 'Secondary Level 10');


-- =========================================================
-- 20. SAMPLE BADGES
-- =========================================================

INSERT INTO badges
(badge_name, description, icon_path, required_xp, badge_type)
VALUES
('First Step', 'Complete your first activity.', 'first-step.png', 10, 'achievement'),

('Math Star', 'Complete mathematics activities.', 'math-star.png', 100, 'learning'),

('Memory Master', 'Complete memory games.', 'memory-master.png', 150, 'memory'),

('Animal Explorer', 'Complete animal activities.', 'animal-explorer.png', 100, 'game'),

('Creative Artist', 'Complete drawing activities.', 'creative-artist.png', 100, 'drawing'),

('Story Reader', 'Read educational stories.', 'story-reader.png', 100, 'story'),

('7 Day Streak', 'Learn for 7 consecutive days.', 'streak-7.png', 200, 'streak'),

('Brain Champion', 'Reach 500 XP.', 'brain-champion.png', 500, 'achievement');


-- =========================================================
-- 21. SAMPLE ANIMALS
-- =========================================================

INSERT INTO animals
(name, category, scientific_name, description, habitat, food, sound_name)
VALUES
('Lion', 'wild', 'Panthera leo',
 'A large wild cat known as the king of the jungle.',
 'Grasslands', 'Meat', 'Roar'),

('Elephant', 'wild', 'Elephas maximus',
 'A large animal with a trunk and big ears.',
 'Forest', 'Plants', 'Trumpet'),

('Dog', 'domestic', 'Canis lupus familiaris',
 'A friendly domestic animal and common pet.',
 'Home', 'Food', 'Bark'),

('Cat', 'domestic', 'Felis catus',
 'A small domestic animal often kept as a pet.',
 'Home', 'Fish and meat', 'Meow'),

('Parrot', 'bird', 'Psittaciformes',
 'A colorful bird that can imitate sounds.',
 'Forest', 'Seeds and fruits', 'Chirp'),

('Dolphin', 'sea', 'Delphinidae',
 'An intelligent marine animal.',
 'Ocean', 'Fish', 'Click');


-- =========================================================
-- 22. SAMPLE GAMES
-- =========================================================

INSERT INTO games
(title, description, game_type, difficulty, points)
VALUES
('Quick Calculation',
 'Solve simple mathematics calculations.',
 'calculation', 'easy', 10),

('Memory Cards',
 'Remember and match the hidden cards.',
 'memory', 'easy', 20),

('Animal Match',
 'Match animals with their names.',
 'animal', 'easy', 15),

('Image Matching',
 'Match the correct images.',
 'image_matching', 'easy', 15),

('Brain Quiz',
 'Answer educational questions.',
 'quiz', 'medium', 20),

('Number Sequence',
 'Find the missing number in the sequence.',
 'sequence', 'medium', 20),

('Word Puzzle',
 'Solve vocabulary puzzles.',
 'word', 'medium', 20);


-- =========================================================
-- DATABASE COMPLETE
-- =========================================================