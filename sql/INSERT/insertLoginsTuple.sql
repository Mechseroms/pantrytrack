INSERT INTO logins
(username, password, email) 
VALUES (%s, %s, %s) 
RETURNING *;