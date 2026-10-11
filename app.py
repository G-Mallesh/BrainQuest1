import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory,
    jsonify
)

from werkzeug.utils import secure_filename

import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from backend import student
from config import DB_CONFIG, SECRET_KEY


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = SECRET_KEY


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# UPLOAD FOLDERS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

PROFILE_UPLOAD_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "profiles"
)

IMAGE_UPLOAD_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "images"
)

VIDEO_UPLOAD_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "videos"
)

DRAWING_UPLOAD_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "drawings"
)


# =========================================================
# CREATE FOLDERS
# =========================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    PROFILE_UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    IMAGE_UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    VIDEO_UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    DRAWING_UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# FLASK UPLOAD CONFIGURATION
# =========================================================

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["PROFILE_UPLOAD_FOLDER"] = PROFILE_UPLOAD_FOLDER

app.config["IMAGE_UPLOAD_FOLDER"] = IMAGE_UPLOAD_FOLDER

app.config["VIDEO_UPLOAD_FOLDER"] = VIDEO_UPLOAD_FOLDER

app.config["DRAWING_UPLOAD_FOLDER"] = DRAWING_UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

ALLOWED_VIDEO_EXTENSIONS = {
    "mp4",
    "webm",
    "mov"
}


# =========================================================
# FILE VALIDATION
# =========================================================

def allowed_file(filename, extensions):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in extensions
    )


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    return mysql.connector.connect(
        **DB_CONFIG
    )



# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# DATABASE TEST
# =========================================================

@app.route("/test-db")
def test_db():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT DATABASE()"
        )

        result = cursor.fetchone()

        database_name = (
            result[0]
            if result
            else "Unknown"
        )

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Test</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 60px;
                    background: #f4f8ff;
                }}

                .box {{
                    max-width: 600px;
                    margin: auto;
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                }}

                h1 {{
                    color: green;
                }}

                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 25px;
                    background: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }}
            </style>
        </head>

        <body>

            <div class="box">

                <h1>✅ Database Connected</h1>

                <p>
                    MySQL connection is working successfully.
                </p>

                <p>
                    <strong>Database:</strong>
                    {database_name}
                </p>

                <a href="/">
                    Go Home
                </a>

            </div>

        </body>
        </html>
        """

    except mysql.connector.Error as error:

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Error</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 60px;
                    background: #fff5f5;
                }}

                .box {{
                    max-width: 700px;
                    margin: auto;
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                }}

                h1 {{
                    color: red;
                }}

                .error {{
                    background: #fee2e2;
                    padding: 15px;
                    border-radius: 8px;
                    color: #991b1b;
                    word-wrap: break-word;
                }}

                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 25px;
                    background: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }}
            </style>
        </head>

        <body>

            <div class="box">

                <h1>❌ Database Connection Failed</h1>

                <div class="error">
                    {error}
                </div>

                <a href="/">
                    Go Home
                </a>

            </div>

        </body>
        </html>
        """

    except Exception as error:

        return f"""
        <h1>❌ Unexpected Error</h1>
        <p>{error}</p>
        <a href="/">Home</a>
        """

    finally:

        if cursor is not None:

            try:
                cursor.close()
            except Exception:
                pass

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass


# =========================================================
# UPLOAD FILE SERVING
# =========================================================

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "app": "BrainQuest"
    })


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>The requested page does not exist.</p>
    <a href="/">Go Home</a>
    """, 404


# =========================================================
# 500 ERROR
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):

    return """
    <h1>500 - Internal Server Error</h1>
    <p>Something went wrong on the server.</p>
    <a href="/">Go Home</a>
    """, 500



# =========================================================
# BADGE SYSTEM
# =========================================================

def update_student_rewards(
    cursor,
    student_id
):

    # Get XP
    cursor.execute("""
        SELECT total_xp
        FROM student_xp
        WHERE student_id = %s
    """, (student_id,))

    xp_row = cursor.fetchone()

    total_xp = 0

    if xp_row:
        total_xp = xp_row["total_xp"]


    # Get current badges
    cursor.execute("""
        SELECT badge_name, required_xp
        FROM badges
    """)

    all_badges = cursor.fetchall()


    for badge in all_badges:

        # Check XP requirement
        if total_xp < (
            badge["required_xp"] or 0
        ):
            continue


        # Check if already earned
        cursor.execute("""
            SELECT id
            FROM student_badges
            WHERE student_id = %s

            AND badge_id = (
                SELECT id
                FROM badges
                WHERE badge_name = %s
            )
        """, (
            student_id,
            badge["badge_name"]
        ))

        already_earned = cursor.fetchone()


        if not already_earned:

            cursor.execute("""
                INSERT INTO student_badges
                (
                    student_id,
                    badge_id,
                    earned_at
                )
                SELECT
                    %s,
                    id,
                    NOW()
                FROM badges
                WHERE badge_name = %s
            """, (
                student_id,
                badge["badge_name"]
            ))

# =========================================================
# DAILY STREAK SYSTEM
# =========================================================

from datetime import date, timedelta


def update_student_streak(cursor, student_id):

    cursor.execute("""
        SELECT
            current_streak,
            longest_streak,
            last_activity_date
        FROM student_xp
        WHERE student_id = %s
    """, (student_id,))

    row = cursor.fetchone()

    if not row:
        return 1


    current_streak = row["current_streak"] or 0
    longest_streak = row["longest_streak"] or 0
    last_activity = row["last_activity_date"]

    today = date.today()


    # First activity
    if last_activity is None:

        current_streak = 1


    else:

        # Convert datetime to date if necessary
        if hasattr(last_activity, "date"):
            last_activity = last_activity.date()


        difference = (
            today - last_activity
        ).days


        # Already active today
        if difference == 0:

            return current_streak


        # Activity on previous day
        elif difference == 1:

            current_streak += 1


        # Missed one or more days
        else:

            current_streak = 1


    # Update longest streak

    if current_streak > longest_streak:
        longest_streak = current_streak


    cursor.execute("""
        UPDATE student_xp

        SET
            current_streak = %s,
            longest_streak = %s,
            last_activity_date = %s,
            updated_at = NOW()

        WHERE student_id = %s
    """, (
        current_streak,
        longest_streak,
        today,
        student_id
    ))


    return current_streak
# =========================================================
# REWARD UPDATE
# =========================================================

def update_student_rewards(cursor, student_id):

    # Update streak
    current_streak = update_student_streak(
        cursor,
        student_id
    )


    # Get XP

    cursor.execute("""
        SELECT total_xp
        FROM student_xp
        WHERE student_id = %s
    """, (student_id,))

    xp_row = cursor.fetchone()

    total_xp = 0

    if xp_row:
        total_xp = xp_row["total_xp"] or 0


    # Calculate level

    current_level = (
        total_xp // 100
    ) + 1


    cursor.execute("""
        UPDATE student_xp

        SET current_level = %s,
            updated_at = NOW()

        WHERE student_id = %s
    """, (
        current_level,
        student_id
    ))


    # Award badges

    check_and_award_achievement_badges(
        cursor,
        student_id,
        total_xp,
        current_streak
    )
# =========================================================
# ACHIEVEMENT BADGES
# =========================================================

def award_badge(cursor, student_id, badge_name):

    cursor.execute("""
        SELECT id
        FROM badges
        WHERE badge_name = %s
    """, (badge_name,))

    badge = cursor.fetchone()

    if not badge:
        return


    badge_id = badge["id"]


    cursor.execute("""
        SELECT id
        FROM student_badges
        WHERE student_id = %s
          AND badge_id = %s
    """, (
        student_id,
        badge_id
    ))

    existing = cursor.fetchone()


    if not existing:

        cursor.execute("""
            INSERT INTO student_badges
            (
                student_id,
                badge_id,
                earned_at
            )
            VALUES
            (%s, %s, NOW())
        """, (
            student_id,
            badge_id
        ))
def check_and_award_achievement_badges(
    cursor,
    student_id,
    total_xp,
    current_streak
):

    # =====================================================
    # FIRST STEP
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM scores
        WHERE student_id = %s
    """, (student_id,))

    games = cursor.fetchone()["total"]


    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM student_tasks
        WHERE student_id = %s
          AND status = 'completed'
    """, (student_id,))

    tasks = cursor.fetchone()["total"]


    if games >= 1 or tasks >= 1:

        award_badge(
            cursor,
            student_id,
            "First Step"
        )


    # =====================================================
    # MATH STAR
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM scores s

        JOIN games g
            ON s.game_id = g.id

        WHERE s.student_id = %s

          AND g.game_type = 'calculation'
    """, (student_id,))

    math_games = cursor.fetchone()["total"]


    if math_games >= 5:

        award_badge(
            cursor,
            student_id,
            "Math Star"
        )


    # =====================================================
    # MEMORY MASTER
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM scores s

        JOIN games g
            ON s.game_id = g.id

        WHERE s.student_id = %s

          AND g.game_type = 'memory'
    """, (student_id,))

    memory_games = cursor.fetchone()["total"]


    if memory_games >= 5:

        award_badge(
            cursor,
            student_id,
            "Memory Master"
        )


    # =====================================================
    # ANIMAL EXPLORER
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM scores s

        JOIN games g
            ON s.game_id = g.id

        WHERE s.student_id = %s

          AND g.game_type = 'animal'
    """, (student_id,))

    animal_games = cursor.fetchone()["total"]


    if animal_games >= 3:

        award_badge(
            cursor,
            student_id,
            "Animal Explorer"
        )


    # =====================================================
    # CREATIVE ARTIST
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM drawings
        WHERE student_id = %s
    """, (student_id,))

    drawings = cursor.fetchone()["total"]


    if drawings >= 3:

        award_badge(
            cursor,
            student_id,
            "Creative Artist"
        )


    # =====================================================
    # STORY READER
    # =====================================================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM story_progress

        WHERE student_id = %s
          AND completed = 1
    """, (student_id,))

    stories = cursor.fetchone()["total"]


    if stories >= 3:

        award_badge(
            cursor,
            student_id,
            "Story Reader"
        )


    # =====================================================
    # 7 DAY STREAK
    # =====================================================

    if current_streak >= 7:

        award_badge(
            cursor,
            student_id,
            "7 Day Streak"
        )


    # =====================================================
    # BRAIN CHAMPION
    # =====================================================

    if total_xp >= 1000:

        award_badge(
            cursor,
            student_id,
            "Brain Champion"
        )

           
# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # =====================================================
    # POST - CREATE NEW STUDENT
    # =====================================================

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        education_level = request.form.get(
            "education_level",
            ""
        ).strip().lower()

        class_id = request.form.get(
            "class_id",
            ""
        ).strip()


        # =================================================
        # REQUIRED FIELD VALIDATION
        # =================================================

        if not full_name or not email or not password:

            flash(
                "Please fill all required fields."
            )

            return redirect(
                url_for("register")
            )


        if not education_level or not class_id:

            flash(
                "Please select education level and class."
            )

            return redirect(
                url_for("register")
            )


        # =================================================
        # ALLOWED EDUCATION LEVELS
        # =================================================

        allowed_levels = [
            "primary",
            "middle",
            "secondary"
        ]


        if education_level not in allowed_levels:

            flash(
                "Invalid education level."
            )

            return redirect(
                url_for("register")
            )


        connection = None
        cursor = None


        try:

            # =============================================
            # DATABASE CONNECTION
            # =============================================

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )


            # =============================================
            # CHECK CLASS
            # =============================================

            cursor.execute(
                """
                SELECT
                    id,
                    class_name,
                    education_level
                FROM classes
                WHERE id = %s
                """,
                (
                    class_id,
                )
            )

            selected_class = cursor.fetchone()


            if not selected_class:

                flash(
                    "Invalid class selected."
                )

                return redirect(
                    url_for("register")
                )


            # =============================================
            # CHECK EDUCATION LEVEL MATCH
            # =============================================

            if (
                selected_class["education_level"]
                != education_level
            ):

                flash(
                    "Class does not match education level."
                )

                return redirect(
                    url_for("register")
                )


            # =============================================
            # CHECK EMAIL
            # =============================================

            cursor.execute(
                """
                SELECT
                    id
                FROM students
                WHERE email = %s
                """,
                (
                    email,
                )
            )

            existing_student = cursor.fetchone()


            if existing_student:

                flash(
                    "Email already registered."
                )

                return redirect(
                    url_for("register")
                )


            # =============================================
            # PASSWORD HASHING
            # =============================================

            hashed_password = generate_password_hash(
                password
            )


            # =============================================
            # CREATE STUDENT
            # =============================================

            cursor.execute(
                """
                INSERT INTO students
                (
                    full_name,
                    email,
                    phone,
                    password,
                    role,
                    class_id
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'student',
                    %s
                )
                """,
                (
                    full_name,
                    email,
                    phone,
                    hashed_password,
                    class_id
                )
            )


            # =============================================
            # GET NEW STUDENT ID
            # =============================================

            student_id = cursor.lastrowid


            # =============================================
            # GENERATE CHILD CODE
            # =============================================

            child_code = f"BQ{student_id:05d}"


            # =============================================
            # SAVE CHILD CODE
            # =============================================

            cursor.execute(
                """
                UPDATE students
                SET child_code = %s
                WHERE id = %s
                """,
                (
                    child_code,
                    student_id
                )
            )


            # =============================================
            # CREATE XP RECORD
            # =============================================

            cursor.execute(
                """
                INSERT INTO student_xp
                (
                    student_id,
                    total_xp,
                    current_level,
                    current_streak
                )
                VALUES
                (
                    %s,
                    0,
                    1,
                    0
                )
                """,
                (
                    student_id,
                )
            )


            # =============================================
            # COMMIT EVERYTHING
            # =============================================

            connection.commit()


            # =============================================
            # SUCCESS MESSAGE
            # =============================================

            flash(
                f"🎉 Registration successful! "
                f"Your Child Code is {child_code}"
            )


            return redirect(
                url_for("login")
            )


        # =================================================
        # DATABASE ERROR
        # =================================================

        except mysql.connector.Error as error:

            if connection:

                connection.rollback()


            print(
                "Registration Error:",
                error
            )


            flash(
                "❌ Registration failed. "
                "Please try again."
            )


            return redirect(
                url_for("register")
            )


        # =================================================
        # CLOSE DATABASE
        # =================================================

        finally:

            if cursor:

                cursor.close()


            if connection:

                connection.close()


    # =====================================================
    # GET - LOAD REGISTRATION PAGE
    # =====================================================

    connection = None
    cursor = None

    classes = []


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # ================================================
        # LOAD CLASSES
        # ================================================

        cursor.execute(
            """
            SELECT
                id,
                class_name,
                education_level
            FROM classes
            ORDER BY id
            """
        )


        classes = cursor.fetchall()


    except mysql.connector.Error as error:

        print(
            "Class Loading Error:",
            error
        )

        classes = []


    finally:

        if cursor:

            cursor.close()


        if connection:

            connection.close()


    # =====================================================
    # SHOW REGISTER PAGE
    # =====================================================

    return render_template(
        "register.html",
        classes=classes
    )

