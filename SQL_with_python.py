import psycopg2

class PersonInfo:

    def __init__(self):
        print('Input DataBase name:')
        self.name_db = input()
        print('Input username:')
        self.user_db = input()
        print('Input password:')
        self.pass_db = int(input())

    def create_db(self):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DROP TABLE person_info CASCADE;
                    DROP TABLE person_phone CASCADE;
                    """)
                cur.execute("""
                        CREATE TABLE IF NOT EXISTS person_info(
                            person_id SERIAL PRIMARY KEY,
                            person_name VARCHAR(50) NOT NULL,
                            person_surname VARCHAR(60) NOT NULL,
                            email VARCHAR(100),
                            UNIQUE NULLS NOT DISTINCT(email)
                        );
                        """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS person_phone(
                        phone_id SERIAL PRIMARY KEY,
                        person_id INTEGER NOT NULL,
                        phone_number VARCHAR(15),
                        FOREIGN KEY (person_id) REFERENCES person_info(person_id) ON DELETE CASCADE,
                        UNIQUE NULLS NOT DISTINCT (phone_number)
                     );
                    """)
                conn.commit()

    def create_person(self, name, surname, email, phone=''):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO person_info(person_name, person_surname, email)
                    VALUES (%s, %s, %s) RETURNING person_id;
                    """, (name, surname, email))
                person_id = cur.fetchone()[0]
                if phone != '':
                    cur.execute("""
                        INSERT INTO person_phone(person_id, phone_number)
                        VALUES (%s, %s);
                        """, (person_id, phone))
                conn.commit()
        print(f'Пользователь {name} {surname} создан в базе')

    def phone_add(self, email, phone):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT person_id FROM person_info pi2 
                    WHERE pi2.email = %s;
                    """, (email, ))
                person_id = cur.fetchone()
                if person_id is None:
                    print(f'Пользователь с email {email} не найден в базе')
                    return
                cur.execute("""
                        INSERT INTO person_phone(person_id, phone_number)
                        VALUES (%s, %s);
                        """, (person_id[0], phone))
                conn.commit()
        print(f'Для пользователя с email {email} добавлен телефон {phone} в базу')

    def update_surname(self, email, surname):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                     UPDATE person_info SET person_surname = %s WHERE email = %s;
                     """, (surname, email))
        print(f'Фамилия пользователя изменена на {surname}')

    def phone_del(self, email, phone):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT person_id FROM person_info pi2 
                    WHERE pi2.email = %s;
                    """, (email, ))
                person_id = cur.fetchone()
                if person_id is None:
                    print(f'Пользователь с email {email} не найден в базе')
                    return
                cur.execute("""
                        DELETE FROM person_phone WHERE person_id = %s AND phone_number = %s;
                        """, (person_id[0], phone))
                conn.commit()
        print(f'У пользователя с email {email} удален телефон {phone} из базы')

    def delete_person(self, email):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                     DELETE FROM person_info WHERE email = %s RETURNING person_name;
                     """, (email, ))
                person_name = cur.fetchone()
                if person_name is None:
                    print(f'Пользователь с email {email} не найден в базе')
                    return
        print(f'Пользователь {person_name[0]} удален из базы')

    def find_person_phone(self, name, surname, phone):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT person_name, person_surname, email, phone_number FROM person_info pi2 
                    LEFT JOIN person_phone pp ON pi2.person_id = pp.person_id 
                    WHERE person_name = %s AND person_surname = %s AND pp.phone_number = %s
                    """, (name, surname, phone))
                find_person = cur.fetchone()
                if find_person is None:
                    print(f'Пользователь {name} {surname} не найден в базе')
                    return
        print(find_person)
        return find_person


if __name__ == '__main__':
    person_info = PersonInfo()
    person_info.create_db()
    person_info.create_person('Serj', 'Dari', 'Dari_S@gmail.com', '+97867565676')
    person_info.phone_add('Dari_S@gmail.com', '+865456789')
    person_info.update_surname('Dari_S@gmail.com', 'Darja')
    person_info.phone_del('Dari_S@gmail.com', '+865456789')
    person_info.create_person('Ben', 'Mendel', 'B_M@gmail.com', '+5266626466')
    person_info.delete_person('Dari_S@gmail.com')
    find_person_info = person_info.find_person_phone('Ben', 'Mendel', '+5266626466')
