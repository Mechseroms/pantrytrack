INSERT INTO units (unit_plural, unit_single, unit_fullname, unit_description)
VALUES (%(unit_plural)s, %(unit_single)s,%(unit_fullname)s,%(unit_description)s)
RETURNING *;