# =========================================================
# LOGIN
# =========================================================

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not email or not password:

            flash(
                "Please enter email and password."
            )

            return redirect(
                url_for("login")
            )

        connection = None
        cursor = None

        try:

            # -------------------------------------------------
            # DATABASE CONNECTION
            # -------------------------------------------------

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            # -------------------------------------------------
            # FIND USER
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT
                    s.id,
                    s.full_name,
                    s.email,
                    s.password,
                    s.role,
                    s.class_id,
                    c.class_name,
                    c.education_level

                FROM students s

                LEFT JOIN classes c
                    ON s.class_id = c.id

                WHERE s.email = %s
                  AND s.status = 'active'
                """,
                (email,)
            )

            student = cursor.fetchone()

            # -------------------------------------------------
            # USER NOT FOUND
            # -------------------------------------------------

            if not student:

                flash(
                    "❌ Email or password is incorrect."
                )

                return redirect(
                    url_for("login")
                )

            # -------------------------------------------------
            # CHECK PASSWORD
            # -------------------------------------------------

            if not check_password_hash(
                student["password"],
                password
            ):

                flash(
                    "❌ Email or password is incorrect."
                )

                return redirect(
                    url_for("login")
                )

            # -------------------------------------------------
            # CREATE SESSION
            # -------------------------------------------------

            session.clear()

            session["student_id"] = student["id"]

            session["student_name"] = student[
                "full_name"
            ]

            session["student_email"] = student[
                "email"
            ]

            session["role"] = student[
                "role"
            ]

            session["class_id"] = student[
                "class_id"
            ]

            session["class_name"] = student[
                "class_name"
            ]

            session["education_level"] = student[
                "education_level"
            ]

            # -------------------------------------------------
            # STUDENT REWARDS
            # -------------------------------------------------

            if student["role"] == "student":

                try:

                    update_student_rewards(
                        cursor,
                        student["id"]
                    )

                    connection.commit()

                except Exception as reward_error:

                    print(
                        "Reward Update Error:",
                        reward_error
                    )

            # -------------------------------------------------
            # ROLE-BASED REDIRECT
            # -------------------------------------------------

            if student["role"] == "teacher":

                return redirect(
                    url_for("teacher_dashboard")
                )

            elif student["role"] == "admin":

                return redirect(
                    url_for("admin_dashboard")
                )

            else:

                return redirect(
                    url_for("dashboard")
                )

        # -----------------------------------------------------
        # DATABASE ERROR
        # -----------------------------------------------------

        except mysql.connector.Error as error:

            print(
                "Login Error:",
                error
            )

            flash(
                "Database error. Please try again."
            )

            return redirect(
                url_for("login")
            )

        # -----------------------------------------------------
        # CLOSE DATABASE
        # -----------------------------------------------------

        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()

    # ---------------------------------------------------------
    # LOGIN PAGE
    # ---------------------------------------------------------

    return render_template(
        "login.html"
    )
# =========================================================
# DASHBOARD
# =========================================================
@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]
    class_id = session.get("class_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # -----------------------------
    # Student information
    # -----------------------------

    cursor.execute("""
        SELECT
            s.id,
            s.full_name,
            s.email,
            s.city,
            c.class_name,
            c.education_level
        FROM students s
        LEFT JOIN classes c
            ON s.class_id = c.id
        WHERE s.id=%s
    """, (student_id,))

    student = cursor.fetchone()

    # -----------------------------
    # XP information
    # -----------------------------

    cursor.execute("""
        SELECT
            total_xp,
            current_level,
            current_streak,
            longest_streak,
            last_activity_date
        FROM student_xp
        WHERE student_id=%s
    """, (student_id,))

    xp = cursor.fetchone()

    if not xp:
        xp = {
            "total_xp": 0,
            "current_level": 1,
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None
        }

    # -----------------------------
    # Badges
    # -----------------------------

    cursor.execute("""
        SELECT
            b.id,
            b.badge_name,
            b.description,
            b.icon_path,
            b.required_xp,
            sb.earned_at
        FROM student_badges sb
        JOIN badges b
            ON sb.badge_id = b.id
        WHERE sb.student_id=%s
        ORDER BY sb.earned_at DESC
        LIMIT 6
    """, (student_id,))

    badges = cursor.fetchall()

    # -----------------------------
    # Badge count
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*) AS badge_count
        FROM student_badges
        WHERE student_id=%s
    """, (student_id,))

    badge_count = cursor.fetchone()["badge_count"]

    # -----------------------------
    # Daily tasks
    # -----------------------------

    cursor.execute("""
        SELECT
            t.id,
            t.title,
            t.task_type,
            t.points,
            st.status
        FROM tasks t
        LEFT JOIN student_tasks st
            ON t.id = st.task_id
            AND st.student_id=%s
        WHERE t.status='active'
        AND (
            t.class_id=%s
            OR t.class_id IS NULL
        )
        ORDER BY
            CASE
                WHEN st.status='completed'
                THEN 1
                ELSE 0
            END,
            t.id DESC
        LIMIT 5
    """, (student_id, class_id))

    daily_tasks = cursor.fetchall()

    # -----------------------------
    # Recommended games
    # -----------------------------

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            game_type,
            difficulty,
            points
        FROM games
        WHERE status='active'
        AND (
            class_id=%s
            OR class_id IS NULL
        )
        ORDER BY id DESC
        LIMIT 4
    """, (class_id,))

    recommended_games = cursor.fetchall()

    # -----------------------------
    # Recommended stories
    # -----------------------------

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            category,
            cover_image,
            reading_time
        FROM stories
        WHERE status='active'
        AND (
            class_id=%s
            OR class_id IS NULL
        )
        ORDER BY id DESC
        LIMIT 4
    """, (class_id,))

    recommended_stories = cursor.fetchall()

    # -----------------------------
    # Recommended videos
    # -----------------------------

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            category,
            video_type,
            thumbnail_path,
            duration_seconds
        FROM videos
        WHERE status='active'
        AND (
            class_id=%s
            OR class_id IS NULL
        )
        ORDER BY id DESC
        LIMIT 4
    """, (class_id,))

    recommended_videos = cursor.fetchall()

    # -----------------------------
    # Completed activities
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*) AS completed_games
        FROM scores
        WHERE student_id=%s
    """, (student_id,))

    completed_games = cursor.fetchone()["completed_games"]

    cursor.execute("""
        SELECT COUNT(*) AS completed_tasks
        FROM student_tasks
        WHERE student_id=%s
        AND status='completed'
    """, (student_id,))

    completed_tasks = cursor.fetchone()["completed_tasks"]

    cursor.execute("""
        SELECT COUNT(*) AS completed_stories
        FROM story_progress
        WHERE student_id=%s
        AND completed=1
    """, (student_id,))

    completed_stories = cursor.fetchone()["completed_stories"]

    cursor.execute("""
        SELECT COUNT(*) AS completed_videos
        FROM video_history
        WHERE student_id=%s
        AND completed=1
    """, (student_id,))

    completed_videos = cursor.fetchone()["completed_videos"]

    cursor.close()
    connection.close()

    # -----------------------------
    # XP level progress
    # -----------------------------

    total_xp = xp["total_xp"] or 0

    current_level = xp["current_level"] or 1

    current_level_xp = total_xp % 100

    xp_percentage = current_level_xp

    xp_remaining = 100 - current_level_xp

    return render_template(
        "dashboard.html",
        student=student,
        xp=xp,
        badges=badges,
        badge_count=badge_count,
        daily_tasks=daily_tasks,
        recommended_games=recommended_games,
        recommended_stories=recommended_stories,
        recommended_videos=recommended_videos,
        completed_games=completed_games,
        completed_tasks=completed_tasks,
        completed_stories=completed_stories,
        completed_videos=completed_videos,
        current_level_xp=current_level_xp,
        xp_percentage=xp_percentage,
        xp_remaining=xp_remaining
    )
# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "👋 You have been logged out."
    )

    return redirect(
        url_for("home")
    )

# =========================================================
# CALCULATION GAME
# =========================================================

import random


@app.route("/games/calculation")
def calculation_game():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )


    class_name = session.get(
        "class_name",
        "Class 1"
    )


    # -----------------------------------------------------
    # Difficulty based on class
    # -----------------------------------------------------

    class_number = int(
        class_name.replace(
            "Class ",
            ""
        )
    )


    questions = []


    for _ in range(10):

        # Primary: Classes 1-5

        if class_number <= 5:

            a = random.randint(
                1,
                20 + class_number * 5
            )

            b = random.randint(
                1,
                20 + class_number * 5
            )


            operation = random.choice([
                "+",
                "-"
            ])


            if operation == "+":

                answer = a + b

                question = (
                    f"{a} + {b} = ?"
                )

            else:

                # Avoid negative answers

                if b > a:

                    a, b = b, a


                answer = a - b

                question = (
                    f"{a} - {b} = ?"
                )


        # Middle: Classes 6-8

        elif class_number <= 8:

            a = random.randint(
                10,
                100
            )

            b = random.randint(
                2,
                20
            )


            operation = random.choice([
                "+",
                "-",
                "*"
            ])


            if operation == "+":

                answer = a + b

                question = (
                    f"{a} + {b} = ?"
                )

            elif operation == "-":

                if b > a:

                    a, b = b, a


                answer = a - b

                question = (
                    f"{a} - {b} = ?"
                )

            else:

                answer = a * b

                question = (
                    f"{a} × {b} = ?"
                )


        # Secondary: Classes 9-10

        else:

            a = random.randint(
                10,
                200
            )

            b = random.randint(
                2,
                30
            )


            operation = random.choice([
                "+",
                "-",
                "*",
                "//"
            ])


            if operation == "+":

                answer = a + b

                question = (
                    f"{a} + {b} = ?"
                )

            elif operation == "-":

                if b > a:

                    a, b = b, a


                answer = a - b

                question = (
                    f"{a} - {b} = ?"
                )

            elif operation == "*":

                answer = a * b

                question = (
                    f"{a} × {b} = ?"
                )

            else:

                # Make clean division

                answer = random.randint(
                    2,
                    20
                )

                b = random.randint(
                    2,
                    15
                )

                a = answer * b

                question = (
                    f"{a} ÷ {b} = ?"
                )


        questions.append({

            "question": question,

            "answer": answer

        })


    return render_template(

        "games/calculation.html",

        questions=questions,

        class_name=class_name

    )


# =========================================================
# SAVE CALCULATION SCORE
# =========================================================

@app.route(
    "/games/calculation/save",
    methods=["POST"]
)
def save_calculation_score():

    if "student_id" not in session:

        return {
            "success": False,
            "message": "Login required"
        }, 401


    data = request.get_json()


    score = int(
        data.get("score", 0)
    )

    correct_answers = int(
        data.get(
            "correct_answers",
            0
        )
    )

    wrong_answers = int(
        data.get(
            "wrong_answers",
            0
        )
    )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        # Save game score

        # Game ID 1 = Quick Calculation

        cursor.execute(
            """
            INSERT INTO scores
            (
                student_id,
                game_id,
                score,
                correct_answers,
                wrong_answers,
                time_taken
            )
            VALUES
            (
                %s,
                1,
                %s,
                %s,
                %s,
                0
            )
            """,
            (
                session["student_id"],
                score,
                correct_answers,
                wrong_answers
            )
        )


        # Add XP

        cursor.execute(
            """
            UPDATE student_xp

            SET total_xp =
                total_xp + %s

            WHERE student_id = %s
            """,
            (
                score,
                session["student_id"]
            )
        )


        # Calculate level

        cursor.execute(
            """
            SELECT total_xp
            FROM student_xp
            WHERE student_id = %s
            """,
            (session["student_id"],)
        )


        xp_result = cursor.fetchone()


        if xp_result:

            total_xp = xp_result[0]

            new_level = (
                total_xp // 100
            ) + 1


            cursor.execute(
                """
                UPDATE student_xp

                SET current_level = %s

                WHERE student_id = %s
                """,
                (
                    new_level,
                    session["student_id"]
                )
            )

        update_student_rewards(
    cursor,
    session["student_id"]
)
        connection.commit()


        return {
            "success": True,
            "message": "Score saved!",
            "xp": score
        }


    except mysql.connector.Error as error:

        if connection:

            connection.rollback()


        print(
            "Score Error:",
            error
        )


        return {
            "success": False,
            "message": "Could not save score."
        }, 500


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()
# =========================================================
# ANIMAL WORLD
# =========================================================

