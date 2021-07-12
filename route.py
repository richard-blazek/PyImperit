import flask

def post(app, url, default_gen, **par):
	def decorator(func):
		def wrapper(*args, **kwargs):
			values=[flask.request.form.get(key, type=par[key]) for key in par]
			if [value for value in values if value is None]:
				return default_gen()
			result=func(*values, *args, **kwargs)
			return result if result else default_gen()
		wrapper.__name__=func.__name__
		return app.route(url, methods=['GET', 'POST'])(wrapper)
	return decorator