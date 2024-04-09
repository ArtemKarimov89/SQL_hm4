from pprint import pprint

import psycopg2
from pprint import pprint

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
        conn.close()

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
        conn.close()
        print(f'Пользователь {name} {surname} создан в базе')

    def phone_add(self, email, phone):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT person_id FROM person_info pi2 
                        WHERE pi2.email = %s;
                    """, (email,))
                person_id = cur.fetchone()
                if person_id is None:
                    print(f'Пользователь с email {email} не найден в базе')
                    return
                cur.execute("""
                        INSERT INTO person_phone(person_id, phone_number)
                            VALUES (%s, %s);
                        """, (person_id[0], phone))
        conn.close()
        print(f'Для пользователя с email {email} добавлен телефон {phone} в базу')

    def update_info(self, email, info_for_update):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT person_id FROM person_info pi2 
                                WHERE pi2.email = %s;
                            """, (email,))
                person_id = cur.fetchone()
                if person_id is None:
                    print(f'Пользователь с email {email} не найден в базе')
                    return
                for key, value in info_for_update.items():
                    if key == 'phone_number':
                        cur.execute(f'UPDATE person_phone SET {key} = %s WHERE person_id = %s AND phone_number '
                                    f'= %s;',
                                    (value[0], person_id[0], value[1]))
                    else:
                        cur.execute(f'UPDATE person_info SET {key} = %s WHERE person_id = %s;', (value, person_id[0]))
        conn.close()
        print('Данные обновлены')

    def phone_del(self, email, phone):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT person_id FROM person_info pi2 
                            WHERE pi2.email = %s;
                            """, (email,))
                person_id = cur.fetchone()
                if person_id is None:
                    print(f'Пользователь с email {email} не найден в базе')
                    return
                cur.execute("""
                        DELETE FROM person_phone WHERE person_id = %s AND phone_number = %s;
                        """, (person_id[0], phone))
        conn.close()
        print(f'У пользователя с email {email} удален телефон {phone} из базы')

    def delete_person(self, email):
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                     DELETE FROM person_info WHERE email = %s RETURNING person_name;
                     """, (email,))
                person_name = cur.fetchone()
                if person_name is None:
                    print(f'Пользователь с email {email} не найден в базе')
                    conn.close()
                    return
        conn.close()
        print(f'Пользователь {person_name[0]} удален из базы')

    def find_persons(self, name='', surname='', email='', phone=''):
        params = []
        with psycopg2.connect(database=self.name_db, user=self.user_db, password=self.pass_db) as conn:
            with conn.cursor() as cur:
                if name != '':
                    condition = 'person_name = %s'
                    params.append(name)
                if surname != '':
                    if condition != '':
                        condition = condition + ' AND person_surname = %s'
                    else:
                        condition = 'person_surname = %s'
                    params.append(surname)
                if email != '':
                    if condition != '':
                        condition = condition + ' AND email = %s'
                    else:
                        condition = 'email = %s'
                    params.append(email)
                if phone != '':
                    if condition != '':
                        condition = condition + ' AND pp.phone_number = %s'
                    else:
                        condition = 'pp.phone_number = %s'
                    params.append(phone)
                if len(params) == 1:
                    tuple_params = (params[0], )
                else:
                    tuple_params = (params[0::])
                cur.execute(f'SELECT person_name, person_surname, email, phone_number FROM person_info pi2'
                            f' LEFT JOIN person_phone pp ON pi2.person_id = pp.person_id'
                            f' WHERE {condition}',
                            tuple_params)
                find_persons = cur.fetchall()
                if find_persons is None:
                    print(f'Пользователь не найден в базе')
                    conn.close()
                    return
        conn.close()
        pprint(f'Результат поиска: {find_persons}')
        return find_persons


if __name__ == '__main__':
    person_info = PersonInfo()
    person_info.create_db()
    person_info.create_person('Serj', 'Dari', 'Dari_S@gmail.com', '+97867565676')
    person_info.phone_add('Dari_S@gmail.com', '+865456789')

    new_info_dict = {'person_name': 'Modey',
                     'person_surname': 'Darja',
                     'phone_number': ['+97867561111', '+97867565676']}
    person_info.update_info('Dari_S@gmail.com', new_info_dict)
    person_info.phone_del('Dari_S@gmail.com', '+865456789')
    person_info.create_person('Ben', 'Mendel', 'B_M@gmail.com', '+5266626466')
    person_info.create_person('Ben', 'Anderson', 'B_A@gmail.com', '+5266326466')
    person_info.create_person('Ben', 'Karter', 'B_K@gmail.com', '+9266326466')
    person_info.create_person('Ben', 'Mendel', 'B_M2@gmail.com', '+7266326466')
    person_info.delete_person('Dari_S@gmail.com')
    find_person_info = person_info.find_persons('Ben', 'Mendel')
