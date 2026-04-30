
def get_client_info(request):
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    return ip, user_agent