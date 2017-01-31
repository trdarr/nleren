from psycopg2 import ProgrammingError

class UserService:
  def __init__(self, connection):
    self.connection = connection

  def create(self, google_user_id, name, email):
    with self.connection.cursor() as cursor:
      parameters = {
          'google_user_id': google_user_id,
          'name': name,
          'email': email}

      cursor.execute('''
          insert into users (google_user_id, name, email)
          values (%(google_user_id)s, %(name)s, %(email)s)
          on conflict (google_user_id) do update set
          name = %(name)s, email = %(email)s
          returning user_id
          ''', parameters)
      self.connection.commit()
      return cursor.fetchone()['user_id']

  def create_session(self, user_id):
    with self.connection.cursor() as cursor:
      cursor.execute('''
          insert into sessions (user_id)
          values (%s)
          returning session_id
          ''', (user_id,))
      self.connection.commit()
      return cursor.fetchone()['session_id']

  def find_by_session_id(self, session_id):
    with self.connection.cursor() as cursor:
      cursor.execute('''
          select user_id, name
          from sessions
          join users using (user_id)
          where session_id = %s
          ''', (session_id,))
      self.connection.commit()

      try:
        return cursor.fetchone()
      except ProgrammingError:
        return None
