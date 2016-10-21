from flask import request
from flask import jsonify
from flask.views import MethodView


class View(MethodView):
    """Subclass of Flask MethodView with a couple helper methods."""

    @classmethod
    def register(cls, blueprint, route, name):
        """
        A shortcut method for registering this view to an app or blueprint.
        Assuming we have a blueprint and a CourseAdd view, then these two
        lines are identical in functionality:
            views.add_url_rule('/courses', view_func=CourseAdd.as_view('courses'))
            CourseAdd.register(views, '/courses', 'courses')
        """
        blueprint.add_url_rule(route, view_func=cls.as_view(name))

    def dispatch(self):
        """Hook for a custom action before the normal method is called."""
        pass

    def dispatch_request(self, *args, **kwargs):
        """Subclass to call the custom dispatch() method."""
        self.args = args
        self.kwargs = kwargs

        rv = self.dispatch()
        if rv:
            return rv
        return super().dispatch_request(*args, **kwargs)

    def get_post_data(self):
        """Get the post data, either from the form or json."""
        if request.form:
            return request.form.to_dict()
        if request.json:
            return dict(request.json)
        return {}

    def response(self, data, code=200):
        """Return the given data as JSON with the given status code."""
        return jsonify(data), code

    def object(self, data):
        """Return the given data as JSON with a key of 'object'."""
        return jsonify(dict(object=data)), 200

    def objects(self, data):
        """Return the given data as JSON with a key of 'objects'."""
        return jsonify(dict(objects=data)), 200

    def errors(self, data):
        """Return the given data as JSON with a key of 'errors'."""
        return jsonify(dict(errors=data)), 422
