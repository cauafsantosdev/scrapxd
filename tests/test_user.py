from scrapxd.models.user import User

user = User(username="methdrinkerr")

logs = user.logs()

print(logs)
print()

for i, v in enumerate(logs.entries, start=1):
    print(f"{i}: {v}")
