import sqlite3

def init_db():
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    
    # Kateqoriyalar cədvəli
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Tədbirlər cədvəli
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    """)
    
    # İstifadəçilər / İştirakçılar cədvəli
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    
    # Qeydiyyatlar cədvəli (Eyni istifadəçinin eyni tədbirə təkrar qeydiyyatının qarşısını almaq üçün UNIQUE constraint)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            participant_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES events (id),
            FOREIGN KEY (participant_id) REFERENCES participants (id),
            UNIQUE(event_id, participant_id)
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()