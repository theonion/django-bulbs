from elasticsearch_dsl.filter import Exists, MatchAll, Nested, Not, Range, Term, Terms
from elasticsearch_dsl.query import FunctionScore


def TagBoost(tags, boost_mode="multiply", weight=5):
    return FunctionScore()


def VideoBoost(boost_mode="multiply", weight=5):
    return FunctionScore()
