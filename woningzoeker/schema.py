import graphene

import corporations.schema


class Query(
    corporations.schema.Query,
    graphene.ObjectType
):
    pass


# class Mutation(graphene.ObjectType):
#     pass


schema = graphene.Schema(query=Query)
