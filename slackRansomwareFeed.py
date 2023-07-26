import requests
import time
import datetime 

SLACK_BOT_TOKEN = "YOUR_TOKEN"
SLACK_CHANNEL = "#general"  # Replace with the channel you want to post in

GITHUB_JSON_FEED_URL = "https://raw.githubusercontent.com/joshhighet/ransomwatch/main/posts.json"

def get_latest_victims():
    response = requests.get(GITHUB_JSON_FEED_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def format_message(victim_data):
    post_title = victim_data["post_title"]
    group_name = victim_data["group_name"]
    discovered_date = datetime.datetime.strptime(victim_data["discovered"], "%Y-%m-%d %H:%M:%S.%f")

    # Check if the group_name is in the known members list
    known_members = ["group1", "group2", "group3"]  # Replace with your list of known members
    is_known_member = any(member.lower() in post_title.lower() for member in known_members)

    # Check if the post_title ends with ".fr"
    is_gov_domain = post_title.lower().endswith(".gov")

    # Add @here mention if the condition is met
    if is_known_member or is_gov_domain:
        mention = "<!channel>"
    else:
        mention = ""

    # Format the date in the desired format (e.g., "Jul 26, 2023 02:36 PM")
    formatted_date = discovered_date.strftime("%b %d, %Y %I:%M %p")

    message = f"{mention} New victim added:\nPost Title: {post_title}\nGroup Name: {group_name}\nDiscovered Date: {formatted_date}"
    return message

def send_slack_message(message):
    slack_message = {
        "text": message,
        "channel": SLACK_CHANNEL,
    }

    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
        json=slack_message,
    )

    if response.status_code == 200 and response.json()["ok"]:
        return True
    else:
        return False

def main():
    last_processed_timestamp = datetime.datetime.now()

    while True:
        latest_victims = get_latest_victims()

        if latest_victims:
            new_victims = []

            for victim_data in latest_victims:
                discovered_date = datetime.datetime.strptime(victim_data["discovered"], "%Y-%m-%d %H:%M:%S.%f")

                # Check if the current entry is newer than the last processed one
                if discovered_date > last_processed_timestamp:
                    new_victims.append(victim_data)

            if new_victims:
                for victim_data in new_victims:
                    message = format_message(victim_data)
                    success = send_slack_message(message)

                    if success:
                        print("Slack message sent successfully.")
                    else:
                        print("Failed to send Slack message.")

                # Update the last processed timestamp to the latest one
                last_processed_timestamp = max(new_victims, key=lambda x: datetime.datetime.strptime(x["discovered"], "%Y-%m-%d %H:%M:%S.%f"))["discovered"]

        # Wait for some time before checking for new victims again (e.g., 1 hour)
        time.sleep(3600)
if __name__ == "__main__":
    main()