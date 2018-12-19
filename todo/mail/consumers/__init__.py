def tracker_consumer(**kwargs):
    def tracker_factory(producer):
        # the import needs to be delayed until call to enable
        # using the wrapper in the django settings
        from .tracker import tracker_consumer

        return tracker_consumer(producer, **kwargs)

    return tracker_factory
