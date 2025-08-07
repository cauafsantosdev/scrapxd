from scrapxd.fetcher import fetch_user, fetch_watchlist, fetch_diary, fetch_reviews, fetch_user_lists, fetch_logs
import scrapxd.parser.user as su

soup = fetch_logs("methdrinkerr")

logs = su.parse_logs(soup)

print(logs)
print()

for i, v in enumerate(logs.entries, start=1):
    print(f"{i}: {v}")