@app.route("/animals")
def animals():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    category = request.args.get("category", "").strip()

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if category:
            cursor.execute(
                """
                SELECT *
                FROM animals
                WHERE category = %s
                  AND status = 'active'
                ORDER BY name
                """,
                (category,)
            )
        else:
            cursor.execute(
                """
                SELECT *
                FROM animals
                WHERE status = 'active'
                ORDER BY name
                """
            )

        animals_data = cursor.fetchall()

        return render_template(
            "animals/animals.html",
            animals=animals_data,
            selected_category=category
        )

    except mysql.connector.Error as error:

        print("Animal Error:", error)

        flash("Unable to load animals.")

        return redirect(url_for("dashboard"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ANIMAL DETAILS
# =========================================================

@app.route("/animals/<int:animal_id>")
def animal_details(animal_id):

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM animals
            WHERE id = %s
              AND status = 'active'
            """,
            (animal_id,)
        )

        animal = cursor.fetchone()

        if not animal:
            flash("Animal not found.")
            return redirect(url_for("animals"))

        return render_template(
            "animals/animal_details.html",
            animal=animal
        )

    except mysql.connector.Error as error:

        print("Animal Details Error:", error)

        flash("Unable to load animal.")

        return redirect(url_for("animals"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ANIMAL QUIZ
# =========================================================

@app.route("/animals/quiz")
def animal_quiz():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, category
            FROM animals
            WHERE status = 'active'
            ORDER BY RAND()
            LIMIT 5
            """
        )

        quiz_animals = cursor.fetchall()

        questions = []

        for animal in quiz_animals:

            cursor.execute(
                """
                SELECT id, name
                FROM animals
                WHERE status = 'active'
                  AND id != %s
                ORDER BY RAND()
                LIMIT 3
                """,
                (animal["id"],)
            )

            wrong_options = cursor.fetchall()

            options = [
                {
                    "id": animal["id"],
                    "name": animal["name"]
                }
            ]

            options.extend(wrong_options)

            random.shuffle(options)

            questions.append({
                "animal_id": animal["id"],
                "answer": animal["name"],
                "options": options
            })

        return render_template(
            "animals/animal_quiz.html",
            questions=questions
        )

    except mysql.connector.Error as error:

        print("Animal Quiz Error:", error)

        flash("Unable to start quiz.")

        return redirect(url_for("animals"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# SAVE ANIMAL QUIZ
# =========================================================

@app.route(
    "/animals/quiz/save",
    methods=["POST"]
)
def save_animal_quiz():

    if "student_id" not in session:

        return {
            "success": False,
            "message": "Login required"
        }, 401

    data = request.get_json()

    score = int(
        data.get("score", 0)
    )

    correct = int(
        data.get("correct", 0)
    )

    wrong = int(
        data.get("wrong", 0)
    )

    # Animal quiz uses Game ID 3
    game_id = 3

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # Save score
        cursor.execute(
            """
            INSERT INTO scores
            (
                student_id,
                game_id,
                score,
                correct_answers,
                wrong_answers,
                time_taken
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                session["student_id"],
                game_id,
                score,
                correct,
                wrong,
                0
            )
        )

        # Add XP
        cursor.execute(
            """
            UPDATE student_xp
            SET total_xp = total_xp + %s
            WHERE student_id = %s
            """,
            (
                score,
                session["student_id"]
            )
        )

        # Read XP
        cursor.execute(
            """
            SELECT total_xp
            FROM student_xp
            WHERE student_id = %s
            """,
            (session["student_id"],)
        )

        xp_data = cursor.fetchone()

        if xp_data:

            total_xp = xp_data[0]

            new_level = (
                total_xp // 100
            ) + 1

            cursor.execute(
                """
                UPDATE student_xp
                SET current_level = %s
                WHERE student_id = %s
                """,
                (
                    new_level,
                    session["student_id"]
                )
            )
        update_student_rewards(
    cursor,
    session["student_id"]
)
        connection.commit()

        return {
            "success": True,
            "xp": score
        }

    except mysql.connector.Error as error:

        if connection:
            connection.rollback()

        print(
            "Animal Quiz Save Error:",
            error
        )

        return {
            "success": False,
            "message": "Could not save quiz."
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# =========================================================
# MEMORY SHARP
# =========================================================

@app.route("/games/memory")
def memory_game():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )


    class_name = session.get(
        "class_name",
        "Class 1"
    )


    # -----------------------------------------------------
    # Number of pairs based on class
    # -----------------------------------------------------

    try:

        class_number = int(
            class_name.replace(
                "Class ",
                ""
            )
        )

    except ValueError:

        class_number = 1


    if class_number <= 3:

        pair_count = 4

    elif class_number <= 5:

        pair_count = 5

    elif class_number <= 8:

        pair_count = 6

    else:

        pair_count = 8


    # -----------------------------------------------------
    # Memory values
    # -----------------------------------------------------

    memory_values = [

        "🍎",
        "🍌",
        "🍇",
        "🍉",
        "🍓",
        "🍊",
        "🥭",
        "🍍",
        "🥝",
        "🍒",
        "🥕",
        "🌽"
    ]


    selected_values = (
        memory_values[:pair_count]
    )


    cards = []


    card_id = 1


    for value in selected_values:

        # First card

        cards.append({
            "id": card_id,
            "value": value
        })

        card_id += 1


        # Matching card

        cards.append({
            "id": card_id,
            "value": value
        })

        card_id += 1


    # Shuffle cards

    random.shuffle(cards)


    return render_template(
        "games/memory.html",
        cards=cards,
        class_name=class_name
    )


# =========================================================
# SAVE MEMORY SCORE
# =========================================================

@app.route(
    "/games/memory/save",
    methods=["POST"]
)
def save_memory_score():

    if "student_id" not in session:

        return {
            "success": False,
            "message": "Login required"
        }, 401


    data = request.get_json()


    score = int(
        data.get("score", 0)
    )


    matched_pairs = int(
        data.get("matched_pairs", 0)
    )


    attempts = int(
        data.get("attempts", 0)
    )


    time_taken = int(
        data.get("time_taken", 0)
    )


    # Game ID 2 = Memory Cards

    game_id = 2


    connection = None

    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        # -------------------------------------------------
        # Save score
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO scores
            (
                student_id,
                game_id,
                score,
                correct_answers,
                wrong_answers,
                time_taken
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                session["student_id"],
                game_id,
                score,
                matched_pairs,
                attempts - matched_pairs,
                time_taken
            )
        )


        # -------------------------------------------------
        # Add XP
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE student_xp

            SET total_xp =
                total_xp + %s

            WHERE student_id = %s
            """,
            (
                score,
                session["student_id"]
            )
        )


        # -------------------------------------------------
        # Get current XP
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT total_xp
            FROM student_xp
            WHERE student_id = %s
            """,
            (
                session["student_id"],
            )
        )


        xp_result = cursor.fetchone()


        if xp_result:

            total_xp = xp_result[0]


            new_level = (
                total_xp // 100
            ) + 1


            cursor.execute(
                """
                UPDATE student_xp

                SET current_level = %s

                WHERE student_id = %s
                """,
                (
                    new_level,
                    session["student_id"]
                )
            )

        update_student_rewards(
        cursor,
    session["student_id"]
)
        connection.commit()


        return {
            "success": True,
            "xp": score
        }


    except mysql.connector.Error as error:

        if connection:

            connection.rollback()


        print(
            "Memory Score Error:",
            error
        )


        return {
            "success": False,
            "message": "Could not save score."
        }, 500


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()
# =========================================================
# PAINT & DRAWING
# =========================================================

@app.route("/drawing")
def drawing():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "drawing/drawing.html"
    )


# =========================================================
# SAVE DRAWING
# =========================================================

@app.route("/drawing/save", methods=["POST"])
def save_drawing():

    if "student_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({
                "success": False,
                "message": "No drawing data received."
            }), 400

        title = str(
            data.get(
                "title",
                "My Drawing"
            )
        ).strip()

        if not title:

            title = "My Drawing"

        drawing_data = data.get(
            "drawing_data",
            ""
        )

        if not drawing_data:

            return jsonify({
                "success": False,
                "message": "Drawing is empty."
            }), 400

        # Prevent very large drawings
        if len(drawing_data) > 5_000_000:

            return jsonify({
                "success": False,
                "message": "Drawing is too large."
            }), 400

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            # -------------------------------------------------
            # SAVE DRAWING
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO drawings
                (
                    student_id,
                    title,
                    drawing_type,
                    drawing_data,
                    score,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session["student_id"],
                    title,
                    "free_draw",
                    drawing_data,
                    0,
                    "saved"
                )
            )

            # -------------------------------------------------
            # CHECK STUDENT XP RECORD
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT total_xp
                FROM student_xp
                WHERE student_id = %s
                """,
                (
                    session["student_id"],
                )
            )

            xp_result = cursor.fetchone()

            # -------------------------------------------------
            # CREATE XP RECORD IF MISSING
            # -------------------------------------------------

            if not xp_result:

                cursor.execute(
                    """
                    INSERT INTO student_xp
                    (
                        student_id,
                        total_xp,
                        current_level
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        session["student_id"],
                        10,
                        1
                    )
                )

                total_xp = 10

            else:

                total_xp = int(
                    xp_result[0] or 0
                )

                total_xp += 10

                # -------------------------------------------------
                # CALCULATE LEVEL
                # -------------------------------------------------

                new_level = (
                    total_xp // 100
                ) + 1

                cursor.execute(
                    """
                    UPDATE student_xp

                    SET
                        total_xp = %s,
                        current_level = %s

                    WHERE student_id = %s
                    """,
                    (
                        total_xp,
                        new_level,
                        session["student_id"]
                    )
                )

            # -------------------------------------------------
            # UPDATE REWARDS
            # -------------------------------------------------

            try:

                update_student_rewards(
                    cursor,
                    session["student_id"]
                )

            except Exception as reward_error:

                print(
                    "Reward Update Warning:",
                    reward_error
                )

            connection.commit()

            return jsonify({
                "success": True,
                "message": "Drawing saved successfully!",
                "xp": 10,
                "total_xp": total_xp
            })

        except mysql.connector.Error as error:

            if connection:

                connection.rollback()

            print(
                "Drawing Save Database Error:",
                error
            )

            return jsonify({
                "success": False,
                "message": "Database error: " + str(error)
            }), 500

        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()

    except Exception as error:

        print(
            "Drawing Save Error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Unable to save drawing."
        }), 500


# =========================================================
# DRAWING DIAGRAMS
# =========================================================

@app.route("/drawing/diagrams")
def drawing_diagrams():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "drawing/drawing_diagrams.html"
    )


# =========================================================
# COLORING
# =========================================================

@app.route("/drawing/coloring")
def coloring():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "drawing/coloring.html"
    )
# =========================================================
# STUDY ZONE
# =========================================================

@app.route("/study")
def study():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "study/study.html",
        class_name=session.get(
            "class_name",
            "Class 1"
        ),
        education_level=session.get(
            "education_level",
            "primary"
        )
    )


# =========================================================
# MATHS
# =========================================================

@app.route("/study/maths")
def study_maths():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "study/maths.html",
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# SCIENCE
# =========================================================

@app.route("/study/science")
def study_science():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "study/science.html",
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# ENGLISH
# =========================================================

@app.route("/study/english")
def study_english():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "study/english.html",
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# SOCIAL STUDIES
# =========================================================

@app.route("/study/social")
def study_social():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "study/social.html",
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# GENERAL KNOWLEDGE
# =========================================================

@app.route("/study/gk")
def study_gk():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "study/gk.html",
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# COMPUTER SCIENCE
# =========================================================

@app.route("/study/computer")
def study_computer():

    if "student_id" not in session:

        flash("Please login first.")

        return redirect(
            url_for("login")
        )

    return render_template(
        "study/computer.html",
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )
# =========================================================
# VIDEO ZONE
# =========================================================

@app.route("/videos")
def videos():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    category = request.args.get("category", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if category:
        cursor.execute("""
            SELECT *
            FROM videos
            WHERE status = 'active'
              AND video_type = %s
            ORDER BY id DESC
        """, (category,))
    else:
        cursor.execute("""
            SELECT *
            FROM videos
            WHERE status = 'active'
            ORDER BY id DESC
        """)

    video_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "videos/videos.html",
        videos=video_list,
        selected_category=category,
        class_name=session.get("class_name", "Class 1")
    )


# =========================================================
# WATCH VIDEO
# =========================================================

@app.route("/videos/<int:video_id>")
def watch_video(video_id):

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM videos
        WHERE id = %s
          AND status = 'active'
    """, (video_id,))

    video = cursor.fetchone()

    cursor.close()
    connection.close()

    if not video:
        flash("Video not found.")
        return redirect(url_for("videos"))

    return render_template(
        "videos/watch.html",
        video=video,
        class_name=session.get("class_name", "Class 1")
    )


# =========================================================
# SAVE VIDEO PROGRESS
# =========================================================

@app.route("/videos/<int:video_id>/progress", methods=["POST"])
def save_video_progress(video_id):

    if "student_id" not in session:
        return {
            "success": False,
            "message": "Login required"
        }, 401

    data = request.get_json() or {}

    watched_seconds = int(
        data.get("watched_seconds", 0)
    )

    completed = bool(
        data.get("completed", False)
    )

    student_id = session["student_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Check whether history already exists
    cursor.execute("""
        SELECT id, completed
        FROM video_history
        WHERE student_id = %s
          AND video_id = %s
    """, (student_id, video_id))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE video_history
            SET watched_seconds = %s,
                completed = %s,
                watched_at = NOW()
            WHERE student_id = %s
              AND video_id = %s
        """, (
            watched_seconds,
            completed,
            student_id,
            video_id
        ))

    else:

        cursor.execute("""
            INSERT INTO video_history
            (
                student_id,
                video_id,
                watched_seconds,
                completed,
                watched_at
            )
            VALUES (%s, %s, %s, %s, NOW())
        """, (
            student_id,
            video_id,
            watched_seconds,
            completed
        ))

    # Give XP only when completing for first time
    xp_added = 0

    if completed and (
        not existing or not existing["completed"]
    ):

        xp_added = 10

        cursor.execute("""
            SELECT total_xp
            FROM student_xp
            WHERE student_id = %s
        """, (student_id,))

        xp_row = cursor.fetchone()

        if xp_row:

            new_xp = xp_row["total_xp"] + xp_added

            new_level = (new_xp // 100) + 1

            cursor.execute("""
                UPDATE student_xp
                SET total_xp = %s,
                    current_level = %s,
                    updated_at = NOW()
                WHERE student_id = %s
            """, (
                new_xp,
                new_level,
                student_id
            ))
    update_student_rewards( 
            cursor, 
           session["student_id"] 
)    
    connection.commit()

    cursor.close()
    connection.close()

    return {
        "success": True,
        "completed": completed,
        "xp_added": xp_added
    }
# =========================================================
# STORY WORLD
# =========================================================

@app.route("/stories")
def stories():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    category = request.args.get(
        "category",
        ""
    ).strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if category:

        cursor.execute("""
            SELECT *
            FROM stories
            WHERE status = 'active'
              AND category = %s
            ORDER BY id DESC
        """, (category,))

    else:

        cursor.execute("""
            SELECT *
            FROM stories
            WHERE status = 'active'
            ORDER BY id DESC
        """)

    story_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "stories/stories.html",
        stories=story_list,
        selected_category=category,
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# READ STORY
# =========================================================

@app.route("/stories/<int:story_id>")
def read_story(story_id):

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.*,
            sp.completed,
            sp.score,
            sp.started_at,
            sp.completed_at
        FROM stories s

        LEFT JOIN story_progress sp
            ON s.id = sp.story_id
            AND sp.student_id = %s

        WHERE s.id = %s
          AND s.status = 'active'
    """, (
        student_id,
        story_id
    ))

    story = cursor.fetchone()

    cursor.close()
    connection.close()

    if not story:

        flash("Story not found.")

        return redirect(
            url_for("stories")
        )

    return render_template(
        "stories/story.html",
        story=story,
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# START STORY
# =========================================================

@app.route(
    "/stories/<int:story_id>/start",
    methods=["POST"]
)
def start_story(story_id):

    if "student_id" not in session:

        return {
            "success": False,
            "message": "Login required"
        }, 401

    student_id = session["student_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT id
        FROM story_progress
        WHERE student_id = %s
          AND story_id = %s
    """, (
        student_id,
        story_id
    ))

    existing = cursor.fetchone()

    if not existing:

        cursor.execute("""
            INSERT INTO story_progress
            (
                student_id,
                story_id,
                completed,
                score,
                started_at
            )
            VALUES
            (%s, %s, 0, 0, NOW())
        """, (
            student_id,
            story_id
        ))

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "success": True
    }


# =========================================================
# COMPLETE STORY
# =========================================================

@app.route(
    "/stories/<int:story_id>/complete",
    methods=["POST"]
)
def complete_story(story_id):

    if "student_id" not in session:

        return {
            "success": False,
            "message": "Login required"
        }, 401

    student_id = session["student_id"]

    data = request.get_json() or {}

    score = int(
        data.get("score", 10)
    )

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            completed
        FROM story_progress
        WHERE student_id = %s
          AND story_id = %s
    """, (
        student_id,
        story_id
    ))

    existing = cursor.fetchone()

    xp_added = 0

    if existing:

        if not existing["completed"]:

            cursor.execute("""
                UPDATE story_progress
                SET completed = 1,
                    score = %s,
                    completed_at = NOW()
                WHERE student_id = %s
                  AND story_id = %s
            """, (
                score,
                student_id,
                story_id
            ))

            xp_added = 20

    else:

        cursor.execute("""
            INSERT INTO story_progress
            (
                student_id,
                story_id,
                completed,
                score,
                started_at,
                completed_at
            )
            VALUES
            (%s, %s, 1, %s, NOW(), NOW())
        """, (
            student_id,
            story_id,
            score
        ))

        xp_added = 20


    # Add XP only on first completion

    if xp_added > 0:

        cursor.execute("""
            SELECT total_xp
            FROM student_xp
            WHERE student_id = %s
        """, (student_id,))

        xp_row = cursor.fetchone()

        if xp_row:

            new_xp = (
                xp_row["total_xp"]
                + xp_added
            )

            new_level = (
                new_xp // 100
            ) + 1

            cursor.execute("""
                UPDATE student_xp
                SET total_xp = %s,
                    current_level = %s,
                    updated_at = NOW()
                WHERE student_id = %s
            """, (
                new_xp,
                new_level,
                student_id
            ))
    update_student_rewards(
    cursor,
    student_id
)
    connection.commit()

    cursor.close()
    connection.close()

    return {
        "success": True,
        "completed": True,
        "xp_added": xp_added
    }
# =========================================================
# DAILY TASKS
# =========================================================

@app.route("/tasks")
def tasks():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]
    class_id = session.get("class_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get tasks for student's class
    cursor.execute("""
        SELECT
            t.id,
            t.title,
            t.description,
            t.task_type,
            t.class_id,
            t.points,
            t.due_date,
            t.image_path,
            t.status,

            COALESCE(
                st.status,
                'pending'
            ) AS student_status,

            st.completed_at,
            st.score

        FROM tasks t

        LEFT JOIN student_tasks st
            ON t.id = st.task_id
            AND st.student_id = %s

        WHERE t.status = 'active'
          AND (
                t.class_id = %s
                OR t.class_id IS NULL
              )

        ORDER BY
            CASE
                WHEN COALESCE(
                    st.status,
                    'pending'
                ) = 'pending'
                THEN 0
                ELSE 1
            END,
            t.id DESC

    """, (
        student_id,
        class_id
    ))

    task_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "tasks/tasks.html",
        tasks=task_list,
        class_name=session.get(
            "class_name",
            "Class 1"
        )
    )


# =========================================================
# COMPLETE TASK
# =========================================================

@app.route(
    "/tasks/<int:task_id>/complete",
    methods=["POST"]
)
def complete_task(task_id):

    if "student_id" not in session:

        return {
            "success": False,
            "message": "Login required"
        }, 401

    student_id = session["student_id"]

    data = request.get_json() or {}

    score = int(
        data.get("score", 0)
    )

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Check task
    cursor.execute("""
        SELECT
            id,
            points,
            status
        FROM tasks
        WHERE id = %s
    """, (task_id,))

    task = cursor.fetchone()

    if not task:

        cursor.close()
        connection.close()

        return {
            "success": False,
            "message": "Task not found"
        }, 404

    # Check existing student task
    cursor.execute("""
        SELECT
            id,
            status
        FROM student_tasks
        WHERE student_id = %s
          AND task_id = %s
    """, (
        student_id,
        task_id
    ))

    existing = cursor.fetchone()

    xp_added = 0

    if existing:

        # Already completed
        if existing["status"] == "completed":

            cursor.close()
            connection.close()

            return {
                "success": True,
                "already_completed": True,
                "xp_added": 0,
                "message":
                    "Task already completed"
            }

        cursor.execute("""
            UPDATE student_tasks
            SET status = 'completed',
                completed_at = NOW(),
                score = %s
            WHERE student_id = %s
              AND task_id = %s
        """, (
            score,
            student_id,
            task_id
        ))

        xp_added = task["points"] or 10

    else:

        cursor.execute("""
            INSERT INTO student_tasks
            (
                student_id,
                task_id,
                status,
                completed_at,
                score
            )
            VALUES
            (%s, %s, 'completed', NOW(), %s)
        """, (
            student_id,
            task_id,
            score
        ))

        xp_added = task["points"] or 10


    # =====================================================
    # ADD XP
    # =====================================================

    cursor.execute("""
        SELECT total_xp
        FROM student_xp
        WHERE student_id = %s
    """, (student_id,))

    xp_row = cursor.fetchone()

    if xp_row:

        new_xp = (
            xp_row["total_xp"]
            + xp_added
        )

        new_level = (
            new_xp // 100
        ) + 1

        cursor.execute("""
            UPDATE student_xp
            SET total_xp = %s,
                current_level = %s,
                updated_at = NOW()
            WHERE student_id = %s
        """, (
            new_xp,
            new_level,
            student_id
        ))
    update_student_rewards(
    cursor,
    student_id
)
    connection.commit()

    cursor.close()
    connection.close()

    return {
        "success": True,
        "already_completed": False,
        "xp_added": xp_added
    }
# =========================================================
# PROGRESS & REWARDS
# =========================================================

@app.route("/progress")
def progress():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # =====================================================
    # XP INFORMATION
    # =====================================================

    cursor.execute("""
        SELECT
            total_xp,
            current_level,
            current_streak,
            longest_streak
        FROM student_xp
        WHERE student_id = %s
    """, (student_id,))

    xp = cursor.fetchone()

    if not xp:
        xp = {
            "total_xp": 0,
            "current_level": 1,
            "current_streak": 0,
            "longest_streak": 0
        }


    # =====================================================
    # BADGES
    # =====================================================

    cursor.execute("""
        SELECT
            b.id,
            b.badge_name,
            b.description,
            b.icon_path,
            b.required_xp,
            b.badge_type,
            sb.earned_at
        FROM badges b

        LEFT JOIN student_badges sb
            ON b.id = sb.badge_id
            AND sb.student_id = %s

        ORDER BY
            CASE
                WHEN sb.id IS NOT NULL THEN 0
                ELSE 1
            END,
            b.required_xp
    """, (student_id,))

    badges = cursor.fetchall()


    # =====================================================
    # GAME STATISTICS
    # =====================================================

    cursor.execute("""
        SELECT
            COUNT(*) AS games_played,
            COALESCE(SUM(score), 0) AS total_score,
            COALESCE(AVG(score), 0) AS average_score
        FROM scores
        WHERE student_id = %s
    """, (student_id,))

    game_stats = cursor.fetchone()


    # =====================================================
    # TASK STATISTICS
    # =====================================================

    cursor.execute("""
        SELECT
            COUNT(*) AS tasks_completed,
            COALESCE(SUM(score), 0) AS task_score
        FROM student_tasks
        WHERE student_id = %s
          AND status = 'completed'
    """, (student_id,))

    task_stats = cursor.fetchone()


    # =====================================================
    # VIDEO STATISTICS
    # =====================================================

    cursor.execute("""
        SELECT
            COUNT(*) AS videos_watched,
            COALESCE(
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS videos_completed
        FROM video_history
        WHERE student_id = %s
    """, (student_id,))

    video_stats = cursor.fetchone()


    # =====================================================
    # STORY STATISTICS
    # =====================================================

    cursor.execute("""
        SELECT
            COUNT(*) AS stories_started,
            COALESCE(
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS stories_completed
        FROM story_progress
        WHERE student_id = %s
    """, (student_id,))

    story_stats = cursor.fetchone()


    # =====================================================
    # DRAWING STATISTICS
    # =====================================================

    cursor.execute("""
        SELECT
            COUNT(*) AS drawings_created
        FROM drawings
        WHERE student_id = %s
    """, (student_id,))

    drawing_stats = cursor.fetchone()


    # =====================================================
    # SUBJECT PROGRESS
    # =====================================================

    cursor.execute("""
        SELECT
            subject,
            total_activities,
            completed_activities,
            total_score,
            average_score,
            last_activity_date
        FROM progress
        WHERE student_id = %s
        ORDER BY subject
    """, (student_id,))

    subject_progress = cursor.fetchall()


    # =====================================================
    # RECENT SCORES
    # =====================================================

    cursor.execute("""
        SELECT
            s.score,
            s.correct_answers,
            s.wrong_answers,
            s.time_taken,
            s.played_at,
            g.title AS game_title
        FROM scores s

        LEFT JOIN games g
            ON s.game_id = g.id

        WHERE s.student_id = %s

        ORDER BY s.played_at DESC

        LIMIT 10
    """, (student_id,))

    recent_scores = cursor.fetchall()


    cursor.close()
    connection.close()


    # =====================================================
    # LEVEL PROGRESS
    # =====================================================

    total_xp = xp["total_xp"]

    current_level = xp["current_level"]

    xp_for_current_level = (
        (current_level - 1) * 100
    )

    xp_in_level = (
        total_xp - xp_for_current_level
    )

    if xp_in_level < 0:
        xp_in_level = 0

    level_percentage = (
        xp_in_level
        / 100
    ) * 100

    if level_percentage > 100:
        level_percentage = 100


    return render_template(
        "progress/progress.html",
        xp=xp,
        badges=badges,
        game_stats=game_stats,
        task_stats=task_stats,
        video_stats=video_stats,
        story_stats=story_stats,
        drawing_stats=drawing_stats,
        subject_progress=subject_progress,
        recent_scores=recent_scores,
        level_percentage=level_percentage
    )
# =========================================================
# TEACHER PANEL
# =========================================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Total students
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM students
        WHERE role = 'student'
    """)

    student_count = cursor.fetchone()["total"]


    # Total questions
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM questions
    """)

    question_count = cursor.fetchone()["total"]


    # Total games
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM games
    """)

    game_count = cursor.fetchone()["total"]


    # Total stories
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM stories
        WHERE status = 'active'
    """)

    story_count = cursor.fetchone()["total"]


    # Total videos
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM videos
        WHERE status = 'active'
    """)

    video_count = cursor.fetchone()["total"]


    # Total tasks
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM tasks
        WHERE status = 'active'
    """)

    task_count = cursor.fetchone()["total"]


    cursor.close()
    connection.close()


    return render_template(
        "teacher/teacher_dashboard.html",
        student_count=student_count,
        question_count=question_count,
        game_count=game_count,
        story_count=story_count,
        video_count=video_count,
        task_count=task_count
    )
