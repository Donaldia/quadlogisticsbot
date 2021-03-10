

ceo = 806009685089583114
coo = 806009860537057312

donald = 289890066514575360

def isDonald(ctx):
    return ctx.author.id == donald

admissionsTeam = 806011794945998848
admissionsDirector = 806010819195699250

def canInviteCode(ctx):
    # CEO, COO, Donald, Admissions Team, Admissions Director
    roles_ids = [admissionsDirector, admissionsTeam, ceo, coo]
    for r in roles_ids:
        if r in [role.id for role in ctx.author.roles] or isDonald(ctx):
            return True
    
    return False

def canAnnounce(ctx):
    # CEO, COO, Donald
    roles_ids = [ceo, coo]
    for r in roles_ids:
        if r in [role.id for role in ctx.author.roles] or isDonald(ctx):
            return True
    return False

managementTeam = 806009983514574879
managementDirector = 806010967519526932

def canWarn(ctx):
    # CEO, COO, Donald, Community Management Team, Community Director
    roles_ids = [managementDirector, managementTeam, ceo, coo]
    for r in roles_ids:
        if r in [role.id for role in ctx.author.roles] or isDonald(ctx):
            return True
    return False

hrTeam = 806011713354203136
hrDirector = 806011039619481610

def canKick(ctx):
    # CEO, COO, Donald, Human Resources Team, Human Resources Director
    roles_ids = [hrDirector, hrTeam, ceo, coo]
    for r in roles_ids:
        if r in [role.id for role in ctx.author.roles] or isDonald(ctx):
            return True
    return False

def canBan(ctx):
    # CEO, COO, Donald, Human Resources Team, Human Resources Director, Community Management Team, Community Director
    roles_ids = [hrDirector, hrTeam, managementDirector, managementTeam, ceo, coo]
    for r in roles_ids:
        if r in [role.id for role in ctx.author.roles] or isDonald(ctx):
            return True
    return False

def canClear(ctx):
    # CEO, COO, Donald, Community Management Team, Community Director
    roles_ids = [managementDirector, managementTeam, ceo, coo]
    for r in roles_ids:
        if r in [role.id for role in ctx.author.roles] or isDonald(ctx):
            return True
    return False

