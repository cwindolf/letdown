import types
import contextlib
import dataclasses


@contextlib.contextmanager
def tagged_union(union_name, shared_fields=None):

    # -- storage for subclasses of main class so that
    #    they live as attributes of that class

    in_context = True
    registry = {}

    # to be added to the class we yield
    def __init_subclass__(cls, **kwargs):
        if in_context:
            registry[cls.__name__] = cls
        else:
            raise ValueError("Please only subclass me in my context.")

    # -- logic so that that shared fields in the variants
    #    don't have to be repeated

    shared_fields_bases = ()
    if shared_fields is not None:
        shared_fields_bases = (
            dataclasses.make_dataclass(
                f"{union_name}VariantBase", fields=shared_fields
            ),
        )

    # -- metaclass for the union superclass

    class UnionMeta(type):
        def __new__(mcs, name, bases, namespace, **kwargs):
            if bases:
                return dataclasses.dataclass(
                    type.__new__(
                        MemberMeta,
                        name,
                        shared_fields_bases + bases,
                        namespace,
                        **kwargs,
                    )
                )
            else:
                return type.__new__(mcs, name, bases, namespace, **kwargs)

        def __getattr__(cls, name):
            if name in registry:
                return registry[name]
            raise AttributeError(
                f"TaggedUnion {union_name} has no attribute {name}."
            )

        @classmethod
        def __prepare__(cls, name, bases):
            return {"__init_subclass__": __init_subclass__}

    # -- metaclass for the types in the union
    # this basically sets them up as dataclasses and makes sure
    # they don't have the

    class MemberMeta(UnionMeta):
        def __getattr__(cls, name):
            raise AttributeError(
                f"Union variant {cls.__name__} has no attribute {name}."
            )

    # -- define the actual class which variants will subclass

    my_tagged_union = types.new_class(
        union_name, kwds=dict(metaclass=UnionMeta)
    )

    # -- yield it to the context

    try:
        yield my_tagged_union
    finally:
        in_context = False
