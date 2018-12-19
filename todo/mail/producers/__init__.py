def imap_producer(**kwargs):
    def imap_producer_factory():
        # the import needs to be delayed until call to enable
        # using the wrapper in the django settings
        from .imap import imap_producer

        return imap_producer(**kwargs)

    return imap_producer_factory
