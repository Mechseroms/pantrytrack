INSERT INTO users (user_name, user_password, user_email)
VALUES (%(user_name)s, %(user_password)s, %(user_email)s)
RETURNING *;