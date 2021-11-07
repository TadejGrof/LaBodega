from django_filters import FilterSet

class InitFilterSet(FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()
            for name, f in self.base_filters.items():
                initial = f.extra.get('initial')
                if not data.get(name) and initial:
                    data[name] = initial
        super().__init__(data, *args, **kwargs)
