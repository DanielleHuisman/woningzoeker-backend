import graphene

import corporations.schema
import profiles.schema
import residences.schema


class Query(
    corporations.schema.Query,
    profiles.schema.Query,
    residences.schema.Query,
    graphene.ObjectType
):
    pass


# class Mutation(graphene.ObjectType):
#     pass


schema = graphene.Schema(query=Query)
