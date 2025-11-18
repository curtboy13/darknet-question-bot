import os
import json
import time
from datetime import datetime
import praw

# ---------- CONFIG ----------

STATE_FILE = "state.json"
SUBREDDIT_NAME = os.getenv("SUBREDDIT_NAME", "darknet_questions")

# Duration of poll in days (1 = 24 hours)
POLL_DURATION_DAYS = 1

# Question bank: add as many as you want.
# answer_index = index of the correct option in "options" list.
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
            "Using a reputable encrypted password manager with a strong, unique master "
            "password greatly reduces the risk of credential theft, compared to storing "
            "logins in plaintext or in your browser."
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
            "Using Tor Browser from a hardened, compartmentalized environment with good "
            "OPSEC reduces cross-contamination with your real identity and lowers risk."
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
            "PGP is primarily used to encrypt sensitive communications and to verify "
            "that messages or onion links were signed by the claimed party."
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
            "Reusing the same handle makes it easy to correlate darknet activity with "
            "clearnet forums, social media, or past posts through OSINT and search engines."
        )
    },
    {
        "id": 5,
        "question": "Which is generally the safer way to handle BTC for darknet use?",
        "options": [
            "Sending directly from KYC exchange to market deposit address",
            "Sending from KYC exchange to a self-custody wallet, then through a privacy-focused workflow before markets",
            "Keeping all coins on the exchange at all times",
            "Emailing your private key to yourself for backup"
        ],
        "answer_index": 1,
        "explanation": (
            "Directly linking a KYC exchange to a market is bad OPSEC. A self-custody "
            "wallet and privacy-focused steps reduce direct linkage between KYC data and markets."
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
            "Using your real email directly ties your darknet activity to your real identity, "
            "which can be discovered through data breaches, subpoenas, or OSINT techniques."
        )
    },
    {
        "id": 7,
        "question": "Why should you avoid taking screenshots of market pages?",
        "options": [
            "Screenshots don't work in Tor Browser",
            "Metadata can reveal device info, and accidental cloud sync can expose activity",
            "Markets automatically ban users who take screenshots",
            "It slows down your connection"
        ],
        "answer_index": 1,
        "explanation": (
            "Screenshot metadata can contain device fingerprints, timestamps, and system info. "
            "Auto-sync to cloud services can inadvertently expose your darknet activity."
        )
    },
    {
        "id": 8,
        "question": "What is 'fingerprinting' in the context of browser privacy?",
        "options": [
            "Using biometric login",
            "Tracking users by their unique browser configuration and behavior patterns",
            "A type of malware",
            "Encrypting your browsing history"
        ],
        "answer_index": 1,
        "explanation": (
            "Browser fingerprinting tracks unique combinations of your browser settings, fonts, "
            "screen size, plugins, and other attributes to identify you across sessions."
        )
    },
    {
        "id": 9,
        "question": "Why is it recommended to use the Tor Browser default settings?",
        "options": [
            "Custom settings make it faster",
            "Changing settings can make your browser more unique and easier to fingerprint",
            "Default settings are required by Tor network rules",
            "Custom settings void your warranty"
        ],
        "answer_index": 1,
        "explanation": (
            "Modifying Tor Browser settings creates a unique fingerprint. Using default settings "
            "makes you look like millions of other Tor users, providing anonymity through uniformity."
        )
    },
    {
        "id": 10,
        "question": "What does 'doxing' mean?",
        "options": [
            "Installing security software",
            "Publicly revealing someone's private personal information",
            "Creating fake documents",
            "Encrypting your data"
        ],
        "answer_index": 1,
        "explanation": (
            "Doxing is the act of researching and publishing private or identifying information "
            "about an individual online, often used as a form of harassment or intimidation."
        )
    },
    {
        "id": 11,
        "question": "Why should you avoid logging into personal accounts while using Tor?",
        "options": [
            "Personal accounts don't work with Tor",
            "It defeats anonymity by linking your real identity to your Tor session",
            "Tor is too slow for personal accounts",
            "It's against Tor's terms of service"
        ],
        "answer_index": 1,
        "explanation": (
            "Logging into accounts tied to your real identity while on Tor directly connects "
            "that session to you, negating the anonymity Tor provides."
        )
    },
    {
        "id": 12,
        "question": "What is the purpose of using Tails OS for darknet activities?",
        "options": [
            "It's faster than regular operating systems",
            "It's a privacy-focused, amnesic OS that leaves no trace on your computer",
            "It's required by all darknet markets",
            "It automatically mines cryptocurrency"
        ],
        "answer_index": 1,
        "explanation": (
            "Tails is designed to leave no trace of your activity. It runs from a USB stick, "
            "routes all traffic through Tor, and forgets everything when shut down."
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
        "explanation": (
            "OPSEC stands for Operational Security - the practice of protecting information "
            "that could be used to harm you if discovered by adversaries."
        )
    },
    {
        "id": 14,
        "question": "Why should you never share screenshots of your market transactions?",
        "options": [
            "They take up too much space",
            "They can contain identifying metadata and transaction details that link to you",
            "Markets prohibit sharing screenshots",
            "Screenshots don't capture onion links properly"
        ],
        "answer_index": 1,
        "explanation": (
            "Screenshots can reveal transaction IDs, wallet addresses, timestamps, and metadata "
            "that can be used to identify you or trace your activities."
        )
    },
    {
        "id": 15,
        "question": "What is the safest way to verify a market's onion link?",
        "options": [
            "Google search for the market name",
            "Use trusted community sources and verify PGP signatures",
            "Click random links from forum posts",
            "Ask strangers in Reddit DMs"
        ],
        "answer_index": 1,
        "explanation": (
            "Always verify onion links through trusted sources with PGP signatures. "
            "Phishing sites are common and can steal your credentials and funds."
        )
    },
    {
        "id": 16,
        "question": "Why is it dangerous to use the same password across multiple markets?",
        "options": [
            "Markets share password databases",
            "If one market is compromised, all your accounts are at risk",
            "It slows down login times",
            "Markets require unique passwords by law"
        ],
        "answer_index": 1,
        "explanation": (
            "When a market gets compromised or exit scams, attackers will try those credentials "
            "on other markets. Unique passwords limit damage to a single account."
        )
    },
    {
        "id": 17,
        "question": "What does 'KYC' stand for in cryptocurrency?",
        "options": [
            "Keep Your Coins",
            "Know Your Customer",
            "Key Your Crypto",
            "Kill Your Cache"
        ],
        "answer_index": 1,
        "explanation": (
            "KYC (Know Your Customer) refers to identity verification requirements imposed by "
            "regulated exchanges, which ties your real identity to your cryptocurrency transactions."
        )
    },
    {
        "id": 18,
        "question": "Why should you avoid using public WiFi for darknet activities?",
        "options": [
            "It's slower than home WiFi",
            "Network owners can monitor traffic, even if encrypted, and link activity to you",
            "Public WiFi blocks Tor access",
            "It costs money to use"
        ],
        "answer_index": 1,
        "explanation": (
            "Even with Tor, using public WiFi can create logs linking your physical presence "
            "to that location and time. Compromised networks can also attempt to de-anonymize you."
        )
    },
    {
        "id": 19,
        "question": "What is 'multisig escrow' in darknet markets?",
        "options": [
            "Multiple shipping addresses",
            "A system requiring multiple parties to approve a transaction release",
            "Multiple payment methods",
            "Multiple vendor accounts"
        ],
        "answer_index": 1,
        "explanation": (
            "Multisig escrow requires signatures from multiple parties (buyer, vendor, and arbitrator) "
            "to release funds, preventing markets from exit scamming with escrowed funds."
        )
    },
    {
        "id": 20,
        "question": "Why should you never reuse Bitcoin addresses?",
        "options": [
            "Addresses expire after one use",
            "Reusing addresses reduces privacy by linking all transactions together",
            "Bitcoin charges extra for address reuse",
            "Old addresses are slower to process"
        ],
        "answer_index": 1,
        "explanation": (
            "Address reuse allows anyone to see all transactions associated with that address, "
            "making it easier to track your activity and estimate your holdings."
        )
    },
    {
        "id": 21,
        "question": "What is the purpose of using a VPN before connecting to Tor?",
        "options": [
            "It makes Tor faster",
            "It hides the fact that you're using Tor from your ISP",
            "It's required by Tor to function",
            "It provides better encryption than Tor alone"
        ],
        "answer_index": 1,
        "explanation": (
            "A VPN before Tor (VPN -> Tor) hides Tor usage from your ISP, which can be useful "
            "in locations where Tor is suspicious or blocked. However, it adds a trusted party."
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
        "explanation": (
            "OSINT is Open Source Intelligence - information gathering from publicly available sources "
            "like social media, forums, and websites to build profiles or track individuals."
        )
    },
    {
        "id": 23,
        "question": "Why is it important to verify PGP signatures on market communications?",
        "options": [
            "It makes messages look professional",
            "It confirms the message actually came from who it claims to be from",
            "It's required by law",
            "It encrypts the message"
        ],
        "answer_index": 1,
        "explanation": (
            "PGP signatures prove authenticity. Verifying signatures prevents phishing attacks "
            "where someone impersonates a vendor or market admin to steal information or funds."
        )
    },
    {
        "id": 24,
        "question": "What is 'tumbling' or 'mixing' cryptocurrency?",
        "options": [
            "Converting to a different cryptocurrency",
            "Breaking the link between source and destination addresses by mixing with other users' coins",
            "Storing coins in multiple wallets",
            "Mining new coins"
        ],
        "answer_index": 1,
        "explanation": (
            "Tumblers/mixers pool coins from many users and redistribute them, making it harder "
            "to trace the original source of any particular coin."
        )
    },
    {
        "id": 25,
        "question": "Why should you avoid discussing specific orders or vendors in public forums?",
        "options": [
            "It's against forum rules",
            "It can help law enforcement connect the dots and identify patterns",
            "Vendors don't like publicity",
            "It slows down the forum"
        ],
        "answer_index": 1,
        "explanation": (
            "Public discussions of orders can create a trail of evidence. Combined with other data, "
            "it can help identify buyers, vendors, and shipping patterns."
        )
    },
    {
        "id": 26,
        "question": "What is the main advantage of Monero over Bitcoin for privacy?",
        "options": [
            "Monero is faster",
            "Monero has privacy features built-in by default, while Bitcoin is pseudonymous",
            "Monero is worth more",
            "Monero is easier to buy"
        ],
        "answer_index": 1,
        "explanation": (
            "Monero uses ring signatures, stealth addresses, and confidential transactions to hide "
            "sender, receiver, and amount - making it private by default unlike Bitcoin's transparent blockchain."
        )
    },
    {
        "id": 27,
        "question": "Why is it risky to keep funds in a market wallet?",
        "options": [
            "Market wallets charge high fees",
            "Markets can exit scam, get seized, or hacked - taking all deposited funds",
            "You can't withdraw from market wallets",
            "Market wallets are slower than personal wallets"
        ],
        "answer_index": 1,
        "explanation": (
            "Markets control the private keys to market wallets. Exit scams, law enforcement seizures, "
            "and hacks are common, resulting in total loss of any funds left on the market."
        )
    },
    {
        "id": 28,
        "question": "What is 'OpSec fatigue'?",
        "options": [
            "Tired feeling after long Tor sessions",
            "Becoming careless with security practices over time due to complacency",
            "A type of computer virus",
            "Slow internet from using Tor"
        ],
        "answer_index": 1,
        "explanation": (
            "OpSec fatigue occurs when people gradually become less careful with security practices "
            "over time, making mistakes that can compromise their anonymity."
        )
    },
    {
        "id": 29,
        "question": "Why should you clear Tor Browser cookies between sessions?",
        "options": [
            "It makes Tor faster",
            "Cookies can be used to track you across sessions",
            "It's required to connect to new sites",
            "Cookies take up too much space"
        ],
        "answer_index": 1,
        "explanation": (
            "Persistent cookies can link multiple Tor sessions together, potentially de-anonymizing "
            "you. Tor Browser can be configured to clear cookies automatically when closed."
        )
    },
    {
        "id": 30,
        "question": "What is a 'canary warrant'?",
        "options": [
            "A type of bird-watching warrant",
            "A regularly updated statement that a service hasn't received a secret subpoena/gag order",
            "A special search warrant for markets",
            "A cryptocurrency transaction"
        ],
        "answer_index": 1,
        "explanation": (
            "A warrant canary is a published statement that a service has not received secret legal "
            "requests. If it stops being updated, it may indicate they've been served with a gag order."
        )
    },
    {
        "id": 31,
        "question": "Why is JavaScript often recommended to be disabled in Tor Browser?",
        "options": [
            "JavaScript slows down page loading",
            "JavaScript can be exploited to reveal your real IP or fingerprint your browser",
            "Tor doesn't support JavaScript",
            "JavaScript uses too much bandwidth"
        ],
        "answer_index": 1,
        "explanation": (
            "JavaScript can be exploited through browser vulnerabilities to de-anonymize users, "
            "execute malicious code, or fingerprint browsers through timing attacks and system queries."
        )
    },
    {
        "id": 32,
        "question": "What is 'compartmentalization' in OPSEC?",
        "options": [
            "Organizing your computer files into folders",
            "Separating different activities/identities into isolated environments",
            "Using multiple hard drives",
            "Storing data in the cloud"
        ],
        "answer_index": 1,
        "explanation": (
            "Compartmentalization means keeping different activities completely separate - different "
            "devices, OS instances, or VMs - to prevent cross-contamination if one is compromised."
        )
    },
    {
        "id": 33,
        "question": "Why should you avoid using your phone for darknet activities?",
        "options": [
            "Phones are too slow",
            "Phones have GPS, constant tracking, and are harder to secure than dedicated systems",
            "Tor doesn't work on phones",
            "Phone plans are too expensive"
        ],
        "answer_index": 1,
        "explanation": (
            "Smartphones constantly leak location data, have difficult-to-audit security, carrier tracking, "
            "and are tied to your identity through purchase, SIM cards, and app accounts."
        )
    },
    {
        "id": 34,
        "question": "What does 'FE' mean in darknet market context?",
        "options": [
            "Fast Encryption",
            "Finalize Early - releasing payment before receiving the product",
            "Fair Exchange",
            "Federal Evidence"
        ],
        "answer_index": 1,
        "explanation": (
            "FE (Finalize Early) means releasing escrowed payment to a vendor before receiving your order. "
            "This removes buyer protection and is commonly used in scams."
        )
    },
    {
        "id": 35,
        "question": "Why is it important to use unique usernames for each market?",
        "options": [
            "Markets require unique usernames",
            "Reusing usernames allows correlation of accounts and order history across markets",
            "It's easier to remember unique usernames",
            "Unique usernames get better vendor discounts"
        ],
        "answer_index": 1,
        "explanation": (
            "Using the same username across markets allows anyone to link your accounts together, "
            "potentially revealing patterns, order history, and vendor relationships."
        )
    },
    {
        "id": 36,
        "question": "What is 'steganography'?",
        "options": [
            "The study of ancient writing",
            "Hiding messages or data within other files like images or audio",
            "A type of encryption algorithm",
            "Blockchain technology"
        ],
        "answer_index": 1,
        "explanation": (
            "Steganography conceals the existence of a message by hiding it in plain sight within "
            "innocent-looking files, as opposed to encryption which scrambles the message."
        )
    },
    {
        "id": 37,
        "question": "Why should you verify vendor PGP keys through multiple sources?",
        "options": [
            "It's required by markets",
            "Prevents man-in-the-middle attacks where someone substitutes a fake key",
            "Multiple verifications make keys work better",
            "Vendors require multiple verifications"
        ],
        "answer_index": 1,
        "explanation": (
            "Verifying PGP keys from multiple independent sources prevents attackers from providing "
            "you with a fake key that they control, allowing them to intercept encrypted communications."
        )
    },
    {
        "id": 38,
        "question": "What is a 'dead drop'?",
        "options": [
            "A failed cryptocurrency transaction",
            "A method of exchanging items by leaving them in a hidden location",
            "A type of exit scam",
            "A blocked onion link"
        ],
        "answer_index": 1,
        "explanation": (
            "A dead drop is a secret location where items are left for pickup by another party, "
            "avoiding direct contact between buyer and seller."
        )
    },
    {
        "id": 39,
        "question": "Why should you avoid clicking shortened URLs on darknet forums?",
        "options": [
            "Shortened URLs don't work with Tor",
            "They can hide phishing links or malicious sites and enable tracking",
            "They cost money to use",
            "Forums prohibit shortened URLs"
        ],
        "answer_index": 1,
        "explanation": (
            "URL shorteners hide the true destination, can track who clicks them, and are commonly "
            "used for phishing attacks to steal credentials or install malware."
        )
    },
    {
        "id": 40,
        "question": "What is '2FA' and why is it important?",
        "options": [
            "Two-Factor Authentication - requiring two forms of verification to log in",
            "Two Fast Actions - a quick login method",
            "Two Failed Attempts - account lockout",
            "Two Fake Addresses - using decoy shipping info"
        ],
        "answer_index": 0,
        "explanation": (
            "2FA requires a second verification method (like a code from an app) in addition to your password, "
            "greatly reducing the risk of account compromise even if your password is stolen."
        )
    },
    {
        "id": 41,
        "question": "Why is it risky to use real personal information for shipping?",
        "options": [
            "Packages are more expensive with real names",
            "It directly links seized packages to your real identity",
            "Post office requires fake names",
            "Real names cause delivery delays"
        ],
        "answer_index": 1,
        "explanation": (
            "If a package is intercepted, using your real name and address creates direct evidence "
            "linking you to the illegal shipment, making prosecution much easier."
        )
    },
    {
        "id": 42,
        "question": "What is 'correlation analysis'?",
        "options": [
            "Comparing product prices",
            "Linking separate pieces of data to identify patterns or individuals",
            "Market review analysis",
            "Blockchain validation"
        ],
        "answer_index": 1,
        "explanation": (
            "Correlation analysis involves combining multiple data points (timing, writing style, "
            "transaction patterns, etc.) to identify individuals despite attempts at anonymity."
        )
    },
    {
        "id": 43,
        "question": "Why should you avoid bragging about darknet activities?",
        "options": [
            "It's impolite",
            "Loose talk creates evidence and makes you a target for law enforcement or scammers",
            "Nobody cares",
            "Markets ban people who brag"
        ],
        "answer_index": 1,
        "explanation": (
            "Discussing illegal activities creates evidence, attracts unwanted attention from law enforcement, "
            "and makes you a target for extortion, hacking, or robbery."
        )
    },
    {
        "id": 44,
        "question": "What is the purpose of using encrypted messaging apps like Signal?",
        "options": [
            "They're faster than regular SMS",
            "They provide end-to-end encryption protecting message content from interception",
            "They're free to use",
            "They have better emojis"
        ],
        "answer_index": 1,
        "explanation": (
            "End-to-end encryption ensures only you and your recipient can read messages - not even "
            "the service provider. However, metadata like who you talk to and when is still collected."
        )
    },
    {
        "id": 45,
        "question": "Why should you use full disk encryption?",
        "options": [
            "It makes your computer faster",
            "It protects all data if your device is seized or stolen",
            "It's required by Tor",
            "It uses less storage space"
        ],
        "answer_index": 1,
        "explanation": (
            "Full disk encryption ensures that if your device is seized, stolen, or accessed while powered off, "
            "all data remains encrypted and inaccessible without the correct password."
        )
    },
    {
        "id": 46,
        "question": "What is 'traffic analysis'?",
        "options": [
            "Analyzing website visitor statistics",
            "Monitoring communication patterns to identify users even without reading message content",
            "Checking internet speed",
            "Analyzing cryptocurrency prices"
        ],
        "answer_index": 1,
        "explanation": (
            "Traffic analysis examines patterns like timing, volume, and connections to identify users "
            "or relationships even when the actual content is encrypted."
        )
    },
    {
        "id": 47,
        "question": "Why is it important to keep Tor Browser updated?",
        "options": [
            "New versions are faster",
            "Updates patch security vulnerabilities that could de-anonymize you",
            "Old versions expire",
            "Updates add new features only"
        ],
        "answer_index": 1,
        "explanation": (
            "Security updates fix vulnerabilities that attackers actively exploit to de-anonymize users. "
            "Running outdated software leaves you exposed to known attacks."
        )
    },
    {
        "id": 48,
        "question": "What is an 'exit scam'?",
        "options": [
            "A legitimate market closure",
            "When a market or vendor disappears with customers' escrowed funds or unshipped orders",
            "A special discount before leaving",
            "A cryptocurrency withdrawal"
        ],
        "answer_index": 1,
        "explanation": (
            "An exit scam occurs when a market or vendor suddenly closes and steals all escrowed funds "
            "and recent deposits, often after building trust over time."
        )
    },
    {
        "id": 49,
        "question": "Why should you use different cryptocurrency wallets for different purposes?",
        "options": [
            "Wallets have transaction limits",
            "Compartmentalization prevents linking all transactions together if one wallet is compromised",
            "Multiple wallets earn more interest",
            "It's required by exchanges"
        ],
        "answer_index": 1,
        "explanation": (
            "Using separate wallets for different activities prevents blockchain analysis from linking "
            "all your transactions together, maintaining better privacy and security."
        )
    },
    {
        "id": 50,
        "question": "What is the main purpose of using a 'burner' email?",
        "options": [
            "To get more storage space",
            "To have a disposable, anonymous email not linked to your real identity",
            "To send emails faster",
            "To avoid spam filters"
        ],
        "answer_index": 1,
        "explanation": (
            "Burner emails are temporary, anonymous addresses created specifically for one purpose "
            "and then discarded, preventing your activity from being linked to your real identity."
        )
    }
]

# ---------- STATE MANAGEMENT ----------

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def get_next_question_index(last_index):
    if last_index is None:
        return 0
    return (last_index + 1) % len(QUESTIONS)

# ---------- REDDIT SETUP ----------

def get_reddit_instance():
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "darknet_questions_bot")
    )
    return reddit

# ---------- POST BUILDER ----------

def build_post_body(state, current_question_index):
    q = QUESTIONS[current_question_index]

    body_parts = []

    # 1. Yesterday's answer (if any)
    last_index = state.get("last_question_index")
    if last_index is not None and 0 <= last_index < len(QUESTIONS):
        prev_q = QUESTIONS[last_index]
        correct_option = prev_q["options"][prev_q["answer_index"]]
        explanation = prev_q["explanation"]

        # Use spoiler tags so people have to click to reveal
        # >!spoiler text!<
        body_parts.append(
            "**Yesterday's answer:**\n"
            f">!{correct_option}!<\n\n"
            f"{explanation}\n\n"
            "---\n"
        )

    # 2. Disclaimer / reminder
    body_parts.append(
        "_This community does **not** encourage or promote illegal activity. "
        "All discussion is for educational and harm-reduction purposes only._\n\n"
    )

    # 3. Today's question
    body_parts.append(
        f"**Today's Darknet / OPSEC Question:**\n\n"
        f"{q['question']}\n\n"
        "Vote in the poll below. The correct answer and explanation will be "
        "posted with tomorrow's question.\n"
    )

    return "".join(body_parts)

def build_post_title(current_question_index):
    q = QUESTIONS[current_question_index]
    number = QUESTIONS[current_question_index]["id"]
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"Darknet Question of the Day #{number} ({today})"

# ---------- CORE LOGIC ----------

def post_daily_question():
    state = load_state()
    last_index = state.get("last_question_index")

    current_index = get_next_question_index(last_index)
    q = QUESTIONS[current_index]

    reddit = get_reddit_instance()
    subreddit_name = SUBREDDIT_NAME
    subreddit = reddit.subreddit(subreddit_name)

    title = build_post_title(current_index)
    body = build_post_body(state, current_index)

    print(f"Posting to r/{subreddit_name}: {title}")

    submission = subreddit.submit_poll(
        title=title,
        selftext=body,
        options=q["options"],
        duration=POLL_DURATION_DAYS
    )

    print(f"Posted: {submission.id}")

    # Update state for tomorrow
    state["last_question_index"] = current_index
    save_state(state)

# ---------- MAIN ----------

if __name__ == "__main__":
    print("Starting Reddit bot - posting daily question...")
    post_daily_question()
    print("Done! Bot will run again on next scheduled trigger.")
