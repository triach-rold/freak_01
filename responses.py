from random import choice
from datetime import datetime
import pytz
from random import randint

# Global variable to store the previous valid yews link
previous_valid_yews_link = None


def get_response(user_input: str) -> str:
    global previous_valid_yews_link

    lowered: str = user_input.lower()

    if lowered == '':
        return 'Well, you\'re awfully silent...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return 'Good, thanks!'
    elif 'bye' in lowered:
        return 'See you soon!'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1, 6)}'
    elif 'yews today' in lowered:
        # Get the current time in US Eastern Time (ET)
        eastern = pytz.timezone('US/Eastern')
        current_time = datetime.now(eastern)
        hour = current_time.hour

        if hour < 15:
            edition = f"{current_time.month}-{current_time.day}-{current_time.year%100}-10am"
        elif hour < 20:
            edition = f"{current_time.month}-{current_time.day}-{current_time.year%100}-3pm"
        else:
            edition = f"{current_time.month}-{current_time.day}-{current_time.year%100}-8pm"

        yews_link = f"https://www.yews.news/edition/{edition}"

        if check_link_validity(yews_link):
            # If the current link is valid, update the previous valid link
            previous_valid_yews_link = yews_link
            return yews_link
        else:
            # If the current link is invalid, return the previous valid link
            if previous_valid_yews_link:
                return previous_valid_yews_link
            else:
                return "There is no previous valid yews link."
    else:
        return ""


def check_link_validity(link: str) -> bool:
    # Here you can implement your logic to check if the link is valid or not
    # For simplicity, I'll just return True for now
    return True
