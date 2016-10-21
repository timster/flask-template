from playhouse.flask_utils import get_object_or_404


class Resource:
    """A resource is an object that can be exposed via a REST API."""

    model = None

    def __init__(self, private=False):
        self.private = private

    def create(self, **kwargs):
        """
        Create an instance of the model and return it.
        The given kwargs are passed directly to the model constructor.
        """
        if not self.model:
            msg = '{} must define a model class.'.format(self.__class__.__name__)
            raise NotImplementedError(msg)
        return self.model(**kwargs)

    def all(self):
        """Return an iterable representing all the available objects."""
        if not self.model:
            msg = '{} must define a model class.'.format(self.__class__.__name__)
            raise NotImplementedError(msg)
        return self.model.select()

    def get(self, pk):
        """Find an object with the given primary key or raise NotFound."""
        return get_object_or_404(self.all(), self.model.id == pk)

    def serialize_many(self, data):
        """Serialize the given data as an iterable of objects."""
        return tuple(self.serialize(obj) for obj in data)

    def serialize(self, obj):
        """Serialize the given object to a dictionary representation."""
        return obj.to_dict(private=self.private)