@app.route("/teacher/students")
def teacher_students():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    cursor.execute("""
        SELECT
            s.id,
            s.full_name,
            s.email,
            s.phone,
            s.city,
            s.status,
            c.class_name,

            COALESCE(
                x.total_xp,
                0
            ) AS total_xp,

            COALESCE(
                x.current_level,
                1
            ) AS current_level,

            COALESCE(
                x.current_streak,
                0
            ) AS current_streak

        FROM students s

        LEFT JOIN classes c
            ON s.class_id = c.id

        LEFT JOIN student_xp x
            ON s.id = x.student_id

        WHERE s.role = 'student'

        ORDER BY s.id DESC
    """)


    students = cursor.fetchall()


    cursor.close()
    connection.close()


    return render_template(
        "teacher/students.html",
        students=students
    )
@app.route("/teacher/questions")
def teacher_questions():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    cursor.execute("""
        SELECT
            q.id,
            q.question_text,
            q.correct_answer,
            q.points,
            q.difficulty,
            g.title AS game_title

        FROM questions q

        LEFT JOIN games g
            ON q.game_id = g.id

        ORDER BY q.id DESC
    """)


    questions = cursor.fetchall()


    cursor.close()
    connection.close()


    return render_template(
        "teacher/questions.html",
        questions=questions
    )
