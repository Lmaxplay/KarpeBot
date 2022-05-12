class AuthenticationException(Exception):
    def __str__(self):
        return "User is not Authenticated"

# Create a class called DiscordException that inherits from Exception