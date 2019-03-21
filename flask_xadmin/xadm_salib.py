# -*- coding: utf-8 -*-
# __author__ = 'dsedad'

from sqlalchemy.inspection import inspect as inspect_sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.interfaces import MANYTOMANY, ONETOMANY, MANYTOONE
from sqlalchemy.types import TypeDecorator, VARCHAR


class Password(TypeDecorator):
    """Platform-independent password type."""
    impl = VARCHAR


def sa_column_changed(model, column):
    from sqlalchemy import inspect
    inspr = inspect(model)
    hist = getattr(inspr.attrs, column).history
    return hist.has_changes()

def sa_view_url(model, vwtype='details'):
    tm = model
    return '{}.{}_view'.format(model.__name__.lower(), vwtype)


def sa_relationship_key_pairs(relationship):
    remote = relationship.mapper.class_
    local = relationship.parent.class_
    srckeys = []
    rmtkeys = []
    for r in relationship.local_remote_pairs:
        srckeys.append(r[0].key)
        rmtkeys.append(r[1].key)
    return {"mapper": remote, "parent": local, "local": srckeys, "remote": rmtkeys,
            "direction": str(relationship.direction)}


def sa_get_relationship_value(relationship):
    return relationship


def sa_relationships(model, relation_name=None, directions=[MANYTOONE]):
    # Find relationship (filter by name, do not filter if filter_name = None)
    res = []
    for r in inspect_sa(model).relationships:
        pass
        if relation_name is None:
            if r.direction in directions:
                res.append(r)
        elif relation_name.lower() == r.key.lower():
            res.append(r)

    return res


def sa_column_filters(model, mode='full'):
    list = sa_column_filterable_list(model)
    if mode == 'full':
        list += sa_relationships_keys(model)
    return list


def sa_relationship_keys(relationship):
    return [rel.key for rel in relationship]


def sa_relationships_keys(model, directions=[MANYTOONE]):
    return [rel.key for rel in sa_relationships(model, directions=directions)]


def sa_hybrids(model):
    return [item for item in inspect_sa(model).all_orm_descriptors if type(item) == hybrid_property]


def sa_hybrid_keys(model):
    return [item.__name__ for item in sa_hybrids(model)]


def sa_column_type(model, column_name):
    sa_model = inspect_sa(model)
    col = sa_model.c.get(column_name)
    col_type = None
    if col is not None:
        col_type = type(col.type).__name__.lower()
    return col_type


def sa_column_description(model_column):
    desc = ""
    try:
        desc = model_column.doc
    except:
        pass
    return desc


def sa_columns(model):
    mapper = inspect_sa(model)
    return mapper.attrs


def sa_column_keys(model):
    return [item.key for item in sa_columns(model)]

def sa_type_keys(model, lowertype):
    keys = []
    for c in sa_columns(model):
        typestr = sa_column_type(model, c.key)
        if typestr == lowertype:
            keys.append(c.key)
    return keys

def sa_column_descriptions(model):
    result = {}
    for prop in sa_columns(model):
        desc = sa_column_description(prop)
        if desc:
            result[prop.key] = desc
    return result


def sa_column_filterable_list(model):
    return [str(c.name)
            for c in model.__table__.columns
            if type(c.type).__name__.lower() not in ('guid', 'largebinary')]


def sa_column_searchable_list(model):
    x = model.__table__.columns
    return [str(c.name)
            for c in model.__table__.columns
            if type(c.type).__name__ == 'String']


def sa_relationships4key(model, key, directions=[MANYTOONE]):
    res = []
    for r in sa_relationships(model):
        kp = sa_relationship_key_pairs(r)
        if key in kp["local"] and r.direction in directions:
            res.append(r)
    return res

def gen_href_formatter(model, relationship_names=None, ahref_fmt="<a href='%s'>%s</a>"):
    from flask import url_for, Markup
    def _href_formatter(view, context, model, name):
        rels = sa_relationships(type(model), name)
        res = ""
        if rels:
            # Get first relationship if found more then one -
            r = rels[0]

            # Generate url path
            view_url = sa_view_url(r.mapper.class_)

            # Populate url args
            url_args = []
            i = 0
            # Find mapping between local and remote keys
            r_kp = sa_relationship_key_pairs(r)
            for rmt in r_kp['remote']:
                url_args.append(getattr(model, r_kp['local'][i]))
                i += 1
            url_args_str = ",".join(str(e) for e in url_args)

            # Ignore if instance of referenced model view does not exists
            show_attr = getattr(model, name)

            # Python 3 compatibility
            try:
                show_value = show_attr.__unicode__()
            except:
                show_value = show_attr.__str__()

            try:
                url = url_for(view_url, id=url_args_str)
                if show_attr:
                    res = Markup(
                        ahref_fmt % (
                            url,
                            show_value
                        )
                    )
                    pass
            except:
                res = show_value
        return res

    # If relationship_names == None, generate for all relationships
    res = {}
    if relationship_names == None:
        for r in sa_relationships(model):
            res[r.key] = _href_formatter
    else:
        for r in relationship_names:
            for r in sa_relationships(model, relation_name=r):
                res[r.key] = _href_formatter
    return res
