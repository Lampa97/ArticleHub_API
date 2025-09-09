from fastapi import Request


def get_articles_collection(request: Request):
    return request.app.mongodb["articles"]


def get_users_collection(request: Request):
    return request.app.mongodb["users"]
