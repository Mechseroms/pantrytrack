WITH passed_id AS (SELECT %s AS passed_id),
	cte_login AS (
		SELECT logins.* FROM logins
		WHERE logins.id = (SELECT passed_id FROM passed_id)
	),
	cte_roles AS (
		SELECT roles.*,
			row_to_json(sites.*) AS site
		FROM roles
		LEFT JOIN sites ON sites.id = roles.site_id
		WHERE roles.id = ANY(SELECT unnest(site_roles) FROM cte_login)
	)

SELECT login.*, 
	(SELECT COALESCE(array_agg(row_to_json(r)), '{}') FROM cte_roles r) AS site_roles
FROM cte_login login;