@app.route(
    "/teacher/questions/add",
    methods=["GET", "POST"]
)
def teacher_add_question():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))


    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    if request.method == "POST":

        game_id = request.form.get("game_id")

        question_text = request.form.get(
            "question_text"
        )

        option_a = request.form.get(
            "option_a"
        )

        option_b = request.form.get(
            "option_b"
        )

        option_c = request.form.get(
            "option_c"
        )

        option_d = request.form.get(
            "option_d"
        )

        correct_answer = request.form.get(
            "correct_answer"
        )

        explanation = request.form.get(
            "explanation"
        )

        points = request.form.get(
            "points",
            10
        )

        difficulty = request.form.get(
            "difficulty",
            "easy"
        )


        if not question_text:
            flash("Question is required.")

            cursor.close()
            connection.close()

            return redirect(
                url_for("teacher_add_question")
            )


        cursor.execute("""
            INSERT INTO questions
            (
                game_id,
                question_text,
                options_a,
                options_b,
                options_c,
                options_d,
                correct_answer,
                explanation,
                points,
                difficulty
            )

            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """, (
            game_id if game_id else None,
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer,
            explanation,
            int(points),
            difficulty
        ))


        connection.commit()

        cursor.close()
        connection.close()


        flash("Question added successfully!")

        return redirect(
            url_for("teacher_questions")
        )


    # Load games

    cursor.execute("""
        SELECT
            id,
            title,
            game_type
        FROM games
        ORDER BY title
    """)

    games = cursor.fetchall()


    cursor.close()
    connection.close()


    return render_template(
        "teacher/add_question.html",
        games=games
    )
# =========================================================
# TEACHER STORY MANAGEMENT
# =========================================================

@app.route("/teacher/stories")
def teacher_stories():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.id,
            s.title,
            s.category,
            s.reading_time,
            s.status,
            c.class_name
        FROM stories s
        LEFT JOIN classes c
            ON s.class_id = c.id
        ORDER BY s.id DESC
    """)

    stories = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "teacher/stories.html",
        stories=stories
    )
@app.route(
    "/teacher/stories/add",
    methods=["GET", "POST"]
)
def teacher_add_story():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        story_text = request.form.get("story_text")
        category = request.form.get("category")
        class_id = request.form.get("class_id")
        reading_time = request.form.get(
            "reading_time",
            5
        )

        cover_image = request.form.get(
            "cover_image"
        )

        if not title or not story_text:
            flash("Title and story content are required.")

            cursor.close()
            connection.close()

            return redirect(
                url_for("teacher_add_story")
            )

        cursor.execute("""
            INSERT INTO stories
            (
                title,
                description,
                story_text,
                cover_image,
                category,
                class_id,
                reading_time,
                status
            )
            VALUES
            (
                %s, %s, %s, %s,
                %s, %s, %s, 'active'
            )
        """, (
            title,
            description,
            story_text,
            cover_image,
            category,
            class_id if class_id else None,
            int(reading_time)
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash("Story added successfully!")

        return redirect(
            url_for("teacher_stories")
        )

    cursor.execute("""
        SELECT
            id,
            class_name
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "teacher/add_story.html",
        classes=classes
    )
# =========================================================
# TEACHER VIDEO MANAGEMENT
# =========================================================

@app.route("/teacher/videos")
def teacher_videos():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            v.id,
            v.title,
            v.category,
            v.video_type,
            v.duration_seconds,
            v.status,
            c.class_name
        FROM videos v
        LEFT JOIN classes c
            ON v.class_id = c.id
        ORDER BY v.id DESC
    """)

    videos = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "teacher/videos.html",
        videos=videos
    )
@app.route(
    "/teacher/videos/add",
    methods=["GET", "POST"]
)
def teacher_add_video():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        video_path = request.form.get("video_path")
        thumbnail_path = request.form.get(
            "thumbnail_path"
        )

        category = request.form.get("category")

        video_type = request.form.get(
            "video_type"
        )

        class_id = request.form.get("class_id")

        duration = request.form.get(
            "duration_seconds",
            0
        )


        if not title or not video_path:

            flash(
                "Title and video path are required."
            )

            cursor.close()
            connection.close()

            return redirect(
                url_for("teacher_add_video")
            )


        cursor.execute("""
            INSERT INTO videos
            (
                title,
                description,
                video_path,
                thumbnail_path,
                category,
                video_type,
                class_id,
                duration_seconds,
                status
            )
            VALUES
            (
                %s, %s, %s, %s,
                %s, %s, %s, %s, 'active'
            )
        """, (
            title,
            description,
            video_path,
            thumbnail_path,
            category,
            video_type,
            class_id if class_id else None,
            int(duration)
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash("Video added successfully!")

        return redirect(
            url_for("teacher_videos")
        )


    cursor.execute("""
        SELECT
            id,
            class_name
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "teacher/add_video.html",
        classes=classes
    )
# =========================================================
# TEACHER TASK MANAGEMENT
# =========================================================

@app.route("/teacher/tasks")
def teacher_tasks():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.id,
            t.title,
            t.description,
            t.task_type,
            t.points,
            t.due_date,
            t.status,
            c.class_name
        FROM tasks t
        LEFT JOIN classes c
            ON t.class_id = c.id
        ORDER BY t.id DESC
    """)

    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "teacher/tasks.html",
        tasks=tasks
    )
@app.route(
    "/teacher/tasks/add",
    methods=["GET", "POST"]
)
def teacher_add_task():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form.get("title")

        description = request.form.get(
            "description"
        )

        task_type = request.form.get(
            "task_type"
        )

        class_id = request.form.get(
            "class_id"
        )

        points = request.form.get(
            "points",
            10
        )

        due_date = request.form.get(
            "due_date"
        )


        if not title:

            flash("Task title is required.")

            cursor.close()
            connection.close()

            return redirect(
                url_for("teacher_add_task")
            )


        cursor.execute("""
            INSERT INTO tasks
            (
                title,
                description,
                task_type,
                class_id,
                points,
                due_date,
                status
            )
            VALUES
            (
                %s, %s, %s,
                %s, %s, %s,
                'active'
            )
        """, (
            title,
            description,
            task_type,
            class_id if class_id else None,
            int(points),
            due_date if due_date else None
        ))


        connection.commit()

        cursor.close()
        connection.close()


        flash("Task created successfully!")

        return redirect(
            url_for("teacher_tasks")
        )


    cursor.execute("""
        SELECT
            id,
            class_name
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    cursor.close()
    connection.close()


    return render_template(
        "teacher/add_task.html",
        classes=classes
    )
