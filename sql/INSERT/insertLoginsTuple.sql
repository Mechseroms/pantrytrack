INSERT INTO logins
(username, password, email, row_type) 
VALUES (%s, %s, %s, %s) 
RETURNING *;