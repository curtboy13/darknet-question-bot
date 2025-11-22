import os
import json
import traceback
from datetime import datetime
import praw

# ============================================================
# CONFIG
# ============================================================

STATE_FILE = "state.json"
SUBREDDIT_NAME = os.getenv("SUBREDDIT_NAME", "darknet_questions")
POLL_DURATION_DAYS = 1  # 1-day poll

# ============================================================
# QUESTION BANK
# ============================================================

QUESTIONS = [
    {
        "id": 1,
        "question": "What is the safest place to store your market login credentials?",
        "options": [
            "In your browser's saved passwords",
            "In a plaintext notes file on your PC",
            "In an encrypted password manager with a strong master password",
            "Memorized but also reused on multiple sites"
        ],
        "answer_index": 2,
        "explanation": "Using an encrypted password manager with a strong, unique master password greatly reduces risk."
    },
    {
        "id": 2,
        "question": "Which of the following is the BEST way to access onion services?",
        "options": [
            "Normal Chrome/Firefox over a VPN",
            "Tor Browser over your home IP without any hardening",
            "Tor Browser from a hardened OS with good OPSEC",
            "Tor Browser inside normal Windows with all your personal stuff"
        ],
        "answer_index": 2,
        "explanation": "Using Tor Browser from a hardened OS reduces cross-contamination and improves anonymity."
    },
    {
        "id": 3,
        "question": "What is the main purpose of PGP in darknet OPSEC?",
        "options": [
            "To hide your IP address",
            "To encrypt and/or verify messages",
            "To speed up your internet",
            "To automatically find trusted markets"
        ],
        "answer_index": 1,
        "explanation": "PGP is used to encrypt communications and verify authenticity."
    },
    # ... include all your other questions here
]

# ============================================================
# DEBUG FUNCTION - ADD THIS AT THE TOP LEVEL
# ============================================================

def debug_environment():
    print("=== DEBUG INFO ===")
    print(f"Client ID: {'SET' if os.getenv('REDDIT_CLIENT_ID') else 'MISSING'}")
    print(f"Client Secret: {'SET' if os.getenv('REDDIT_CLIENT_SECRET') else 'MISSING'}")
    print(f"Username: {'SET' if os.getenv('REDDIT_USERNAME') else 'MISSING'}")
    print(f"Subreddit: {os.getenv('SUBREDDIT_NAME', 'NOT SET')}")
    print("==================")

# ============================================================
# STATE HANDLING
# ============================================================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_question_index": None}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"last_question_index": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_next_question_index(last_index):
    if last_index is None:
        return 0
    return (last_index + 1) % len(QUESTIONS)

# ============================================================
# REDDIT AUTH
# ============================================================

def get_reddit_instance():
    """Create authenticated Reddit client (PRAW)."""
    try:
        return praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent="darknet_daily_bot_v1.0"  # Use hardcoded user agent
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Reddit client: {e}")

# ============================================================
# POST BUILDERS
# ============================================================

def build_post_title(current_index):
    q = QUESTIONS[current_index]
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"Darknet Question of the Day #{q['id']} ({today})"

def build_post_body(state, current_index):
    q = QUESTIONS[current_index]
    body = []

    # Yesterday's answer
    last_index = state.get("last_question_index")
    if last_index is not None:
        prev_q = QUESTIONS[last_index]
        correct = prev_q["options"][prev_q["answer_index"]]
        explanation = prev_q["explanation"]

        body.append(
            "**Yesterday's answer:**\n"
            f">!{correct}!<\n\n"
            f"{explanation}\n\n"
            "---\n\n"
        )

    # Disclaimer
    body.append(
        "_This subreddit does **not** encourage or promote illegal activity. "
        "All discussion is for educational and harm-reduction purposes only._\n\n"
    )

    # Today's question
    body.append(
        f"**Today's Darknet / OPSEC Question:**\n\n"
        f"{q['question']}\n\n"
        "Vote in the poll below — the correct answer will appear tomorrow.\n"
    )

    return "".join(body)

# ============================================================
# MAIN BOT LOGIC
# ============================================================

def post_daily_question():
    state = load_state()
    last_index = state.get("last_question_index")

    current_index = get_next_question_index(last_index)
    q = QUESTIONS[current_index]

    print(f"Posting Question #{q['id']}")

    reddit = get_reddit_instance()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    title = build_post_title(current_index)
    body = build_post_body(state, current_index)

    print(f"Posting to r/{SUBREDDIT_NAME}...")

    submission = subreddit.submit_poll(
        title=title,
        selftext=body,
        options=q["options"],
        duration=POLL_DURATION_DAYS
    )

    print("Posted:", submission.id)

    state["last_question_index"] = current_index
    save_state(state)

    print("State updated.")

# ============================================================
# ENTRY POINT - SINGLE, CLEAN VERSION
# ============================================================

if __name__ == "__main__":
    print("=== Starting Darknet Daily Bot ===")
    debug_environment()  # This will show what's set up
    
    try:
        post_daily_question()
        print("=== Success! Bot completed. ===")
    except Exception as e:
        print(f"=== ERROR: {e} ===")
        Run and capture output to a file (simple, works for any executable/script): nohup python bot.py > bot.log 2>&1 & # background, logs to bot.log tail -f bot.log # follow log
            - name: Direct Reddit OAuth token check
      env:
        REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
        REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
        REDDIT_USERNAME: ${{ secrets.REDDIT_USERNAME }}
        REDDIT_PASSWORD: ${{ secrets.REDDIT_PASSWORD }}
        REDDIT_USER_AGENT: ${{ secrets.REDDIT_USER_AGENT }}
      run: |
        python3 - <<'PY'
import os, requests, sys

cid = os.getenv("REDDIT_CLIENT_ID")
csec = os.getenv("REDDIT_CLIENT_SECRET")
user = os.getenv("REDDIT_USERNAME")
pw = os.getenv("REDDIT_PASSWORD")
ua = os.getenv("REDDIT_USER_AGENT", "darknet_daily_bot_v1.0")

print("Performing direct OAuth token request...")

r = requests.post(
    "https://www.reddit.com/api/v1/access_token",
    auth=(cid, csec),
    data={"grant_type": "password", "username": user, "password": pw},
    headers={"User-Agent": ua},
    timeout=10
)

print("HTTP Status:", r.status_code)
print("Response:", r.text[:500])
PY

        traceback.print_exc()
        # Exit with error code so GitHub Actions shows failure
        exit(1)