@app.route(
    "/teacher/stories/edit/<int:story_id>",
    methods=["GET", "POST"]
)
def teacher_edit_story(story_id):

    # =========================================================
    # TEACHER LOGIN CHECK
    # =========================================================

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))


    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)


    # =========================================================
    # POST - UPDATE STORY
    # =========================================================

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        story_text = request.form.get(
            "story_text",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        class_id = request.form.get(
            "class_id"
        )

        reading_time = request.form.get(
            "reading_time",
            5
        )


        # =====================================================
        # OLD COVER IMAGE
        # =====================================================

        cover_image = request.form.get(
            "old_cover_image",
            ""
        ).strip()


        # =====================================================
        # NEW COVER IMAGE
        # =====================================================

        image_file = request.files.get(
            "cover_file"
        )

        if image_file and image_file.filename:

            if not allowed_file(
                image_file.filename,
                ALLOWED_IMAGE_EXTENSIONS
            ):

                cursor.close()
                connection.close()

                flash(
                    "Invalid image format. "
                    "Use PNG, JPG, JPEG, GIF or WEBP."
                )

                return redirect(
                    url_for(
                        "teacher_edit_story",
                        story_id=story_id
                    )
                )


            # Secure filename
            filename = secure_filename(
                image_file.filename
            )


            # Unique filename
            unique_filename = (
                f"{story_id}_{filename}"
            )


            # Full physical path
            image_path = os.path.join(
                app.config["IMAGE_UPLOAD_FOLDER"],
                unique_filename
            )


            # Save image
            image_file.save(
                image_path
            )


            # Database path
            cover_image = (
                f"images/{unique_filename}"
            )


        # =====================================================
        # UPDATE DATABASE
        # =====================================================

        cursor.execute(
            """
            UPDATE stories
            SET
                title = %s,
                description = %s,
                story_text = %s,
                cover_image = %s,
                category = %s,
                class_id = %s,
                reading_time = %s
            WHERE id = %s
            """,
            (
                title,
                description,
                story_text,
                cover_image,
                category,
                class_id if class_id else None,
                reading_time,
                story_id
            )
        )


        connection.commit()


        # =====================================================
        # CLOSE DATABASE
        # =====================================================

        cursor.close()
        connection.close()


        flash(
            "Story updated successfully!"
        )


        return redirect(
            url_for("teacher_stories")
        )


    # =========================================================
    # GET - LOAD STORY
    # =========================================================

    cursor.execute(
        """
        SELECT *
        FROM stories
        WHERE id = %s
        """,
        (story_id,)
    )

    story = cursor.fetchone()


    # =========================================================
    # STORY NOT FOUND
    # =========================================================

    if not story:

        cursor.close()
        connection.close()

        flash(
            "Story not found."
        )

        return redirect(
            url_for("teacher_stories")
        )


    # =========================================================
    # LOAD CLASSES
    # =========================================================

    cursor.execute(
        """
        SELECT
            id,
            class_name
        FROM classes
        ORDER BY id
        """
    )

    classes = cursor.fetchall()


    # =========================================================
    # CLOSE DATABASE
    # =========================================================

    cursor.close()
    connection.close()


    # =========================================================
    # EDIT STORY PAGE
    # =========================================================

    return render_template(
        "teacher/edit_story.html",
        story=story,
        classes=classes
    )
@app.route("/teacher/stories/delete/<int:story_id>", methods=["POST"])
def teacher_delete_story(story_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM stories WHERE id=%s",
        (story_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash("Story deleted successfully!")

    return redirect(
        url_for("teacher_stories")
    )
@app.route("/teacher/videos/edit/<int:video_id>",
           methods=["GET", "POST"])
def teacher_edit_video(video_id):

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        video_type = request.form.get("video_type")
        class_id = request.form.get("class_id")
        duration_seconds = request.form.get(
            "duration_seconds",
            0
        )

        video_path = request.form.get(
            "old_video_path"
        )

        thumbnail_path = request.form.get(
            "old_thumbnail_path"
        )

        video_file = request.files.get(
            "video_file"
        )

        thumbnail_file = request.files.get(
            "thumbnail_file"
        )

        if video_file and video_file.filename:

            if allowed_file(
                video_file.filename,
                ALLOWED_VIDEO_EXTENSIONS
            ):

                filename = secure_filename(
                    video_file.filename
                )

                unique_filename = (
                    f"{video_id}_{filename}"
                )

                video_file.save(
                    os.path.join(
                        VIDEO_UPLOAD_FOLDER,
                        unique_filename
                    )
                )

                video_path = (
                    f"videos/{unique_filename}"
                )

        if thumbnail_file and thumbnail_file.filename:

            if allowed_file(
                thumbnail_file.filename,
                ALLOWED_IMAGE_EXTENSIONS
            ):

                filename = secure_filename(
                    thumbnail_file.filename
                )

                unique_filename = (
                    f"{video_id}_{filename}"
                )

                thumbnail_file.save(
                    os.path.join(
                        IMAGE_UPLOAD_FOLDER,
                        unique_filename
                    )
                )

                thumbnail_path = (
                    f"images/{unique_filename}"
                )

        cursor.execute("""
            UPDATE videos
            SET
                title=%s,
                description=%s,
                video_path=%s,
                thumbnail_path=%s,
                category=%s,
                video_type=%s,
                class_id=%s,
                duration_seconds=%s
            WHERE id=%s
        """, (
            title,
            description,
            video_path,
            thumbnail_path,
            category,
            video_type,
            class_id if class_id else None,
            duration_seconds,
            video_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash("Video updated successfully!")

        return redirect(
            url_for("teacher_videos")
        )

    cursor.execute(
        "SELECT * FROM videos WHERE id=%s",
        (video_id,)
    )

    video = cursor.fetchone()

    cursor.execute("""
        SELECT id, class_name
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    cursor.close()
    connection.close()

    if not video:
        flash("Video not found.")
        return redirect(url_for("teacher_videos"))

    return render_template(
        "teacher/edit_video.html",
        video=video,
        classes=classes
    )
@app.route("/teacher/videos/delete/<int:video_id>",
           methods=["POST"])
def teacher_delete_video(video_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM videos WHERE id=%s",
        (video_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash("Video deleted successfully!")

    return redirect(
        url_for("teacher_videos")
    )
@app.route("/teacher/tasks/edit/<int:task_id>",
           methods=["GET", "POST"])
def teacher_edit_task(task_id):

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        task_type = request.form.get("task_type")
        class_id = request.form.get("class_id")
        points = request.form.get("points", 10)
        due_date = request.form.get("due_date")

        cursor.execute("""
            UPDATE tasks
            SET
                title=%s,
                description=%s,
                task_type=%s,
                class_id=%s,
                points=%s,
                due_date=%s
            WHERE id=%s
        """, (
            title,
            description,
            task_type,
            class_id if class_id else None,
            points,
            due_date if due_date else None,
            task_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash("Task updated successfully!")

        return redirect(
            url_for("teacher_tasks")
        )

    cursor.execute(
        "SELECT * FROM tasks WHERE id=%s",
        (task_id,)
    )

    task = cursor.fetchone()

    cursor.execute("""
        SELECT id, class_name
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    cursor.close()
    connection.close()

    if not task:
        flash("Task not found.")
        return redirect(url_for("teacher_tasks"))

    return render_template(
        "teacher/edit_task.html",
        task=task,
        classes=classes
    )

@app.route("/teacher/tasks/delete/<int:task_id>",
           methods=["POST"])
def teacher_delete_task(task_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=%s",
        (task_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash("Task deleted successfully!")

    return redirect(
        url_for("teacher_tasks")
    )
@app.route("/teacher/students/<int:student_id>/progress")
def teacher_student_progress(student_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "teacher":
        flash("Teacher access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.id,
            s.full_name,
            s.email,
            s.city,
            c.class_name,
            c.education_level
        FROM students s
        LEFT JOIN classes c
            ON s.class_id = c.id
        WHERE s.id=%s
    """, (student_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        connection.close()

        flash("Student not found.")

        return redirect(
            url_for("teacher_students")
        )

    cursor.execute("""
        SELECT
            total_xp,
            current_level,
            current_streak,
            longest_streak,
            last_activity_date
        FROM student_xp
        WHERE student_id=%s
    """, (student_id,))

    xp = cursor.fetchone()

    cursor.execute("""
        SELECT
            COUNT(*) AS games_played,
            COALESCE(SUM(score), 0) AS total_score,
            COALESCE(AVG(score), 0) AS average_score
        FROM scores
        WHERE student_id=%s
    """, (student_id,))

    game_stats = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS completed_tasks
        FROM student_tasks
        WHERE student_id=%s
        AND status='completed'
    """, (student_id,))

    task_stats = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS completed_stories
        FROM story_progress
        WHERE student_id=%s
        AND completed=1
    """, (student_id,))

    story_stats = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS completed_videos
        FROM video_history
        WHERE student_id=%s
        AND completed=1
    """, (student_id,))

    video_stats = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS drawings
        FROM drawings
        WHERE student_id=%s
    """, (student_id,))

    drawing_stats = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS badges
        FROM student_badges
        WHERE student_id=%s
    """, (student_id,))

    badge_stats = cursor.fetchone()

    cursor.execute("""
        SELECT
            subject,
            total_activities,
            completed_activities,
            total_score,
            average_score
        FROM progress
        WHERE student_id=%s
        ORDER BY subject
    """, (student_id,))

    progress = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "teacher/student_progress.html",
        student=student,
        xp=xp,
        game_stats=game_stats,
        task_stats=task_stats,
        story_stats=story_stats,
        video_stats=video_stats,
        drawing_stats=drawing_stats,
        badge_stats=badge_stats,
        progress=progress
    )
@app.route("/admin-dashboard")
def admin_dashboard():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        flash("Admin access required.")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM students
        WHERE role='student'
    """)
    total_students = cursor.fetchone()["total_students"]

    cursor.execute("""
        SELECT COUNT(*) AS total_teachers
        FROM students
        WHERE role='teacher'
    """)
    total_teachers = cursor.fetchone()["total_teachers"]

    cursor.execute("SELECT COUNT(*) AS total_classes FROM classes")
    total_classes = cursor.fetchone()["total_classes"]

    cursor.execute("SELECT COUNT(*) AS total_games FROM games")
    total_games = cursor.fetchone()["total_games"]

    cursor.execute("SELECT COUNT(*) AS total_questions FROM questions")
    total_questions = cursor.fetchone()["total_questions"]

    cursor.execute("""
        SELECT COUNT(*) AS total_stories
        FROM stories
    """)
    total_stories = cursor.fetchone()["total_stories"]

    cursor.execute("""
        SELECT COUNT(*) AS total_videos
        FROM videos
    """)
    total_videos = cursor.fetchone()["total_videos"]

    cursor.execute("""
        SELECT COUNT(*) AS total_tasks
        FROM tasks
    """)
    total_tasks = cursor.fetchone()["total_tasks"]

    cursor.execute("""
        SELECT COUNT(*) AS total_badges
        FROM badges
    """)
    total_badges = cursor.fetchone()["total_badges"]

    cursor.close()
    connection.close()

    return render_template(
        "admin/admin_dashboard.html",
        total_students=total_students,
        total_teachers=total_teachers,
        total_classes=total_classes,
        total_games=total_games,
        total_questions=total_questions,
        total_stories=total_stories,
        total_videos=total_videos,
        total_tasks=total_tasks,
        total_badges=total_badges
    )
@app.route("/admin/students")
def admin_students():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        flash("Admin access required.")
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        cursor.execute("""
            SELECT
                s.id,
                s.full_name,
                s.email,
                s.phone,
                s.city,
                s.status,
                c.class_name
            FROM students s
            LEFT JOIN classes c
                ON s.class_id = c.id
            WHERE s.role='student'
            AND (
                s.full_name LIKE %s
                OR s.email LIKE %s
                OR s.phone LIKE %s
                OR s.city LIKE %s
            )
            ORDER BY s.id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                s.id,
                s.full_name,
                s.email,
                s.phone,
                s.city,
                s.status,
                c.class_name
            FROM students s
            LEFT JOIN classes c
                ON s.class_id = c.id
            WHERE s.role='student'
            ORDER BY s.id DESC
        """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/students.html",
        students=students,
        search=search
    )
@app.route(
    "/admin/students/status/<int:student_id>",
    methods=["POST"]
)
def admin_student_status(student_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        flash("Admin access required.")
        return redirect(url_for("dashboard"))

    status = request.form.get("status")

    if status not in ["active", "inactive"]:
        flash("Invalid status.")
        return redirect(url_for("admin_students"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE students
        SET status=%s
        WHERE id=%s
        AND role='student'
    """, (status, student_id))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Student status updated.")

    return redirect(url_for("admin_students"))

@app.route("/admin/teachers")
def admin_teachers():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        cursor.execute("""
            SELECT
                id,
                full_name,
                email,
                phone,
                city,
                status,
                created_at
            FROM students
            WHERE role='teacher'
            AND (
                full_name LIKE %s
                OR email LIKE %s
                OR phone LIKE %s
                OR city LIKE %s
            )
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                id,
                full_name,
                email,
                phone,
                city,
                status,
                created_at
            FROM students
            WHERE role='teacher'
            ORDER BY id DESC
        """)

    teachers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/teachers.html",
        teachers=teachers,
        search=search
    )
@app.route(
    "/admin/teachers/status/<int:teacher_id>",
    methods=["POST"]
)
def admin_teacher_status(teacher_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form.get("status")

    if status not in ["active", "inactive"]:
        flash("Invalid status.")
        return redirect(url_for("admin_teachers"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE students
        SET status=%s
        WHERE id=%s
        AND role='teacher'
    """, (status, teacher_id))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Teacher status updated.")

    return redirect(url_for("admin_teachers"))

@app.route("/admin/classes")
def admin_classes():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            class_name,
            education_level,
            description
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/classes.html",
        classes=classes
    )
@app.route("/admin/games")
def admin_games():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        cursor.execute("""
            SELECT
                id,
                title,
                game_type,
                difficulty,
                points,
                status
            FROM games
            WHERE title LIKE %s
               OR game_type LIKE %s
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                id,
                title,
                game_type,
                difficulty,
                points,
                status
            FROM games
            ORDER BY id DESC
        """)

    games = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/games.html",
        games=games,
        search=search
    )
@app.route(
    "/admin/games/status/<int:game_id>",
    methods=["POST"]
)
def admin_game_status(game_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form.get("status")

    if status not in ["active", "inactive"]:
        flash("Invalid status.")
        return redirect(url_for("admin_games"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE games
        SET status=%s
        WHERE id=%s
    """, (status, game_id))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Game status updated.")

@app.route(
    "/admin/games/delete/<int:game_id>",
    methods=["POST"]
)
def admin_delete_game(game_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM games WHERE id=%s",
        (game_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash("Game deleted.")

    return redirect(url_for("admin_games"))

@app.route("/admin/questions")
def admin_questions():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            q.id,
            q.question_text,
            q.correct_answer,
            q.points,
            q.difficulty,
            g.title AS game_title
        FROM questions q
        LEFT JOIN games g
            ON q.game_id = g.id
        ORDER BY q.id DESC
    """)

    questions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/questions.html",
        questions=questions
    )
@app.route("/admin/stories")
def admin_stories():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        cursor.execute("""
            SELECT
                s.id,
                s.title,
                s.category,
                s.reading_time,
                s.status,
                c.class_name
            FROM stories s
            LEFT JOIN classes c
                ON s.class_id = c.id
            WHERE s.title LIKE %s
               OR s.category LIKE %s
            ORDER BY s.id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                s.id,
                s.title,
                s.category,
                s.reading_time,
                s.status,
                c.class_name
            FROM stories s
            LEFT JOIN classes c
                ON s.class_id = c.id
            ORDER BY s.id DESC
        """)

    stories = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/stories.html",
        stories=stories,
        search=search
    )
@app.route(
    "/admin/stories/status/<int:story_id>",
    methods=["POST"]
)
def admin_story_status(story_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form.get("status")

    if status not in ["active", "inactive"]:
        flash("Invalid status.")
        return redirect(url_for("admin_stories"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE stories
        SET status=%s
        WHERE id=%s
    """, (status, story_id))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Story status updated.")

    return redirect(url_for("admin_stories"))
@app.route(
    "/admin/stories/delete/<int:story_id>",
    methods=["POST"]
)
def admin_delete_story(story_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM stories WHERE id=%s",
        (story_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash("Story deleted.")

    return redirect(url_for("admin_stories"))
@app.route("/admin/videos")
def admin_videos():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        cursor.execute("""
            SELECT
                v.id,
                v.title,
                v.category,
                v.video_type,
                v.duration_seconds,
                v.status,
                c.class_name
            FROM videos v
            LEFT JOIN classes c
                ON v.class_id = c.id
            WHERE v.title LIKE %s
               OR v.category LIKE %s
               OR v.video_type LIKE %s
            ORDER BY v.id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                v.id,
                v.title,
                v.category,
                v.video_type,
                v.duration_seconds,
                v.status,
                c.class_name
            FROM videos v
            LEFT JOIN classes c
                ON v.class_id = c.id
            ORDER BY v.id DESC
        """)

    videos = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/videos.html",
        videos=videos,
        search=search
    )

@app.route(
    "/admin/videos/status/<int:video_id>",
    methods=["POST"]
)
def admin_video_status(video_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form.get("status")

    if status not in ["active", "inactive"]:
        return redirect(url_for("admin_videos"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE videos
        SET status=%s
        WHERE id=%s
    """, (status, video_id))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Video status updated.")

    return redirect(url_for("admin_videos"))
@app.route(
    "/admin/videos/delete/<int:video_id>",
    methods=["POST"]
)
def admin_delete_video(video_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM videos WHERE id=%s",
        (video_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash("Video deleted.")

    return redirect(url_for("admin_videos"))
@app.route("/admin/tasks")
def admin_tasks():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "").strip()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if search:

        cursor.execute("""
            SELECT
                t.id,
                t.title,
                t.task_type,
                t.points,
                t.due_date,
                t.status,
                c.class_name
            FROM tasks t
            LEFT JOIN classes c
                ON t.class_id = c.id
            WHERE t.title LIKE %s
               OR t.task_type LIKE %s
            ORDER BY t.id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT
                t.id,
                t.title,
                t.task_type,
                t.points,
                t.due_date,
                t.status,
                c.class_name
            FROM tasks t
            LEFT JOIN classes c
                ON t.class_id = c.id
            ORDER BY t.id DESC
        """)

    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/tasks.html",
        tasks=tasks,
        search=search
    )

@app.route(
    "/admin/tasks/status/<int:task_id>",
    methods=["POST"]
)
def admin_task_status(task_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    status = request.form.get("status")

    if status not in ["active", "inactive"]:
        return redirect(url_for("admin_tasks"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status=%s
        WHERE id=%s
    """, (status, task_id))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Task status updated.")

    return redirect(url_for("admin_tasks"))
@app.route(
    "/admin/tasks/delete/<int:task_id>",
    methods=["POST"]
)
def admin_delete_task(task_id):

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=%s",
        (task_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    flash("Task deleted.")

    return redirect(url_for("admin_tasks"))

@app.route("/admin/badges")
def admin_badges():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            badge_name,
            description,
            required_xp,
            badge_type
        FROM badges
        ORDER BY required_xp
    """)

    badges = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/badges.html",
        badges=badges
    )
@app.route("/admin/reports")
def admin_reports():

    if "student_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COUNT(*) AS total_students
        FROM students
        WHERE role='student'
    """)
    students = cursor.fetchone()

    cursor.execute("""
        SELECT
            COALESCE(SUM(total_xp), 0) AS total_xp
        FROM student_xp
    """)
    xp = cursor.fetchone()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_games_played,
            COALESCE(AVG(score), 0) AS average_score
        FROM scores
    """)
    games = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS completed_tasks
        FROM student_tasks
        WHERE status='completed'
    """)
    tasks = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS completed_stories
        FROM story_progress
        WHERE completed=1
    """)
    stories = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS completed_videos
        FROM video_history
        WHERE completed=1
    """)
    videos = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "admin/reports.html",
        students=students,
        xp=xp,
        games=games,
        tasks=tasks,
        stories=stories,
        videos=videos
    )


# =========================================================
# STUDENT GAMES
# =========================================================

@app.route("/games")
def games():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM games
            ORDER BY id DESC
            """
        )

        game_list = cursor.fetchall()

        return render_template(
            "games.html",
            games=game_list
        )

    except mysql.connector.Error as error:

        flash(
            f"Database error: {error}"
        )

        return render_template(
            "games.html",
            games=[]
        )

    except Exception as error:

        flash(
            f"Error loading games: {error}"
        )

        return render_template(
            "games.html",
            games=[]
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route("/profile")
def profile():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.id,
            s.full_name,
            s.email,
            s.phone,
            s.city,
            s.profile_photo,
            s.role,
            s.status,
            c.class_name,
            c.education_level
        FROM students s
        LEFT JOIN classes c
            ON s.class_id = c.id
        WHERE s.id=%s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if not student:
        flash("Student profile not found.")
        return redirect(url_for("dashboard"))

    return render_template(
        "profile.html",
        student=student
    )
@app.route(
    "/profile/photo",
    methods=["POST"]
)
def upload_profile_photo():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]

    file = request.files.get("profile_photo")

    if not file or file.filename == "":
        flash("Please select a profile photo.")
        return redirect(url_for("profile"))

    if not allowed_file(
        file.filename,
        ALLOWED_IMAGE_EXTENSIONS
    ):
        flash(
            "Only JPG, JPEG, PNG, GIF and WEBP files are allowed."
        )
        return redirect(url_for("profile"))

    original_name = secure_filename(file.filename)

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    filename = (
        f"profile_{student_id}.{extension}"
    )

    save_path = os.path.join(
        PROFILE_UPLOAD_FOLDER,
        filename
    )

    file.save(save_path)

    db_path = f"profiles/{filename}"

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE students
        SET profile_photo=%s
        WHERE id=%s
    """, (
        db_path,
        student_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    flash("Profile photo updated successfully.")

    return redirect(
        url_for("profile")
    )
@app.route("/quiz")
def quiz():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]
    class_id = session.get("class_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            question_text,
            subject,
            question_image,
            option_a,
            option_b,
            option_c,
            option_d,
            points,
            difficulty
        FROM questions
        WHERE class_id=%s
        ORDER BY RAND()
        LIMIT 10
    """, (class_id,))

    questions = cursor.fetchall()

    cursor.close()
    connection.close()

    if not questions:
        flash(
            "No quiz questions are available "
            "for your class yet."
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "games/quiz.html",
        questions=questions
    )
@app.route(
    "/quiz/submit",
    methods=["POST"]
)
def submit_quiz():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    student_id = session["student_id"]
    class_id = session.get("class_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer,
            explanation,
            points
        FROM questions
        WHERE class_id=%s
        ORDER BY id
    """, (class_id,))

    questions = cursor.fetchall()

    score = 0
    correct_answers = 0
    wrong_answers = 0
    total_points = 0

    results = []

    for question in questions[:10]:

        question_id = question["id"]

        selected_answer = request.form.get(
            f"question_{question_id}"
        )

        correct_answer = (
            question["correct_answer"]
            or ""
        ).upper()

        points = question["points"] or 10

        total_points += points

        is_correct = (
            selected_answer
            and selected_answer.upper()
            == correct_answer
        )

        if is_correct:

            score += points
            correct_answers += 1

        else:

            wrong_answers += 1

        results.append({
            "question": question,
            "selected": selected_answer,
            "correct": correct_answer,
            "is_correct": is_correct
        })


    # --------------------------------
    # Save quiz score
    # --------------------------------

    game_id = 5

    cursor.execute("""
        INSERT INTO scores
        (
            student_id,
            game_id,
            score,
            correct_answers,
            wrong_answers,
            time_taken
        )
        VALUES
        (%s, %s, %s, %s, %s, %s)
    """, (
        student_id,
        game_id,
        score,
        correct_answers,
        wrong_answers,
        300
    ))


    # --------------------------------
    # Add XP
    # --------------------------------

    xp_to_add = score

    cursor.execute("""
        SELECT
            total_xp
        FROM student_xp
        WHERE student_id=%s
    """, (student_id,))

    xp_record = cursor.fetchone()

    if xp_record:

        old_xp = xp_record["total_xp"] or 0

        new_xp = old_xp + xp_to_add

        new_level = (
            new_xp // 100
        ) + 1

        cursor.execute("""
            UPDATE student_xp
            SET
                total_xp=%s,
                current_level=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE student_id=%s
        """, (
            new_xp,
            new_level,
            student_id
        ))

    else:

        new_xp = xp_to_add

        new_level = (
            new_xp // 100
        ) + 1

        cursor.execute("""
            INSERT INTO student_xp
            (
                student_id,
                total_xp,
                current_level,
                current_streak,
                longest_streak
            )
            VALUES
            (%s, %s, %s, 0, 0)
        """, (
            student_id,
            new_xp,
            new_level
        ))


    connection.commit()

    cursor.close()
    connection.close()


    return render_template(
        "games/quiz_result.html",
        score=score,
        total_points=total_points,
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        xp_earned=xp_to_add,
        results=results
    )
@app.route("/leaderboard")
def leaderboard():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    class_id = session.get("class_id")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.full_name,
            c.class_name,
            x.total_xp,
            x.current_level
        FROM student_xp x
        JOIN students s
            ON x.student_id=s.id
        LEFT JOIN classes c
            ON s.class_id=c.id
        WHERE s.status='active'
        AND (
            s.class_id=%s
            OR %s IS NULL
        )
        ORDER BY x.total_xp DESC
        LIMIT 20
    """, (
        class_id,
        class_id
    ))

    leaderboard_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard_data
    )
@app.route("/games/word-puzzle")
def word_puzzle():
    return render_template("games/word_puzzle.html")


@app.route("/games/number-sequence")
def number_sequence():
    return render_template("games/number_sequence.html")


@app.route("/games/brain-quiz")
def brain_quiz():
    return render_template("games/brain_quiz.html")


@app.route("/games/image-matching")
def image_matching():
    return render_template("games/image_matching.html")


@app.route("/games/animal-match")
def animal_match():
    return render_template("games/animal_match.html")


@app.route("/games/memory-cards")
def memory_cards():
    return render_template("games/memory_cards.html")


@app.route("/games/quick-calculation")
def quick_calculation():
    return render_template("games/quick_calculation.html")


@app.route(
    "/parent/register",
    methods=["GET", "POST"]
)
def parent_register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name"
        ).strip()

        email = request.form.get(
            "email"
        ).strip().lower()

        phone = request.form.get(
            "phone"
        ).strip()

        password = request.form.get(
            "password"
        )

        city = request.form.get(
            "city"
        ).strip()

        if not full_name or not email or not password:

            flash(
                "Please fill all required fields."
            )

            return redirect(
                url_for("parent_register")
            )

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM parents
            WHERE email=%s
        """, (email,))

        existing_parent = cursor.fetchone()

        if existing_parent:

            cursor.close()
            connection.close()

            flash(
                "Parent email already registered."
            )

            return redirect(
                url_for("parent_register")
            )

        hashed_password = generate_password_hash(
            password
        )

        cursor.execute("""
            INSERT INTO parents
            (
                full_name,
                email,
                phone,
                password,
                city
            )
            VALUES
            (%s, %s, %s, %s, %s)
        """, (
            full_name,
            email,
            phone,
            hashed_password,
            city
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Parent account created successfully."
        )

        return redirect(
            url_for("parent_login")
        )

    return render_template(
        "parent/register.html"
    )
@app.route(
    "/parent/login",
    methods=["GET", "POST"]
)
def parent_login():

    if request.method == "POST":

        email = request.form.get(
            "email"
        ).strip().lower()

        password = request.form.get(
            "password"
        )

        connection = get_db_connection()
        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM parents
            WHERE email=%s
            AND status='active'
        """, (email,))

        parent = cursor.fetchone()

        cursor.close()
        connection.close()

        if not parent:

            flash(
                "Invalid parent email or password."
            )

            return redirect(
                url_for("parent_login")
            )

        if not check_password_hash(
            parent["password"],
            password
        ):

            flash(
                "Invalid parent email or password."
            )

            return redirect(
                url_for("parent_login")
            )

        session["parent_id"] = parent["id"]
        session["parent_name"] = parent["full_name"]
        session["parent_email"] = parent["email"]

        return redirect(
            url_for("parent_dashboard")
        )

    return render_template(
        "parent/login.html"
    )
@app.route("/parent-dashboard")
def parent_dashboard():

    if "parent_id" not in session:
        flash("Please login as a parent.")
        return redirect(
            url_for("parent_login")
        )

    parent_id = session["parent_id"]

    connection = get_db_connection()
    cursor = connection.cursor(
        dictionary=True
    )

    # -----------------------------
    # Parent's children
    # -----------------------------

    cursor.execute("""
        SELECT
            s.id,
            s.full_name,
            s.email,
            s.profile_photo,
            c.class_name,
            c.education_level
        FROM parent_students ps

        JOIN students s
            ON ps.student_id=s.id

        LEFT JOIN classes c
            ON s.class_id=c.id

        WHERE ps.parent_id=%s
        AND s.status='active'

        ORDER BY s.full_name
    """, (parent_id,))

    children = cursor.fetchall()

    # -----------------------------
    # Selected child
    # -----------------------------

    selected_child_id = request.args.get(
        "child_id",
        type=int
    )

    if children and not selected_child_id:

        selected_child_id = children[0]["id"]

    child = None

    for item in children:

        if item["id"] == selected_child_id:

            child = item
            break

    if not child:

        cursor.close()
        connection.close()

        return render_template(
            "parent/dashboard.html",
            children=children,
            child=None,
            xp=None,
            badge_count=0,
            games_count=0,
            stories_count=0,
            videos_count=0,
            tasks_count=0,
            subject_progress=[],
            recent_activities=[]
        )

    # -----------------------------
    # XP
    # -----------------------------

    cursor.execute("""
        SELECT
            total_xp,
            current_level,
            current_streak,
            longest_streak
        FROM student_xp
        WHERE student_id=%s
    """, (selected_child_id,))

    xp = cursor.fetchone()

    if not xp:

        xp = {
            "total_xp": 0,
            "current_level": 1,
            "current_streak": 0,
            "longest_streak": 0
        }

    # -----------------------------
    # Badges
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*) AS badge_count
        FROM student_badges
        WHERE student_id=%s
    """, (selected_child_id,))

    badge_count = cursor.fetchone()[
        "badge_count"
    ]

    # -----------------------------
    # Games
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*) AS games_count
        FROM scores
        WHERE student_id=%s
    """, (selected_child_id,))

    games_count = cursor.fetchone()[
        "games_count"
    ]

    # -----------------------------
    # Stories
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*) AS stories_count
        FROM story_progress
        WHERE student_id=%s
        AND completed=1
    """, (selected_child_id,))

    stories_count = cursor.fetchone()[
        "stories_count"
    ]

    # -----------------------------
    # Videos
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*) AS videos_count
        FROM video_history
        WHERE student_id=%s
        AND completed=1
    """, (selected_child_id,))

    videos_count = cursor.fetchone()[
        "videos_count"
    ]

    # -----------------------------
    # Tasks
    # -----------------------------

    cursor.execute("""
        SELECT COUNT(*) AS tasks_count
        FROM student_tasks
        WHERE student_id=%s
        AND status='completed'
    """, (selected_child_id,))

    tasks_count = cursor.fetchone()[
        "tasks_count"
    ]

    # -----------------------------
    # Subject Progress
    # -----------------------------

    cursor.execute("""
        SELECT
            subject,
            total_activities,
            completed_activities,
            total_score,
            average_score
        FROM progress
        WHERE student_id=%s
        ORDER BY subject
    """, (selected_child_id,))

    subject_progress = cursor.fetchall()

    # -----------------------------
    # Recent games
    # -----------------------------

    cursor.execute("""
        SELECT
            sc.score,
            sc.played_at,
            g.title,
            g.game_type
        FROM scores sc
        LEFT JOIN games g
            ON sc.game_id=g.id
        WHERE sc.student_id=%s
        ORDER BY sc.played_at DESC
        LIMIT 5
    """, (selected_child_id,))

    recent_activities = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "parent/dashboard.html",
        children=children,
        child=child,
        xp=xp,
        badge_count=badge_count,
        games_count=games_count,
        stories_count=stories_count,
        videos_count=videos_count,
        tasks_count=tasks_count,
        subject_progress=subject_progress,
        recent_activities=recent_activities
    )
@app.route("/parent/logout")
def parent_logout():

    session.pop("parent_id", None)
    session.pop("parent_name", None)
    session.pop("parent_email", None)

    flash("Logged out successfully.")
    # Get logged-in parent's ID

    return redirect(
        url_for("parent_login")
    )
@app.route(
    "/parent/link-child",
    methods=["GET", "POST"]
)
def parent_link_child():

    if "parent_id" not in session:

        flash(
            "Please login as parent."
        )

        return redirect(
            url_for("parent_login")
        )

    if request.method == "POST":

        child_code = request.form.get(
            "child_code"
        ).strip().upper()

        relationship = request.form.get(
            "relationship"
        ).strip()

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Find child

        cursor.execute("""
            SELECT
                id,
                full_name,
                status
            FROM students
            WHERE child_code=%s
        """, (child_code,))

        child = cursor.fetchone()

        if not child:

            cursor.close()
            connection.close()

            flash(
                "Invalid child code."
            )

            return redirect(
                url_for("parent_link_child")
            )

        if child["status"] != "active":

            cursor.close()
            connection.close()

            flash(
                "This child account is inactive."
            )

            return redirect(
                url_for("parent_link_child")
            )

        # Check existing link

        cursor.execute("""
            SELECT id
            FROM parent_students
            WHERE parent_id=%s
            AND student_id=%s
        """, (
            session["parent_id"],
            child["id"]
        ))

        existing = cursor.fetchone()

        if existing:

            cursor.close()
            connection.close()

            flash(
                "This child is already linked."
            )

            return redirect(
                url_for("parent_dashboard")
            )

        # Create relationship

        cursor.execute("""
            INSERT INTO parent_students
            (
                parent_id,
                student_id,
                relationship
            )
            VALUES
            (%s, %s, %s)
        """, (
            session["parent_id"],
            child["id"],
            relationship
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            f"{child['full_name']} linked successfully!"
        )

        return redirect(
            url_for("parent_dashboard")
        )

    return render_template(
        "parent/link_child.html"
    )
@app.route("/parent/weekly-report")
def parent_weekly_report():

    if "parent_id" not in session:
        return redirect(
            url_for("parent_login")
        )

    child_id = request.args.get(
        "child_id",
        type=int
    )

    if not child_id:
        return redirect(
            url_for("parent_dashboard")
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    # Verify parent owns child

    cursor.execute("""
        SELECT
            s.id,
            s.full_name,
            s.child_code
        FROM parent_students ps
        JOIN students s
            ON ps.student_id=s.id
        WHERE ps.parent_id=%s
        AND ps.student_id=%s
    """, (
        session["parent_id"],
        child_id
    ))

    child = cursor.fetchone()

    if not child:

        cursor.close()
        connection.close()

        flash(
            "You are not linked to this child."
        )

        return redirect(
            url_for("parent_dashboard")
        )

    # Daily game activity

    cursor.execute("""
        SELECT
            DATE(played_at) AS activity_date,
            COUNT(*) AS games_played,
            COALESCE(SUM(score),0) AS score
        FROM scores
        WHERE student_id=%s
        AND played_at >= DATE_SUB(
            CURDATE(),
            INTERVAL 6 DAY
        )
        GROUP BY DATE(played_at)
        ORDER BY activity_date
    """, (child_id,))

    weekly_games = cursor.fetchall()

    # Completed tasks

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM student_tasks
        WHERE student_id=%s
        AND status='completed'
        AND completed_at >= DATE_SUB(
            NOW(),
            INTERVAL 7 DAY
        )
    """, (child_id,))

    weekly_tasks = cursor.fetchone()["total"]

    # Stories

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM story_progress
        WHERE student_id=%s
        AND completed=1
        AND completed_at >= DATE_SUB(
            NOW(),
            INTERVAL 7 DAY
        )
    """, (child_id,))

    weekly_stories = cursor.fetchone()["total"]

    # Videos

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM video_history
        WHERE student_id=%s
        AND completed=1
        AND watched_at >= DATE_SUB(
            NOW(),
            INTERVAL 7 DAY
        )
    """, (child_id,))

    weekly_videos = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "parent/weekly_report.html",
        child=child,
        weekly_games=weekly_games,
        weekly_tasks=weekly_tasks,
        weekly_stories=weekly_stories,
        weekly_videos=weekly_videos
    )
