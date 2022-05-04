class SchemaBase:
    _client = None
    _instance = None


class Resource(dict, SchemaBase):
    def __getattr__(self, name):
        try:
            return super().__getitem__(name)
        except KeyError:
            try:
                return super().__getattribute__(name)
            except AttributeError as e:
                raise AttributeError(e) from None

    def __setattr__(self, name, value):
        super().__setitem__(name, value)

    def __str__(self):
        id = getattr(self, "id", "")

        return f"{self.__class__.__name__} #{id}" if id else self.__class__.__name__

    def __repr__(self):
        return object.__repr__(self)

    def get(self, resource, subresource=None, *args, **kwargs):
        response = self._client.get(
            [resource, subresource, getattr(self, "id", None)], *args, **kwargs
        )
        super().update(response)

        return self

    def patch(self, resource, data, *args, **kwargs):
        response = self._client.patch(
            [resource, getattr(self, "id", None)],
            json=data,
            *args,
            **kwargs,
        )

        super().update(response)

        return self

    def post(self, resource, *args, **kwargs):
        response = self._client.post(
            resource,
            json=self,
            *args,
            **kwargs,
        )
        super().update(response)

        return self

    def put(self, resource, *args, **kwargs):
        response = self._client.put(
            [resource, getattr(self, "id", None)],
            json=self,
            *args,
            **kwargs,
        )

        super().update(response)

        return self

    def delete(self, resource, *args, **kwargs):
        response = self._client.delete(
            [resource, getattr(self, "id", None)], *args, **kwargs
        )
        super().update(response)

        return self


class Collection(list, SchemaBase):
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.__class__(*super().__getitem__(index))

        return super().__getitem__(index)

    def __repr__(self):
        return object.__repr__(self)

    def get(self, *args, **kwargs):
        return self.request(self._client.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request(self._client.post, *args, **kwargs)

    def request(self, method, resource, paginate=False, *args, **kwargs):
        paginator = PageIterator(self, resource, method, *args, **kwargs)

        if paginate:
            return paginator

        self.clear()
        for n, _ in enumerate(paginator):
            if n == paginator.limit - 1:
                break

        return self


class PageIterator:
    def __init__(self, collection, resource, method, limit=25, *args, **kwargs):
        self.collection = collection
        self.resource = resource
        self.method = method
        self.limit = limit

        if limit != 25:
            kwargs.setdefault("params", {}).update(limit=limit)

        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        self.page = 0
        self.total_pages = 0
        self._resources = []

        return self

    def __next__(self):
        if self.resources:
            return self.resources.pop(0)

        if self.page <= self.total_pages:
            self.kwargs.setdefault("params", {}).update(page=self.page)
            self.resources, meta = self.method(self.resource, *self.args, **self.kwargs)
            self.total_pages = meta["totalPages"]
            self.page = meta["number"] + 1

            return next(self)

        raise StopIteration

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, value):
        self._resources = [self.collection.resource(v) for v in value]
        self.collection.extend(self.resources)
