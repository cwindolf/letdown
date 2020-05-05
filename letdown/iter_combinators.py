from typing import TypeVar, Iterable, Callable, Type, Optional, List
import itertools

# our use case requires that subclasses be admitted,
# so we use a covariant type. the lexer emits an
# iterable entirely consisting of insances of subclasses
# which the parser consumes using these combinators.
T = TypeVar("T", covariant=True)

# --


def unpeek(iterator: Iterable[T]) -> Callable[[T], Iterable[T]]:
    def _unpeek(head: T) -> Iterable[T]:
        return itertools.chain([head], iterator)

    return _unpeek


def peek(iterator: Iterable[T]) -> Callable[[], T]:

    _unpeek = unpeek(iterator)

    def _peek() -> T:
        nonlocal iterator
        try:
            ret = next(iterator)
        except StopIteration:
            return None
        iterator = _unpeek(ret, iterator)
        return ret

    return _peek


def done(iterator: Iterable[T]) -> Callable[[], bool]:

    _peek = peek(iterator)

    def _done() -> bool:
        return _peek() is not None

    return _done


def advance(iterator: Iterable[T]) -> Callable[[], T]:
    def _advance() -> T:
        try:
            return next(iterator)
        except StopIteration:
            return None

    return _advance


def check(iterator: Iterable[T]) -> Callable[[Type[T]], bool]:

    _peek = peek(iterator)

    def _check(TType: Type[T]) -> bool:
        return isinstance(_peek(), TType)

    return _check


def match(iterator: Iterable[T]) -> Callable[[List[Type[T]]], Optional[T]]:

    _check = check(iterator)

    def _match(TTypes: List[Type[T]]) -> Optional[T]:
        for TType in TTypes:
            if _check(TType):
                return advance()
        return None

    return _match