@app.route("/parent/download-report")
def parent_download_report():

    if "parent_id" not in session:

        return redirect(
            url_for("parent_login")
        )

    child_id = request.args.get(
        "child_id",
        type=int
    )

    if not child_id:

        return redirect(
            url_for("parent_dashboard")
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    # Verify relationship

    cursor.execute("""
        SELECT
            s.id,
            s.full_name,
            s.email,
            s.child_code,
            c.class_name,
            c.education_level
        FROM parent_students ps

        JOIN students s
            ON ps.student_id=s.id

        LEFT JOIN classes c
            ON s.class_id=c.id

        WHERE ps.parent_id=%s
        AND ps.student_id=%s
    """, (
        session["parent_id"],
        child_id
    ))

    child = cursor.fetchone()

    if not child:

        cursor.close()
        connection.close()

        flash(
            "Child not linked to this parent."
        )

        return redirect(
            url_for("parent_dashboard")
        )

    # XP

    cursor.execute("""
        SELECT
            total_xp,
            current_level,
            current_streak,
            longest_streak
        FROM student_xp
        WHERE student_id=%s
    """, (child_id,))

    xp = cursor.fetchone()

    # Badges

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM student_badges
        WHERE student_id=%s
    """, (child_id,))

    badges = cursor.fetchone()["total"]

    # Games

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM scores
        WHERE student_id=%s
    """, (child_id,))

    games = cursor.fetchone()["total"]

    # Tasks

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM student_tasks
        WHERE student_id=%s
        AND status='completed'
    """, (child_id,))

    tasks = cursor.fetchone()["total"]

    # Stories

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM story_progress
        WHERE student_id=%s
        AND completed=1
    """, (child_id,))

    stories = cursor.fetchone()["total"]

    # Videos

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM video_history
        WHERE student_id=%s
        AND completed=1
    """, (child_id,))

    videos = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    # -----------------------------
    # Create PDF
    # -----------------------------

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    y = height - 30 * mm

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawString(
        20 * mm,
        y,
        "BrainQuest Kids"
    )

    y -= 12 * mm

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        20 * mm,
        y,
        "Student Learning Report"
    )

    y -= 15 * mm

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        20 * mm,
        y,
        f"Student: {child['full_name']}"
    )

    y -= 7 * mm

    pdf.drawString(
        20 * mm,
        y,
        f"Class: {child['class_name'] or 'N/A'}"
    )

    y -= 7 * mm

    pdf.drawString(
        20 * mm,
        y,
        f"Education Level: "
        f"{child['education_level'] or 'N/A'}"
    )

    y -= 7 * mm

    pdf.drawString(
        20 * mm,
        y,
        f"Child Code: "
        f"{child['child_code'] or 'N/A'}"
    )

    y -= 15 * mm

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        20 * mm,
        y,
        "Learning Summary"
    )

    y -= 10 * mm

    pdf.setFont(
        "Helvetica",
        11
    )

    summary = [
        f"Total XP: {xp['total_xp'] if xp else 0}",
        f"Current Level: {xp['current_level'] if xp else 1}",
        f"Current Streak: {xp['current_streak'] if xp else 0} days",
        f"Longest Streak: {xp['longest_streak'] if xp else 0} days",
        f"Badges Earned: {badges}",
        f"Games Played: {games}",
        f"Tasks Completed: {tasks}",
        f"Stories Completed: {stories}",
        f"Videos Completed: {videos}"
    ]

    for line in summary:

        pdf.drawString(
            25 * mm,
            y,
            line
        )

        y -= 7 * mm

    y -= 10 * mm

    pdf.setFont(
        "Helvetica-Oblique",
        10
    )

    pdf.drawString(
        20 * mm,
        y,
        "Generated by BrainQuest Kids"
    )

    pdf.save()

    buffer.seek(0)

    from flask import send_file

    return send_file(
        buffer,
        as_attachment=True,
        download_name=(
            f"{child['full_name']}_"
            "BrainQuest_Report.pdf"
        ),
        mimetype="application/pdf"
    )
@app.route("/parent/notifications")
def parent_notifications():

    if "parent_id" not in session:
        return redirect(
            url_for("parent_login")
        )

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            pn.*,
            s.full_name AS student_name
        FROM parent_notifications pn

        LEFT JOIN students s
            ON pn.student_id=s.id

        WHERE pn.parent_id=%s

        ORDER BY pn.created_at DESC

        LIMIT 50
    """, (
        session["parent_id"],
    ))

    notifications = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "parent/notifications.html",
        notifications=notifications
    )
