INSERT INTO units
(plural, single, fullname, description) 
VALUES (%s, %s, %s, %s) 
RETURNING *;