def user_context(user):
    if not user or not user.is_authenticated:
        return {"kind": "user", "key": "anonymous"}

    return {
        "kind": "user",
        "key": str(user.id),
        "email": user.email,
        "role": getattr(user, "role", "user")
    }