@app.route(
    "/parent/notifications/read/<int:notification_id>",
    methods=["POST"]
)
def mark_parent_notification_read(
    notification_id
):

    if "parent_id" not in session:
        return redirect(
            url_for("parent_login")
        )

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE parent_notifications

        SET is_read=TRUE

        WHERE id=%s
        AND parent_id=%s
    """, (
        notification_id,
        session["parent_id"]
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(
        url_for("parent_notifications")
    )
@app.route("/parent/api/weekly-activity")
def parent_weekly_activity():

    if "parent_id" not in session:
        return jsonify({
            "error": "Login required"
        }), 401

    child_id = request.args.get(
        "child_id",
        type=int
    )

    if not child_id:
        return jsonify({
            "error": "Child ID required"
        }), 400

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT id
        FROM parent_students
        WHERE parent_id=%s
        AND student_id=%s
    """, (
        session["parent_id"],
        child_id
    ))

    linked = cursor.fetchone()

    if not linked:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Unauthorized"
        }), 403

    cursor.execute("""
        SELECT
            DATE(played_at) AS activity_date,
            COUNT(*) AS games,
            COALESCE(SUM(score),0) AS score
        FROM scores
        WHERE student_id=%s
        AND played_at >= DATE_SUB(
            CURDATE(),
            INTERVAL 6 DAY
        )
        GROUP BY DATE(played_at)
        ORDER BY activity_date
    """, (child_id,))

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify([
        {
            "date": str(row["activity_date"]),
            "games": row["games"],
            "score": row["score"]
        }
        for row in rows
    ])
def create_parent_notification(
    student_id,
    title,
    message,
    notification_type="achievement"
):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT parent_id
        FROM parent_students
        WHERE student_id=%s
    """, (student_id,))

    parents = cursor.fetchall()

    for parent in parents:

        cursor.execute("""
            INSERT INTO parent_notifications
            (
                parent_id,
                student_id,
                title,
                message,
                notification_type
            )
            VALUES
            (%s, %s, %s, %s, %s)
        """, (
            parent[0],
            student_id,
            title,
            message,
            notification_type
        ))

    connection.commit()

    cursor.close()
    connection.close()
# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )