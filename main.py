import os
import json
from datetime import datetime
import praw

# ============================================================
# CONFIG
# ============================================================

STATE_FILE = "state.json"
SUBREDDIT_NAME = os.getenv("SUBREDDIT_NAME", "darknet_questions")
POLL_DURATION_DAYS = 1  # Poll lasts 24 hours

# ============================================================
# QUESTION BANK — full 50 questions
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
        "explanation": (
            "Using an encrypted password manager with a strong, unique master password "
            "greatly reduces the risk compared to plaintext or browser storage."
        )
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
        "explanation": (
            "Using Tor Browser from a hardened OS reduces cross-contamination and improves anonymity."
        )
    },
    {
        "id": 3,
        "question": "What is the main purpose of PGP in darknet OPSEC?",
        "options": [
            "To hide your IP address from websites",
            "To encrypt and/or verify messages between you and vendors",
            "To speed up your internet connection",
            "To automatically find trusted markets"
        ],
        "answer_index": 1,
        "explanation": (
            "PGP is used to encrypt sensitive communications and verify authenticity of messages."
        )
    },
    {
        "id": 4,
        "question": "Why is reusing nicknames/handles across clearnet and darknet a bad idea?",
        "options": [
            "It makes your connection slower",
            "It makes markets ban you",
            "It links your darknet identity to clearnet footprints and OSINT",
            "It prevents vendors from recognizing you"
        ],
        "answer_index": 2,
        "explanation": (
            "Reusing a handle allows others to correlate clearnet and darknet identities."
        )
    },
    {
        "id": 5,
        "question": "Which is generally the safer way to handle BTC for darknet use?",
        "options": [
            "Sending directly from KYC exchange to market deposit address",
            "Self-custody wallet → privacy workflow → market",
            "Store all coins on the exchange at all times",
            "Email your private key to yourself for backup"
        ],
        "answer_index": 1,
        "explanation": (
            "Using a self-custody wallet and privacy workflow reduces direct linkage from KYC exchanges."
        )
    },
    {
        "id": 6,
        "question": "What is the main risk of using your real email address to register on darknet forums?",
        "options": [
            "You'll receive too much spam",
            "It creates a direct link between your real identity and darknet activity",
            "Email services don't work with Tor",
            "Forums require phone verification for real emails"
        ],
        "answer_index": 1,
        "explanation": (
            "Real emails can be tied to your identity through breaches, subpoenas, or OSINT."
        )
    },
    {
        "id": 7,
        "question": "Why should you avoid taking screenshots of market pages?",
        "options": [
            "Screenshots don't work in Tor Browser",
            "Metadata may reveal device info; cloud sync can expose you",
            "Markets automatically ban users who take screenshots",
            "It slows down your connection"
        ],
        "answer_index": 1,
        "explanation": (
            "Screenshot metadata and accidental cloud sync can leak identifying info."
        )
    },
    {
        "id": 8,
        "question": "What is 'fingerprinting' in browser privacy?",
        "options": [
            "Using biometric login",
            "Tracking users by unique browser configuration",
            "A type of malware",
            "Encrypting your browsing history"
        ],
        "answer_index": 1,
        "explanation": (
            "Fingerprinting uses browser attributes to uniquely identify users."
        )
    },
    {
        "id": 9,
        "question": "Why is it recommended to use Tor Browser default settings?",
        "options": [
            "Custom settings make it faster",
            "Custom settings make you unique and easier to fingerprint",
            "Default settings are required by Tor",
            "Custom settings void your warranty"
        ],
        "answer_index": 1,
        "explanation": (
            "Changing Tor settings creates a unique fingerprint compared to millions of default users."
        )
    },
    {
        "id": 10,
        "question": "What does 'doxing' mean?",
        "options": [
            "Installing security software",
            "Publicly revealing private personal information",
            "Creating fake documents",
            "Encrypting your data"
        ],
        "answer_index": 1,
        "explanation": (
            "Doxing is exposing private information about someone to harm them."
        )
    },
    {
        "id": 11,
        "question": "Why avoid logging into personal accounts while using Tor?",
        "options": [
            "Personal accounts don't work on Tor",
            "It links your real identity to your Tor session",
            "Tor is too slow",
            "It's against Tor rules"
        ],
        "answer_index": 1,
        "explanation": (
            "Logging into real accounts destroys anonymity by linking the session to you."
        )
    },
    {
        "id": 12,
        "question": "What is the purpose of Tails OS?",
        "options": [
            "It's faster",
            "An amnesic OS that leaves no trace and routes all traffic through Tor",
            "It's required by markets",
            "It mines cryptocurrency automatically"
        ],
        "answer_index": 1,
        "explanation": (
            "Tails leaves no trace on your computer and forces all traffic through Tor."
        )
    },
    {
        "id": 13,
        "question": "What is 'OPSEC' short for?",
        "options": [
            "Operation Security",
            "Operational Security",
            "Open Security",
            "Optical Security"
        ],
        "answer_index": 1,
        "explanation": "OPSEC means Operational Security."
    },
    {
        "id": 14,
        "question": "Why never share screenshots of market transactions?",
        "options": [
            "They take up too much space",
            "They contain identifying metadata and transaction details",
            "Markets prohibit it",
            "Screenshots distort onion links"
        ],
        "answer_index": 1,
        "explanation": (
            "Metadata and transaction info can expose you."
        )
    },
    {
        "id": 15,
        "question": "What is the safest way to verify a market's onion link?",
        "options": [
            "Google search the market name",
            "Use trusted community sources + PGP signatures",
            "Click random links on forums",
            "Ask strangers in Reddit DMs"
        ],
        "answer_index": 1,
        "explanation": (
            "PGP-verified trusted sources prevent phishing."
        )
    },
    {
        "id": 16,
        "question": "Why avoid reusing passwords across markets?",
        "options": [
            "Markets share databases",
            "A compromise on one site compromises all",
            "It slows down logins",
            "Markets require unique passwords"
        ],
        "answer_index": 1,
        "explanation": (
            "Markets frequently get hacked or exit scam; reused passwords cause multi-site compromise."
        )
    },
    {
        "id": 17,
        "question": "What does 'KYC' stand for?",
        "options": [
            "Keep Your Coins",
            "Know Your Customer",
            "Key Your Crypto",
            "Kill Your Cache"
        ],
        "answer_index": 1,
        "explanation": (
            "KYC is identity verification used by regulated exchanges."
        )
    },
    {
        "id": 18,
        "question": "Why avoid public WiFi for darknet activity?",
        "options": [
            "It's slower",
            "Network owners can log activity and correlate timestamps",
            "Public WiFi blocks Tor",
            "It costs money"
        ],
        "answer_index": 1,
        "explanation": (
            "Public WiFi logs can correlate your physical presence with online activity."
        )
    },
    {
        "id": 19,
        "question": "What is 'multisig escrow'?",
        "options": [
            "Multiple shipping addresses",
            "Multiple parties must sign to release funds",
            "Multiple payment methods",
            "Multiple vendor accounts"
        ],
        "answer_index": 1,
        "explanation": (
            "Multisig escrow prevents markets from stealing funds."
        )
    },
    {
        "id": 20,
        "question": "Why never reuse Bitcoin addresses?",
        "options": [
            "Addresses expire",
            "Address reuse links all transactions together",
            "Bitcoin charges extra",
            "Old addresses slow down transactions"
        ],
        "answer_index": 1,
        "explanation": (
            "Address reuse destroys privacy by linking transactions."
        )
    },
    {
        "id": 21,
        "question": "Why use a VPN before Tor?",
        "options": [
            "It makes Tor faster",
            "It hides Tor usage from your ISP",
            "Tor requires it",
            "It encrypts Tor traffic"
        ],
        "answer_index": 1,
        "explanation": (
            "VPN-before-Tor hides Tor from your ISP, useful in restrictive regions."
        )
    },
    {
        "id": 22,
        "question": "What is 'OSINT'?",
        "options": [
            "Operating System Intelligence",
            "Open Source Intelligence",
            "Onion Security Internet",
            "Optical Signal Interface"
        ],
        "answer_index": 1,
        "explanation": "OSINT means gathering intel from public sources."
    },
    {
        "id": 23,
        "question": "Why verify PGP signatures on market communications?",
        "options": [
            "It looks professional",
            "It confirms authenticity",
            "It's required by law",
            "It encrypts the message"
        ],
        "answer_index": 1,
        "explanation": (
            "PGP signatures prevent phishing and impersonation attacks."
        )
    },
    {
        "id": 24,
        "question": "What is 'tumbling' or 'mixing' crypto?",
        "options": [
            "Converting to another coin",
            "Mixing coins with others to break linkability",
            "Storing in multiple wallets",
            "Mining new coins"
        ],
        "answer_index": 1,
        "explanation": "Mixing breaks the blockchain link between sender and receiver."
    },
    {
        "id": 25,
        "question": "Why avoid discussing specific orders/vendors publicly?",
        "options": [
            "It's against rules",
            "It helps law enforcement connect patterns",
            "Vendors dislike publicity",
            "It slows down the forum"
        ],
        "answer_index": 1,
        "explanation": (
            "Public details can be correlated with other data to identify individuals."
        )
    },
    {
        "id": 26,
        "question": "What is the main advantage of Monero over Bitcoin?",
        "options": [
            "Monero is faster",
            "Monero has built-in privacy by default",
            "Monero is worth more",
            "Monero is easier to buy"
        ],
        "answer_index": 1,
        "explanation": (
            "Monero hides sender, receiver, and amount using privacy primitives."
        )
    },
    {
        "id": 27,
        "question": "Why is it risky to keep funds in a market wallet?",
        "options": [
            "High fees",
            "Markets can exit scam, get seized, or hacked",
            "Withdrawals don't work",
            "Market wallets are slow"
        ],
        "answer_index": 1,
        "explanation": "Markets control the keys; funds can disappear anytime."
    },
    {
        "id": 28,
        "question": "What is 'OpSec fatigue'?",
        "options": [
            "Tired feeling after Tor",
            "Becoming careless with OPSEC over time",
            "A type of virus",
            "Slow internet"
        ],
        "answer_index": 1,
        "explanation": (
            "Over time, people get sloppy and make dangerous OPSEC mistakes."
        )
    },
    {
        "id": 29,
        "question": "Why clear Tor cookies between sessions?",
        "options": [
            "It speeds up Tor",
            "Cookies can track you across sessions",
            "It's required",
            "They take up space"
        ],
        "answer_index": 1,
        "explanation": (
            "Persistent cookies can link multiple Tor sessions together."
        )
    },
    {
        "id": 30,
        "question": "What is a 'warrant canary'?",
        "options": [
            "A bird warrant",
            "A statement that a service has not received secret subpoenas",
            "A market search warrant",
            "A crypto transaction"
        ],
        "answer_index": 1,
        "explanation": (
            "If the canary disappears, the service may have received a gag order."
        )
    },
    {
        "id": 31,
        "question": "Why disable JavaScript in Tor Browser?",
        "options": [
            "It slows pages",
            "JavaScript exploits can reveal your IP or fingerprint you",
            "Tor doesn't support JS",
            "JS uses bandwidth"
        ],
        "answer_index": 1,
        "explanation": (
            "JS is a major attack surface and can deanonymize users."
        )
    },
    {
        "id": 32,
        "question": "What is 'compartmentalization'?",
        "options": [
            "Organizing files",
            "Separating identities/activities into isolated environments",
            "Using multiple hard drives",
            "Cloud storage"
        ],
        "answer_index": 1,
        "explanation": (
            "Different activities should not share devices or accounts."
        )
    },
    {
        "id": 33,
        "question": "Why avoid using phones for darknet activity?",
        "options": [
            "Phones are slow",
            "Phones leak GPS, telemetry, and identity data",
            "Tor doesn’t work on phones",
            "Phone plans expensive"
        ],
        "answer_index": 1,
        "explanation": (
            "Phones constantly leak identifying data and are tied to your identity."
        )
    },
    {
        "id": 34,
        "question": "What does 'FE' mean?",
        "options": [
            "Fast Encryption",
            "Finalize Early — releasing payment before receiving product",
            "Fair Exchange",
            "Federal Evidence"
        ],
        "answer_index": 1,
        "explanation": (
            "FE removes buyer protection and is commonly exploited in scams."
        )
    },
    {
        "id": 35,
        "question": "Why use unique usernames for each market?",
        "options": [
            "Markets require it",
            "Reused usernames allow correlation of your accounts",
            "Unique names are easy",
            "Unique users get discounts"
        ],
        "answer_index": 1,
        "explanation": (
            "Reused usernames let attackers connect your market activity together."
        )
    },
    {
        "id": 36,
        "question": "What is 'steganography'?",
        "options": [
            "Study of ancient writing",
            "Hiding data inside images/audio",
            "An encryption algorithm",
            "Blockchain tech"
        ],
        "answer_index": 1,
        "explanation": (
            "Steganography hides the existence of a message inside another file."
        )
    },
    {
        "id": 37,
        "question": "Why verify vendor PGP keys through multiple sources?",
        "options": [
            "Required by markets",
            "Prevents man-in-the-middle key substitution attacks",
            "Multiple checks improve encryption",
            "Vendors ask for it"
        ],
        "answer_index": 1,
        "explanation": (
            "A fake key can trick you into sending readable messages to attackers."
        )
    },
    {
        "id": 38,
        "question": "What is a 'dead drop'?",
        "options": [
            "Failed transaction",
            "Hidden location for indirect item exchange",
            "Exit scam",
            "Blocked onion link"
        ],
        "answer_index": 1,
        "explanation": "Dead drops avoid direct contact between parties."
    },
    {
        "id": 39,
        "question": "Why avoid clicking shortened URLs on darknet forums?",
        "options": [
            "They don’t work",
            "They hide destinations and can track or phish you",
            "They cost money",
            "Forums ban them"
        ],
        "answer_index": 1,
        "explanation": (
            "Shortened URLs hide malware, phishing, and tracking systems."
        )
    },
    {
        "id": 40,
        "question": "What is '2FA'?",
        "options": [
            "Two-Factor Authentication",
            "Two Fast Actions",
            "Two Failed Attempts",
            "Two Fake Addresses"
        ],
        "answer_index": 0,
        "explanation": (
            "2FA adds a second verification step beyond passwords."
        )
    },
    {
        "id": 41,
        "question": "Why is it risky to use real personal info for shipping?",
        "options": [
            "It’s expensive",
            "Intercepted packages directly link to your identity",
            "Post office requires fake names",
            "Real names slow deliveries"
        ],
        "answer_index": 1,
        "explanation": (
            "If seized, using real identity creates clear evidence against you."
        )
    },
    {
        "id": 42,
        "question": "What is 'correlation analysis'?",
        "options": [
            "Comparing prices",
            "Linking separate data points to identify individuals",
            "Market review analysis",
            "Blockchain validation"
        ],
        "answer_index": 1,
        "explanation": (
            "Correlating timing, writing style, addresses, and more can deanonymize users."
        )
    },
    {
        "id": 43,
        "question": "Why avoid bragging about darknet activities?",
        "options": [
            "It's impolite",
            "Creates evidence, attracts law enforcement or scammers",
            "Nobody cares",
            "Markets ban bragging"
        ],
        "answer_index": 1,
        "explanation": (
            "Loose talk exposes information that can be used against you."
        )
    },
    {
        "id": 44,
        "question": "Why use encrypted messaging apps like Signal?",
        "options": [
            "They’re faster",
            "They provide end-to-end encryption",
            "They’re free",
            "Better emojis"
        ],
        "answer_index": 1,
        "explanation": (
            "E2E encryption prevents message content interception."
        )
    },
    {
        "id": 45,
        "question": "Why use full disk encryption?",
        "options": [
            "It speeds your computer",
            "Protects data if seized or stolen",
            "Tor requires it",
            "Saves space"
        ],
        "answer_index": 1,
        "explanation": (
            "Without FDE, seized devices reveal everything."
        )
    },
    {
        "id": 46,
        "question": "What is 'traffic analysis'?",
        "options": [
            "Website visitor stats",
            "Analyzing communication patterns to identify users",
            "Internet speed test",
            "Crypto price charts"
        ],
        "answer_index": 1,
        "explanation": (
            "Even encrypted content can be deanonymized via timing/volume patterns."
        )
    },
    {
        "id": 47,
        "question": "Why keep Tor Browser updated?",
        "options": [
            "New versions are faster",
            "Updates patch vulnerabilities that can deanonymize you",
            "Old versions expire",
            "Updates add features"
        ],
        "answer_index": 1,
        "explanation": (
            "Running outdated Tor exposes you to known exploits."
        )
    },
    {
        "id": 48,
        "question": "What is an 'exit scam'?",
        "options": [
            "Legitimate closure",
            "Market/vendor disappearing with funds",
            "Last-day discount",
            "Crypto withdrawal"
        ],
        "answer_index": 1,
        "explanation": "Exit scams steal all escrowed funds."
    },
    {
        "id": 49,
        "question": "Why use different wallets for different purposes?",
        "options": [
            "Wallet limits",
            "Prevents linking all transactions together",
            "More wallets earn interest",
            "Exchanges require it"
        ],
        "answer_index": 1,
        "explanation": (
            "Different wallets compartmentalize risk and prevent chain-analysis correlation."
        )
    },
    {
        "id": 50,
        "question": "What is the purpose of using a 'burner' email?",
        "options": [
            "Extra storage",
            "Disposable anonymous email not linked to your identity",
            "Faster sending",
            "Avoid spam filters"
        ],
        "answer_index": 1,
        "explanation": (
            "Burner emails prevent linking accounts or activity to your real identity."
        )
    }
]

# ============================================================
# STATE MANAGEMENT
# ============================================================

def load_state():
    """Load or initialize state.json."""
    if not os.path.exists(STATE_FILE):
        return {"last_question_index": None}

    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"last_question_index": None}


def save_state(state):
    """Save updated question state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_next_question_index(last_index):
    """Return next question index, wrapping around."""
    if last_index is None:
        return 0
    return (last_index + 1) % len(QUESTIONS)


# ============================================================
# REDDIT CONNECTION
# ============================================================

def get_reddit_instance():
    """Create authenticated Reddit client (PRAW)."""
    try:
        return praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "darknet_questions_bot")
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Reddit client: {e}")


# ============================================================
# POST BUILDING
# ============================================================

def build_post_title(current_question_index):
    q = QUESTIONS[current_question_index]
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"Darknet Question of the Day #{q['id']} ({today})"


def build_post_body(state, current_question_index):
    q = QUESTIONS[current_question_index]
    body = []

    # Yesterday’s answer
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
        "_This community does **not** encourage or promote illegal activity. "
        "All discussion is for educational and harm-reduction purposes only._\n\n"
    )

    # Today's question
    body.append(
        f"**Today's Darknet / OPSEC Question:**\n\n"
        f"{q['question']}\n\n"
        "Vote in the poll below — the correct answer will appear in tomorrow's post.\n"
    )

    return "".join(body)


# ============================================================
# MAIN LOGIC
# ============================================================

def post_daily_question():
    """Post the next question to Reddit as a poll."""

    # Load previous state
    state = load_state()
    last_index = state.get("last_question_index")

    # Determine next question
    current_index = get_next_question_index(last_index)
    question = QUESTIONS[current_index]

    print(f"Selected Question #{question['id']}")

    # Reddit client
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    # Build post
    title = build_post_title(current_index)
    body = build_post_body(state, current_index)

    print(f"Posting to r/{SUBREDDIT_NAME}...")

    # Create poll
    submission = subreddit.submit_poll(
        title=title,
        selftext=body,
        options=question["options"],
        duration=POLL_DURATION_DAYS
    )

    print("Posted:", submission.id)

    # Update state.json for tomorrow
    state["last_question_index"] = current_index
    save_state(state)

    print("State updated.")


# ============================================================
# ENTRY POINT (for GitHub Actions)
# ============================================================

if __name__ == "__main__":
    try:
        print("=== Starting Darknet Daily Bot ===")
        post_daily_question()
        print("=== Completed successfully ===")
    except Exception as e:
        print("ERROR:", repr(e))
        raise
