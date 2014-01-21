import datetime
import uuid


_registry = {}
_registry_rev = {}


def register(name, node):
    assert type(name) is str
    assert type(node) is int

    if _registry.has_key(name) or _registry_rev.has_key(node):
        raise Exception('Node (%d) already registered "%s"' % (node, name))
    else:
        _registry[name] = node
        _registry_rev[node] = name


def create(node_identifier):
    return uuid.uuid1(node(node_identifier))


def node(identifier):
    if type(identifier) is str:
        return _registry[identifier]
    elif identifier in _registry_rev:
        return identifier
    raise Exception('Identifier does not exists')
UUID = node


def uuid_to_dt(u):
    return datetime.datetime.fromtimestamp((u.time - 0x01b21dd213814000L)*100/1e9)