

staff_ids = [
    586931677268279306
]

admin_ids = [
    "0"
]


def isDonald(ctx):
    return ctx.message.author.id == 289890066514575360

def isOwner(ctx):
    return ctx.message.author == ctx.message.guild.owner or isDonald(ctx)

def isStaff(ctx):
    for i in staff_ids:
        if i in [role.id for role in ctx.author.roles] or isDonald(ctx) or isOwner(ctx):
            return True

    return False

def isAdmin(ctx):
    for i in admin_ids:
        if i in [role.id for role in ctx.author.roles] or isDonald(ctx) or isOwner(ctx) or isStaff(ctx):
            return True

    return False