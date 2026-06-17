import os
import time
import csv
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = Path(__file__).resolve().parent / "ratings.csv"


def get_db_url() -> str:
    return os.getenv("DATABASE_URL") or \
        "postgresql://postgres:postgres@movie-postgres:5432/postgres"


def load_csv_rows():
    """Đọc ratings.csv -> list[(user_id, movie_id, score, created_at)]."""
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                user_id = int(r["userId"])
                movie_id = int(r["movieId"])
                score = float(r["rating"])
                # timestamp (epoch giây) -> để None nếu thiếu; Postgres sẽ nhận to_timestamp ở SQL
                ts = r.get("timestamp")
                ts = int(ts) if ts not in (None, "") else None
            except (KeyError, ValueError):
                continue
            rows.append((user_id, movie_id, score, ts))
    return rows


def main():
    start = time.time()

    if not CSV_PATH.exists():
        print(f"[SKIP] ratings.csv không tồn tại tại {CSV_PATH}")
        return

    rows = load_csv_rows()
    if not rows:
        print("[SKIP] ratings.csv rỗng hoặc không hợp lệ.")
        return
    print(f"Đã đọc {len(rows)} dòng từ ratings.csv")

    conn = psycopg2.connect(get_db_url())
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # 1) Tạo users (idempotent) - chỉ những user_id xuất hiện trong CSV.
            user_ids = sorted({r[0] for r in rows})
            user_values = [
                (uid, f"ml_user_{uid}", f"MovieLens User {uid}", f"ml_user_{uid}@example.com")
                for uid in user_ids
            ]
            execute_values(
                cur,
                """
                INSERT INTO users (id, user_name, full_name, email, is_deleted, joined_date, role)
                VALUES %s
                ON CONFLICT (id) DO NOTHING
                """,
                [(uid, un, fn, em, False, "USER") for (uid, un, fn, em) in user_values],
                template="(%s, %s, %s, %s, %s, now(), %s)",
                page_size=1000,
            )

            print(f"Đã đảm bảo {len(user_values)} users tồn tại.")

            # 2) Nạp ratings vào bảng tạm để lọc theo mediacontent + chống trùng.
            cur.execute("""
                CREATE TEMP TABLE tmp_ratings (
                    user_id BIGINT,
                    movie_id BIGINT,
                    score DOUBLE PRECISION,
                    ts BIGINT
                ) ON COMMIT DROP
            """)
            execute_values(
                cur,
                "INSERT INTO tmp_ratings (user_id, movie_id, score, ts) VALUES %s",
                rows,
                page_size=5000,
            )

            # 3) Chèn vào ratings: chỉ giữ movie có thật trong mediacontent,
            #    và bỏ qua cặp (user, movie) đã tồn tại để chạy lại không nhân đôi.
            cur.execute("""
                INSERT INTO ratings (user_id, mediacontent_id, score, created_at)
                SELECT t.user_id, t.movie_id, t.score,
                       CASE WHEN t.ts IS NOT NULL THEN to_timestamp(t.ts) ELSE now() END
                FROM tmp_ratings t
                JOIN mediacontent mc ON mc.media_content_id = t.movie_id
                WHERE NOT EXISTS (
                    SELECT 1 FROM ratings r
                    WHERE r.user_id = t.user_id
                      AND r.mediacontent_id = t.movie_id
                )
            """)
            inserted = cur.rowcount
            print(f"Đã chèn {inserted} ratings (đã lọc theo mediacontent + chống trùng).")

            # 4) Đồng bộ lại identity sequence của users để app không cấp trùng id.
            cur.execute("""
                SELECT setval(
                    pg_get_serial_sequence('users', 'id'),
                    (SELECT GREATEST(MAX(id), 1) FROM users)
                )
            """)

        conn.commit()
        duration = time.time() - start
        print(f"=== Import ratings hoàn tất trong {duration:.2f}s ===")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Import ratings thất bại, đã rollback: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
