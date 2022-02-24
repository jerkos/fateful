def with_(context_manager, f):
    with context_manager:
        f()