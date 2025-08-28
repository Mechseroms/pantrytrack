from application.database_postgres.UsersModel import UsersModel
from application.database_postgres.RolesModel import RolesModel
from application.database_postgres.BaseModel import DatabaseError, tupleDictionaryFactory
import config
import psycopg2

class ExtendedRolesModel(RolesModel):
    @classmethod
    def select_by_site_uuid(self, payload, convert=True, conn=None):
        roles = ()
        self_conn = False
        select_roles_sql = f"SELECT * FROM roles WHERE role_site_uuid = %(site_uuid)s::uuid;"
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(select_roles_sql, payload)
                rows = cur.fetchall()
                if rows and convert:
                    roles = [tupleDictionaryFactory(cur.description, role) for role in rows]
                elif rows and not convert:
                    roles = rows
            
            if self_conn:
                conn.close()

            return roles
        except Exception as error:
            raise DatabaseError(error, payload, select_roles_sql)

class ExtendedUsersModel(UsersModel):
    @classmethod
    def add_admin_user(self, payload:dict, convert=True, conn=None):
        admin_user = ()
        self_conn = False
        sql = f"""INSERT INTO users (user_name, user_password, user_email, user_row_type)  
        VALUES (%(user_name)s, %(user_password)s, %(user_email)s, %(user_row_type)s) ON CONFLICT (user_name) DO UPDATE SET user_name = excluded.user_name RETURNING *;"""
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    admin_user = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    admin_user = rows   

            if self_conn:
                conn.commit()
                conn.close()

            return admin_user
        except Exception as e:
            DatabaseError(str(e), payload, sql)
    
    @classmethod
    def update_roles(self, payload, convert=True, conn=None):
        """ payload: {'role_uuid': x,} """
        self_conn = False
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            select_sql = f"SELECT users.user_uuid FROM users WHERE user_roles @> ARRAY[%(role_uuid)s::uuid];"
            with conn.cursor() as cur:
                cur.execute(select_sql, payload)
                users = tuple([row[0] for row in cur.fetchall()])

            update_sql = f"UPDATE users SET user_roles = array_remove(user_roles, %(role_uuid)s::uuid) WHERE user_uuid = %(user_uuid)s::uuid;"
            with conn.cursor() as cur:
                for user_uuid in users:
                    cur.execute(update_sql, {'role_uuid': payload['role_uuid'], 'user_uuid': user_uuid})
            
            if self_conn:
                conn.commit()
                conn.close()

        except Exception as error:
            raise error

    @classmethod
    def update_sites(self, payload, convert=True, conn=None):
        """ payload: {'site_uuid',} """
        self_conn = False
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True

            select_sql = f"SELECT users.user_uuid FROM users WHERE user_sites @> ARRAY[%(site_uuid)s::uuid];"
            with conn.cursor() as cur:
                cur.execute(select_sql, payload)
                user = tuple([row[0] for row in cur.fetchall()])

            update_sql = f"UPDATE users SET user_sites = array_remove(user_sites, %(site_uuid)s::uuid) WHERE user_uuid = %(user_uuid)s::uuid;"
            with conn.cursor() as cur:
                for user_uuid in user:
                    cur.execute(update_sql, {'site_uuid': payload['site_uuid'], 'user_uuid': user_uuid})
            
            if self_conn:
                conn.commit()
                conn.close()

        except Exception as error:
            raise error

    @classmethod
    def update_user_site_roles(self, payload, convert=True, conn=None):
        """ payload (tuple): (site_uuid, role_uuid, user_uuid) """
        sql = f"UPDATE users SET user_sites = user_sites || %(site_uuid)s::uuid, user_roles = user_roles || %(role_uuid)s::uuid WHERE user_uuid=%(user_uuid)s RETURNING *;"
        user = ()
        self_conn = False
        try:
            if not conn:
                database_config = config.config()
                conn = psycopg2.connect(**database_config)
                conn.autocommit = True
                self_conn = True
            
            with conn.cursor() as cur:
                cur.execute(sql, payload)
                rows = cur.fetchone()
                if rows and convert:
                    user = tupleDictionaryFactory(cur.description, rows)
                elif rows and not convert:
                    user = rows
            
            if self_conn:
                conn.commit()
                conn.close()

            return user
        except Exception as error:
            raise DatabaseError(error, payload, sql)