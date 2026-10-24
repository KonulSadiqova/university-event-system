import sqlite3

class DatabaseManager:
    """Verilənlər bazası əlaqələrini idarə edən sinif (Single Responsibility prinsipi)."""
    def __init__(self, db_name="events.db"):
        self.db_name = db_name

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_query(self, query, params=()):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data


class EventManager:
    """Tədbirlərin idarə olunması üçün sinif."""
    def __init__(self, db_manager):
        self.db = db_manager

    def add_event(self, title, description, category_id, date, time, location, capacity):
        query = """
            INSERT INTO events (title, description, category_id, date, time, location, capacity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute_query(query, (title, description, category_id, date, time, location, capacity))

    def get_all_events(self):
        query = """
            e.id, e.title, e.description, c.name as category, e.date, e.time, e.location, e.capacity
            FROM events e
            LEFT JOIN categories c ON e.category_id = c.id
        """
        return self.db.fetch_query(f"SELECT {query}")


class RegistrationManager:
    """İştirakçı qeydiyyatlarını idarə edən sinif."""
    def __init__(self, db_manager):
        self.db = db_manager

    def register_participant(self, event_id, full_name, email):
        # Əvvəlcə iştirakçının bazada olub- olmadığını yoxlayaq, yoxdursa əlavə edək
        participant = self.db.fetch_query("SELECT id FROM participants WHERE email = ?", (email,))
        
        if participant:
            participant_id = participant[0][0]
        else:
            self.db.execute_query("INSERT INTO participants (full_name, email) VALUES (?, ?)", (full_name, email))
            res = self.db.fetch_query("SELECT id FROM participants WHERE email = ?", (email,))
            participant_id = res[0][0]

        # Tədbirin limitini və təkrar qeydiyyatı yoxlayaraq qeydiyyatı edək
        try:
            self.db.execute_query(
                "INSERT INTO registrations (event_id, participant_id) VALUES (?, ?)",
                (event_id, participant_id)
            )
            return True, "Qeydiyyat uğurla tamamlandı!"
        except sqlite3.IntegrityError:
            return False, "Xəta: Bu e-poçt ilə artıq həmin tədbirə qeydiyyatdan keçilib!"